import torch # make sure to have a cuda version of torch
import open_clip
from PIL import Image
import json
from tqdm import tqdm
import time
from io import BytesIO
from config import (
    CACHE,
    PROCESSED,
    PROMPT_TEMPLATES,
    article
)


# Make sure cache directory exists
CACHE.mkdir(exist_ok=True)

def load_model():
    print("Setting up model...")
    # Set up BioCLIP model
    model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip") # ignore training pipeline, get model and image preprocessor
    tokenizer = open_clip.get_tokenizer("hf-hub:imageomics/bioclip") # open the tokenizer to convert species data from text to tokens
    model.eval() # put the model into evaluation mode -- not training

    print("Done!")

    return model, preprocess, tokenizer


def get_text_features(rank: str, model, tokenizer, device, taxa):
    TAXA_BATCH = 1024 # how many taxa to generate prompts for at once
    PROMPT_BATCH = 1024 # how many prompts to convert to embeddings at once

    embeddings_file = CACHE / f"{rank}.pt" # where to load from/save to

    # check if embeddings are cached
    if embeddings_file.exists(): # load if so
        print("Loading cached embeddings...")
        text_features = torch.load(embeddings_file)
        print("Loaded!")
        return text_features["embeddings"]

    # generate embeddings if not cached
    text_features = [] # to store prompt embeddings for each taxon

    print("Generating text features...")

    with torch.inference_mode(): # open in inference mode for fastest results
        # loop through the whole taxa file, incrementing by TAXA_BATCH
        for chunk_start in tqdm(range(0, len(taxa), TAXA_BATCH), desc=f"{rank}"):
            chunk_start_time = time.perf_counter()
            chunk = taxa[chunk_start:chunk_start + TAXA_BATCH] # slice taxa data to get chunk

            # build prompts for every species in this chunk
            all_prompts = [] # store all prompts for later conversion
            prompt_counts = [] # store how many prompts each taxon has (can be less if no common name)
            # loop through the taxa
            prompt_start = time.perf_counter()
            for taxon in chunk:
                # build prompts
                prompts = []

                # use common prompts for both scientificName and commonName for species
                if (rank == "species"):
                    for func in PROMPT_TEMPLATES["common_and_species"]:
                        # one of each common prompt using scientificName
                        prompts.append(func(taxon["scientificName"]))
                        if taxon["commonName"]:
                            # one of each common prompt using commonName, if applicable
                            prompts.append(func(taxon["commonName"]))
                else:
                    for func in PROMPT_TEMPLATES["scientific_NON_SPECIES"]:
                        # one of each scientific prompt using scientificName
                        prompts.append(func(rank, taxon["scientificName"]))
                    # one of each common prompt using commonName, if applicable
                    if taxon["commonName"]:
                        for func in PROMPT_TEMPLATES["common_and_species"]:
                            prompts.append(func(taxon["commonName"]))

                # stores prompts and prompt counts
                prompt_counts.append(len(prompts))
                all_prompts.extend(prompts)

            prompt_time = time.perf_counter() - prompt_start

            # convert prompts to embeddings
            prompt_embeddings = []
            encode_start = time.perf_counter()
            # loop through all prompts, incrementing by PROMPT_BATCH
            for i in tqdm(range(0, len(all_prompts), PROMPT_BATCH), desc="Encoding", leave=False):
                batch = all_prompts[i: i + PROMPT_BATCH] # batch is made from a slice of the prompts array

                tokens = tokenizer(batch).to(device) # convert batches to tokens on GPU

                embeddings = model.encode_text(tokens) # convert the tokens to embeddings

                # normalize embeddings across their length; means comparisons will use direction, not magnitude -- also keep dimensions is needed for division
                embeddings /= embeddings.norm(dim=-1, keepdim=True) # keepdim=True indicates to match every element in that row with that number, allowing them to be divided element-wise

                # append the embeddings to an array
                prompt_embeddings.append(embeddings)

                # free up memory
                del tokens
                del embeddings

            torch.cuda.synchronize()
            encode_time = time.perf_counter() - encode_start

            # join tensors end to end as new rows to allow for slicing
            prompt_embeddings = torch.cat(prompt_embeddings, dim=0)

            average_start = time.perf_counter()
            # average embeddings per taxon using prompt_counts
            start = 0

            for count in prompt_counts:
                # the start to start+count is one taxon
                emb = prompt_embeddings[start:start+count]

                # average each taxon's prompts across the row and then normalize the result
                emb = emb.mean(dim=0)
                emb /= emb.norm()

                text_features.append(emb.cpu()) # move the embeddings back to RAM to free up GPU memory (also CPU tensors are easier to save!)

                start += count

            # free up memory
            del prompt_embeddings

            average_time = time.perf_counter() - average_start
            chunk_time = time.perf_counter() - chunk_start_time

            print(
                f"Chunk: {chunk_time:.2f}s | "
                f"Prompts: {prompt_time:.2f}s | "
                f"Encode: {encode_time:.2f}s | "
                f"Average: {average_time:.2f}s | "
                f"{len(chunk)} taxa | "
                f"{len(all_prompts)} prompts"
            )

    text_features = torch.stack(text_features) # join tensors together with a new dimension to represent the separation of taxa


    # Save to cache (generation is expensive!)
    print("Saving...")
    torch.save(
        {
            "embeddings": text_features,
            "taxa": taxa,
        }, embeddings_file)
    print("Saved!")

    return text_features


