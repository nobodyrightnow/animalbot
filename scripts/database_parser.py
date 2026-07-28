# Parse the processed database to make it into a json format usable by the computer vision model

import pandas as pd
import csv
import json
from config import PROCESSED_NAMES, NAME_COLS, LANGUAGE, PROCESSED_TAXON, TAXON_COLS, KINGDOM, TAXON_RANKS, STATUS, PHYLUM, OMITTED_CLASS, OMITTED_ORDER, PROCESSED_DATA

print("Starting to read common names.")

# Read in all of the common names of animals
vernacular = pd.read_csv(
    PROCESSED_NAMES,
    sep="\t",
    quoting=csv.QUOTE_MINIMAL,
    on_bad_lines="skip",
    usecols=NAME_COLS
)

total_names = len(vernacular)
print(f"Read in {total_names} common names")

# Filter names
common_names = vernacular[
    (vernacular["dcterms:language"].isin(LANGUAGE))
]

new_num_names = len(vernacular)
print(f"Filtered out {total_names - new_num_names} of different languages. There are now {new_num_names} names")
total_names = new_num_names

# Remove extra names for species
common_names = common_names.drop_duplicates(subset="dwc:taxonID")

new_num_names = len(vernacular)
print(f"Dropped {total_names - new_num_names} duplicate names. There are now {new_num_names} names")
total_names = new_num_names

# Create new commonName col for lowercase (faster than doing it during the loop later)
common_names["commonName"] = common_names["dwc:vernacularName"].str.lower()

print(f"{total_names} common names have been stored!")
print("Starting to read other taxa data. This may take a while...")

# Read in all of the scientific names of animals
taxa = pd.read_csv(
    PROCESSED_TAXON,
    sep="\t",
    quoting=csv.QUOTE_MINIMAL,
    engine="python",
    on_bad_lines="skip",
    usecols=TAXON_COLS
)

total_taxa = len(taxa)
print(f"Read in {total_taxa} taxa")

# Filter taxa
taxa = taxa[
    # By kingdom
    (taxa["dwc:kingdom"].isin(KINGDOM)) &
    # By phylum
    (taxa["dwc:phylum"].isin(PHYLUM)) &
    # By class
    (~taxa["dwc:class"].isin(OMITTED_CLASS)) &
    # By order
    (~taxa["dwc:order"].isin(OMITTED_ORDER)) &
    # By rank
    (taxa["dwc:taxonRank"].isin(TAXON_RANKS)) &
    # By status
    (taxa["dwc:taxonomicStatus"].isin(STATUS))
]

new_num_taxa = len(taxa)
print(f"Filtered out {total_taxa - new_num_taxa} taxa. There are now {new_num_taxa} taxa")
total_taxa = new_num_taxa

# Create new scientificName col based on genericName and specificEpithet
taxa["scientificName"] = (
    taxa["dwc:genericName"].fillna("") + " " + taxa["dwc:specificEpithet"].fillna("")
).str.strip()

print("The rest of the data has been read!")
print("Starting to merge the data. This may take a while...")

# Merge common_names and animals based on common factor (taxonID)
taxa = taxa.merge(common_names, on="dwc:taxonID")

new_num_taxa = len(taxa)
print(f"The data has been merged successfully! {total_taxa - new_num_taxa} taxa were lost, likely because they had no common name")
total_taxa = new_num_taxa
print(f"Starting to write {total_taxa} taxa to the output file. This may take a while...")

# Write to json file
output = []

for taxon in taxa.itertuples(index=False):
    output.append(
        {
            "common_name": taxon.commonName,
            "scientific_name": taxon.scientificName,
            "prompt": [
                f"a photo of {taxon.commonName}",
                f"a photo of {taxon.scientificName}",
                f"a wildlife photograph of {taxon.scientificName}",
                f"an image of {taxon.scientificName}, commonly known as {taxon.commonName}"
            ]
        }
    )

with open(PROCESSED_DATA, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print(f"All done! The image model will now be able to use the data saved at {PROCESSED_DATA}")
