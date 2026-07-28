# Create a smaller Taxon file that has exclusively animal data

import pandas as pd
import csv
from config import DATABASE_TAXON, PROCESSED_TAXON, DATABASE_NAMES, PROCESSED_NAMES, KINGDOM, STATUS, TAXON_RANKS, TAXON_COLS, LANGUAGE, NAME_COLS, DATA, OUTPUT
from pathlib import Path
import sys

csv.field_size_limit(sys.maxsize)

# Make sure data folder exists
DATA.mkdir(exist_ok=True)

# Function to create a simplified Taxon file to save time when parsing it
def create_animal_taxon_file(input_file, output_file):
    print("Starting the reading process. This may take a while...")

    first_chunk = True
    total_animals = 0

    for chunk in pd.read_csv(
        input_file,
        sep="\t",
        quoting=csv.QUOTE_NONE,
        dtype=str,
        engine="python",
        on_bad_lines="error",
        chunksize=100_000,
        usecols=TAXON_COLS
    ):
        # operation find agent p
        platypus = chunk[chunk["dwc:taxonID"] == "74WBV"]
        if not platypus.empty:
            print("Found platypus!")
            print(platypus)
        else:
            print("No platypus here")

        animals = chunk[
            (chunk["dwc:kingdom"].isin(KINGDOM)) &
            (chunk["dwc:taxonomicStatus"].isin(STATUS)) &
            (chunk["dwc:taxonRank"].isin(TAXON_RANKS)) &
            (~chunk["dwc:taxonID"].str.startswith("BOLD.", na=False))
        ]

        print("Still present?", (animals["dwc:taxonID"] == "74WBV").any())

        num_animals = len(animals)

        print(f"Saving {num_animals} taxa")

        animals.to_csv(
            output_file,
            sep="\t",
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk
        )

        total_animals += num_animals

        first_chunk = False

    print(f"Successfully created {output_file} with {total_animals} taxa!")

# Function to create a simplified VernacularName file to save time when parsing it
def create_vernacular_names_file(taxon_file, input_file, output_file):
    print("Gathering taxon IDs into a set...")

    animal_ids = set(
        pd.read_csv(
            taxon_file,
            sep="\t",
            usecols=["dwc:taxonID"],
            dtype=str
        )["dwc:taxonID"]
    )

    print("Done!")

    print("Starting the reading process. This may take a while...")

    first_chunk = True

    total_names = 0

    for chunk in pd.read_csv(
        input_file,
        sep="\t",
        quoting=csv.QUOTE_MINIMAL,
        dtype=str,
        on_bad_lines="skip",
        chunksize=100_000,
        usecols=NAME_COLS
    ):
        filtered_names = chunk[
            (chunk["dwc:taxonID"].isin(animal_ids)) &
            (chunk["dcterms:language"].isin(LANGUAGE))
        ]

        num_names = len(filtered_names)

        print(f"Saving {num_names} vernacular names")

        filtered_names.to_csv(
            output_file,
            sep="\t",
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk
        )

        total_names += num_names

        first_chunk = False

    print(f"Successfully created {output_file} with {total_names} names!")

# main
def main(force=False):
    if force or not Path.exists(PROCESSED_TAXON):
        DATA.mkdir(exist_ok=True)
        OUTPUT.mkdir(exist_ok=True)
        create_animal_taxon_file(DATABASE_TAXON, PROCESSED_TAXON)
    else:
        print(f"Using existing {PROCESSED_TAXON}")
    if force or not Path.exists(PROCESSED_NAMES):
        DATA.mkdir(exist_ok=True)
        OUTPUT.mkdir(exist_ok=True)
        create_vernacular_names_file(PROCESSED_TAXON, DATABASE_NAMES, PROCESSED_NAMES)
    else:
        print(f"Using existing {PROCESSED_NAMES}")


if __name__ == "__main__":
    main(True)
