from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
import torch
from PIL import Image
from io import BytesIO
import json

def parse_result(result):
    message = ""
    data = json.loads(result)

    message += f"I think it's a {data['commonName']} ({data['rank']}: {data['scientificName']})! (confidence: {data['confidence']}\n"

    message += "Other possibilities:\n"
    for i, possibility in enumerate(data['otherPossibilities']):
        message += f"||{i}. {possibility['commonName']} ({possibility['rank']}: {possibility['scientificName']}) (confidence: {possibility['confidence']})||\n"

    return message

def analyze_image(image_bytes):
    model_name = "Qwen/Qwen2.5-VL-7B-Instruct"

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.float16,
    )

    processor = AutoProcessor.from_pretrained(model_name)

    # load image from memory
    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": """
                        You are a nature identification API.

                        You will be given an image and asked to identify what species is in it.

                        If there are multiple species in it, identify the species closest to the center of the image.
                        If there are no species in it, you should leave all string fields blank, confidence at 0.0, and otherPossibilities empty.

                        Always respond with valid JSON in the form:
                        {
                            "commonName": "",
                            "scientificName": "",
                            "rank": "",
                            "confidence": 0.0,
                            "otherPossibilities": [
                                {
                                    "commonName": "",
                                    "scientificName": "",
                                    "rank": "",
                                    "confidence": 0.0
                                },
                            ]
                        }

                        If you are not confident in the exact species, you should roll up to genus. Or even further, if necessary. This should mostly be used for unidentifiable species, such as mites or nematodes.
                        Always attempt to identify the species unless it's virtually impossible.
                        The scientific name should either be the binomial species name or the taxonomic rank's name, if it is a higher rank than species.

                        Your confidence should indicate how good of a match the image is to your guess, from 0 to 100.
                        otherPossibilities should include 0-3 other guesses, depending on confidence of the original guess.

                        Never include explanations outside the JSON.
                    """
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image
                },
                {
                    "type": "text",
                    "text": "Identify this organism",
                }
            ]
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompts=True,
        tokenize=True,
        return_tensors="pt"
    ).to(model.device)

    output = model.generate(
        **inputs,
        max_new_tokens = 50
    )

    result = processor.batch_decode(
        output,
        skip_special_tokens=True
    )

    return parse_result(result)
