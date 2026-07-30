import torch # make sure to have a cuda version of torch
import open_clip
from PIL import Image
import json
from pathlib import Path
from config import CACHE, TAXA_EMBEDDINGS, PROCESSED_DATA

# Make sure cache directory exists
CACHE.mkdir(exist_ok=True)

# Set up BioCLIP model
model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip") # ignore training pipeline, get model and image preprocessor
tokenizer = open_clip.get_tokenizer("hf-hub:imageomics/bioclip") # open the tokenizer to convert species data from text to tokens
model.eval() # put the model into evaluation mode -- not training

# Point model towards GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# Load taxa
with open(PROCESSED_DATA, "r", encoding="utf-8") as f:
    taxa = json.load(f)

# Check if embeddings are saved
if Path.exists(TAXA_EMBEDDINGS):
    print("Loading cached taxa embeddings...")
    text_features = torch.load(TAXA_EMBEDDINGS)
else:
    # Create text prompts
    PROMPTS_PER_TAXA = len(taxa[0]["prompts"])

    all_prompts = [] # list of all prompts for all taxa

    for taxon in taxa:
        prompts = taxon["prompts"] # list of strings
        all_prompts.extend(prompts) # add each prompt to the list

    # Convert text prompts to tokens in batches
    prompt_features = []
    batch_size = 2048

    with torch.no_grad():
        for i in range(0, len(all_prompts), batch_size):
            print(f"Batch {i//batch_size + 1}/{(len(all_prompts)-1)//batch_size + 1}") # progress updates

            batch = all_prompts[i: i + batch_size] # batch is made from a slice of the text prompts array

            tokens = tokenizer(batch).to(device) # convert batch to tokens like normal on GPU
            prompt_embedding = model.encode_text(tokens)  # convert the tokens to embeddings
            prompt_embedding /= prompt_embedding.norm(dim=-1, keepdim=True) # normalize the embeddings according to their length -- makes sure comparisons will be about *direction*, not about size -- keep dimensions for division

            prompt_features.append(prompt_embedding.cpu()) # move the batch back to RAM

    all_prompt_features = torch.cat(prompt_features, dim=0) # Combine all embeddings

    # Average out prompts per taxa
    text_features = []

    for i in range(len(taxa)):
        start = i * PROMPTS_PER_TAXA
        end = start + PROMPTS_PER_TAXA

        taxa_embedding = all_prompt_features[start:end].mean(dim=0) # slice prompts to group them by species
        taxa_embedding /= taxa_embedding.norm() # no need for dim=-1 or keepdim=True because there's only one vector
        text_features.append(taxa_embedding)

    text_features = torch.stack(text_features) # take a list of tensors and make it into one big tensor with a new dimension, as opposed to no new dimension with torch.cat

    # Save text features to cache
    print("Saving...")
    torch.save(text_features, TAXA_EMBEDDINGS)
    print("Saved!")

# Load image
image = preprocess( # adjust a PIL.Image object to fit what BioCLIP expects
    Image.open("test_image.jpg") # open the image as a PIL.Image object
).unsqueeze(0) # add a batch size dimension to the front of the tensor -- neural networks are designed to work with batches, not single inputs

# Generate image embedding
with torch.no_grad():
    image_features = model.encode_image(image.to(device))
    image_features /= image_features.norm(dim=-1, keepdim=True)

image_features = image_features.cpu()

# Compare text embeddings vs image embeddings with matrix multiplication (@ = torch.matmul())
similarities = image_features @ text_features.T # inner dimensions must match for matrix multiplication

# Flatten similarities to its singular row (it only has one because it only processes one image)
similarities = similarities[0]

"""# debugging
print(len(animals))
print(text_features.shape)
print(similarities.shape)
print(similarities.argmax().item())
"""

# Print top k
top_k = torch.topk(similarities, k=7)

for score, i in zip(top_k.values, top_k.indices):
    taxon = taxa[i.item()] # ensure i (tensor) can be used as an index
    print(f"{taxon['common_name']}: {score.item():.2f}")

print(f"I think it's a {taxa[similarities.argmax().item()]['common_name']} ({taxa[similarities.argmax().item()]['scientific_name']})!")