def get_image_features(image_bytes, model, preprocess, device):
    print("Preprocessing image...")

    # load image from memory
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    # load image
    image = preprocess( # adjust a PIL.Image object to fit what BioCLIP expects
        image # open the image as a PIL.Image object
    ).unsqueeze(0) # add a batch size dimension to the front of the tensor --
    # neural networks are designed to work with batches, so the model needs to be told how many images to expect

    print("Generating image embeddings...")

    # generate image embeddings
    with torch.no_grad():
        image_features = model.encode_image(image.to(device)) # convert image to embeddings on GPU
        image_features /= image_features.norm(dim=-1, keepdim=True) # normalize image for the same reason as earlier

    print("Done!")

    image_features = image_features.cpu() # send image features back to RAM to free up GPU memory (also CPU tensors are easier to save!)

    return image_features

def compare_features(image_features, text_features, device):
    # Send image features and text features to GPU to perform comparison
    image_features = image_features.to(device)
    text_features = text_features.to(device)

    print("Comparing embeddings...")

    # Compare image embeddings vs text embeddings with matrix multiplication (@ = torch.matmul())
    similarities = image_features @ text_features.T # inner dimensions must match for matmul, so text features must be transposed

    # Flatten similarities to its singular row (it only has one because it only processes one image)
    similarities = similarities[0]

    print("Done!")

    return similarities

def print_results(similarities, taxa):
    # Convert similarity scores into probabilities (match percentage? idrk)
    probs = (similarities * 100).softmax(dim=0)

    k=5
    # Get the top k probabilities
    top_k = torch.topk(probs, k=min(k, len(taxa)))

    possibilities = ""

    # build list of possibilities from top 5 guesses
    for prob, i in zip(top_k.values, top_k.indices):
        taxon = taxa[i.item()]
        if (taxon['commonName']):
            possibilities += f"{i}. {taxon['commonName']} ({taxon['scientificName']}): {prob.item() * 100:2f}%\n"
        else:
            possibilities += f"{i}. {taxon['scientificName']}: {prob.item() * 100:.2f}%\n"


    # build main conclusion from top choice
    message = ""
    best = top_k.indices[0].item()
    top_choice = taxa[best]
    if (top_choice['commonName']):
        message += f"I think it's {article(top_choice['commonName'])} ({top_choice['scientificName']})!"
    else:
        message += f"I think it's {article(top_choice['scientificName'])} specimen!"

    # return the message
    return f"{message}\n\n||{possibilities}||"



def analyze_image(image):
    # execution
    model, preprocess, tokenizer = load_model()

    # Point model towards GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    rank = "species"

    with open(PROCESSED / f"{rank}.json", "r", encoding="utf-8") as f:
        taxa = json.load(f)

    image_features = get_image_features(image, model, preprocess, device)
    text_features = get_text_features(rank, model, tokenizer, device, taxa)

    similarities = compare_features(image_features, text_features, device)

    return print_results(similarities, taxa)
