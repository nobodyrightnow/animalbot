# Parse the processed database to make it into a json format usable by the computer vision model

import pandas as pd
import csv
import json
from config import (
    PROCESSED_NAMES, 
    NAME_COLS, LANGUAGE, 
    PROCESSED_TAXON, 
    TAXON_COLS, 
    KINGDOM, 
    TAXON_RANKS, 
    STATUS, 
    PHYLUM, 
    OMITTED_ORDER, 
    PROCESSED_DATA,
    CLASS,
    PROCESSED_SPECIES_PROFILE,
    PROFILE_COLS,
    EXTINCT
)

print("Starting to read common names.")

# Read in all of the common names of taxa
vernacular = pd.read_csv(
    PROCESSED_NAMES,
    sep="\t",
    quoting=csv.QUOTE_NONE,
    on_bad_lines="skip",
    dtype=str,
    usecols=NAME_COLS
)

total = len(vernacular)
print(f"Read in {total} common names")

# Filter names
vernacular = vernacular[
    (vernacular["dcterms:language"].isin(LANGUAGE))
]

new_num = len(vernacular)
print(f"Filtered out {total - new_num} of excluded languages. There are now {new_num} names")
total = new_num

# Remove extra names for species
vernacular = vernacular.drop_duplicates(subset="dwc:taxonID")

new_num = len(vernacular)
print(f"Dropped {total - new_num} duplicate names. There are now {new_num} names")
total = new_num

# Create new commonName col for lowercase (faster than doing it during the loop later)
vernacular["commonName"] = vernacular["dwc:vernacularName"].str.lower()

print(f"{total} common names have been stored!")
# Read in species profiles for extinction data
print("Starting to read species profiles...")

profiles = pd.read_csv(
    PROCESSED_SPECIES_PROFILE,
    sep="\t",
    quoting=csv.QUOTE_NONE,
    dtype=str,
    usecols=PROFILE_COLS
)

total = len(profiles)
print(f"Read in {total} profiles")

# Filter profiles
profiles = profiles[
    (profiles["gbif:isExtinct"] == EXTINCT)
]

new_num = len(profiles)
print(f"Filtered out {total - new_num} species profiles. There are now {new_num} profiles")
total = new_num

# Read in all of the taxonomic data
print("Starting to read other taxa data. This may take a while...")


taxa = pd.read_csv(
    PROCESSED_TAXON,
    sep="\t",
    quoting=csv.QUOTE_NONE,
    engine="python",
    on_bad_lines="skip",
    usecols=TAXON_COLS
)

total = len(taxa)
print(f"Read in {total} taxa")

taxa = taxa.rename(columns={
    "dwc:kingdom": "kingdom",
    "dwc:phylum": "phylum",
    "dwc:class": "class_taxon",
    "dwc:order": "order",
})

# Filter taxa
taxa = taxa[
    # By kingdom
    (taxa["kingdom"].isin(KINGDOM)) &
    # By phylum
    (taxa["phylum"].isin(PHYLUM)) &
    # By class
    (taxa["class_taxon"].isin(CLASS)) &
    # By order
    (~taxa["order"].isin(OMITTED_ORDER)) &
    # By rank
    (taxa["dwc:taxonRank"].isin(TAXON_RANKS)) &
    # By status
    (taxa["dwc:taxonomicStatus"].isin(STATUS))
]

new_num = len(taxa)
print(f"Filtered out {total - new_num} taxa. There are now {new_num} taxa")
total_taxa = new_num

# Create new scientificName col based on genericName and specificEpithet
taxa["scientificName"] = (
    taxa["dwc:genericName"].fillna("") + " " + taxa["dwc:specificEpithet"].fillna("")
).str.strip()

print(f"{total} taxa have been stored!")
print("Starting to merge the data. This may take a while...")

# Merge common names and taxa based on common factor (taxonID)
taxa = taxa.merge(vernacular, on="dwc:taxonID")
# Merge profiles and taxa based on common factor (taxonID)
taxa = taxa.merge(profiles, on="dwc:taxonID")

new_num = len(taxa)
print(f"The data has been merged successfully! {total - new_num} taxa were lost")
total = new_num
print(f"Starting to write {total} taxa to the output file. This may take a while...")

# Write to json file
output = []

for taxon in taxa.itertuples(index=False):
    output.append(
        {
            "common_name": taxon.commonName,
            "scientific_name": taxon.scientificName,
            "taxonomy": {
                "class": taxon.class_taxon
            },
            # BioCLIP is trained on specific taxon data, so it shouldn't need
            # filler words like "a photo of a" like other CLIP models.
            # Additionally, scientific names are more useful to it
            # because they are entirely unique to a species and should prevent confusion.
            "prompts": [
                f"{taxon.scientificName}",
                f"{taxon.commonName} ({taxon.scientificName})"
            ]
        }
    )

with open(PROCESSED_DATA, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print(f"All done! The image model will now be able to use the data saved at {PROCESSED_DATA}")
