# Create a smaller Taxon file that has exclusively animal data

import pandas as pd
import csv
from config import (DATABASE_TAXON,
                    PROCESSED_TAXON, 
                    DATABASE_NAMES, 
                    PROCESSED_NAMES, 
                    KINGDOM, STATUS, 
                    TAXON_RANKS, 
                    TAXON_COLS, 
                    LANGUAGE, 
                    NAME_COLS, 
                    DATA, 
                    OUTPUT,
                    DATABASE_SPECIES_PROFILE,
                    PROFILE_COLS,
                    PROCESSED_SPECIES_PROFILE
                )
from pathlib import Path
import sys

csv.field_size_limit(sys.maxsize)

# Function to create a simplified Taxon file to save time when parsing it
def create_taxon_file(input_file, output_file):
    print("Starting the reading process. This may take a while...")

    first_chunk = True
    total_taxa = 0

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
        taxa = chunk[
            (chunk["dwc:kingdom"].isin(KINGDOM)) &
            (chunk["dwc:taxonomicStatus"].isin(STATUS)) &
            (chunk["dwc:taxonRank"].isin(TAXON_RANKS)) &
            (~chunk["dwc:taxonID"].str.startswith("BOLD.", na=False))
        ]

        num_taxa = len(taxa)

        print(f"Saving {num_taxa} taxa")

        taxa.to_csv(
            output_file,
            sep="\t",
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk
        )

        total_taxa += num_taxa

        first_chunk = False

    print(f"Successfully created {output_file} with {total_taxa} taxa!")

# Function to create a simplified VernacularName file to save time when parsing it
def create_vernacular_names_file(taxon_file, input_file, output_file):
    print("Gathering taxa IDs into a set...")

    animal_ids = set(
        pd.read_csv(
            taxon_file,
            sep="\t",
            quoting=csv.QUOTE_NONE,
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
        quoting=csv.QUOTE_NONE,
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

# Function to create a simplified SpeciesProfile file to save time when parsing it
def create_species_profile_file(taxon_file, input_file, output_file):
    print("Gathering taxa IDs into a set...")

    animal_ids = set(
        pd.read_csv(
            taxon_file,
            sep="\t",
            quoting=csv.QUOTE_NONE,
            usecols=["dwc:taxonID"],
            dtype=str
        )["dwc:taxonID"]
    )

    print("Done!")

    print("Starting the reading process. This may take a while...")

    first_chunk = True

    total_profiles = 0

    for chunk in pd.read_csv(
        input_file,
        sep="\t",
        quoting=csv.QUOTE_NONE,
        dtype=str,
        on_bad_lines="skip",
        chunksize=100_000,
        usecols=PROFILE_COLS
    ):
        filtered_profiles = chunk[
            (chunk["dwc:taxonID"].isin(animal_ids))
        ]

        num_profiles = len(filtered_profiles)

        print(f"Saving {num_profiles} vernacular names")

        filtered_profiles.to_csv(
            output_file,
            sep="\t",
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk
        )

        total_profiles += num_profiles

        first_chunk = False

    print(f"Successfully created {output_file} with {total_profiles} profiles!")
    

# main
def main(force=False):
    # Make sure data folder exists
    DATA.mkdir(exist_ok=True)
    OUTPUT.mkdir(exist_ok=True)
    # Generate processed taxon file
    if force or not Path.exists(PROCESSED_TAXON):
        create_taxon_file(DATABASE_TAXON, PROCESSED_TAXON)
    else:
        print(f"Using existing {PROCESSED_TAXON}")
    # Generate processed names file
    if force or not Path.exists(PROCESSED_NAMES):
        create_vernacular_names_file(PROCESSED_TAXON, DATABASE_NAMES, PROCESSED_NAMES)  
    else:
        print(f"Using existing {PROCESSED_NAMES}")
    # Generate species profile file
    if force or not Path.exists(PROCESSED_SPECIES_PROFILE):
        create_species_profile_file(PROCESSED_TAXON, DATABASE_SPECIES_PROFILE, PROCESSED_SPECIES_PROFILE)
    else:
        print(f"Using existing {PROCESSED_SPECIES_PROFILE}")

if __name__ == "__main__":
    main(True)
