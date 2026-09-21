# INFORMATION ON PREPROCESSING COL FILES

# useful:
# col:ID | cross-referencing specific taxa between files
# col:status | filtering out disputed species
# col:scientificName
# col:rank | kingdom, species, etc.
# col:specificEpithet | second part of the binomial name; necessary for constructing scientificName manually to avoid subgenus in parentheses
# col:nameStatus | accepted, established, not established, doubtful, NaN
# col:extinct | filtering out extinct species
# col:species
# col:subgenus
# col:genus
# col:subtribe
# col:tribe
# col:subfamily
# col:family
# col:superfamily
# col:suborder
# col:order
# col:subclass
# col:class
# col:subphylum
# col:phylum
# col:kingdom

# not useful:
# col:parentID
# col:etymology
# col:alternativeID
# col:nameAlternativeID
# col:sourceID
# col:basionymID
# col:originalSpelling
# col:notho
# col:gender
# col:genderAgreement
# col:authorship
# col:combinationAuthorship
# col:combinationAuthorshipID
# col:combinationExAuthorship
# col:combinationExAuthorshipID
# col:combinationAuthorshipYear
# col:basionymAuthorship
# col:basionymAuthorshipID
# col:basionymAuthorshipYear
# col:namePhrase
# col:nameReferenceID
# col:namePublishedInYear
# col:namePublishedInPage
# col:namePublishedInPageLink
# col:accordingToID
# col:accordingToPage
# col:accordingToPageLink
# col:referenceID
# col:scrutinizer
# col:scrutinizerID
# col:scrutinizerDate
# col:temporalRangeStart
# col:temporalRangeEnd
# col:uninomial
# col:cultivarEpithet | additional name given to plant species
# col:infraspecificEpithet | additional term given to subspecies
# col:genericName | identical to genus
# col:infragenericEpithet | subgenus
# col:code
# col:environment
# col:link
# col:section | another division usually used for plants and fungi, between species and subgenus
# col:ordinal
# col:nameRemarks
# col:remarks
# col:modified
# col:modifiedBy
# clb:merged

import pandas as pd
import csv
import json
from pathlib import Path
from config import (
    DATABASE_TAXON,
    DATABASE_NAMES,
    LANGUAGE,
    RANKS,
    PROCESSED,
    OMITTED_PHYLUM,
    OMITTED_CLASS,
    OMITTED_ORDER,
    OMITTED_FAMILY,
    STATUS
)

csv.field_size_limit(10_000_000) # so python engine won't cry when reading files

# A function to read in taxonomic data into a dataframe
def read_taxa(taxa_file: Path) -> pd.DataFrame:
    print("Reading...")

    taxa = pd.read_csv(
        taxa_file,
        sep="\t",
        quoting=csv.QUOTE_NONE,
        engine="python",
        on_bad_lines="error",
        dtype=str,
        usecols=[
            "col:ID",
            "col:status",
            "col:scientificName",
            "col:rank",
            "col:specificEpithet",
            "col:nameStatus",
            "col:extinct",
            "col:species",
            "col:genus",
            "col:family",
            "col:order",
            "col:class",
            "col:phylum",
            "col:kingdom",
        ]
    )

    total_taxa = len(taxa)
    print(f"Read in {total_taxa} taxa. Filtering...")

    # Filter out certain ranks, extinct taxa, and statuses
    taxa = taxa[
        ~(taxa["col:rank"].isin(["unranked", "subspecies"])) &
        (taxa["col:extinct"] != "true") &
        (taxa["col:status"].isin(STATUS)) &
        ~(taxa["col:nameStatus"].isin(["doubtful", "not established"])) &
        ~(taxa["col:phylum"].isin(OMITTED_PHYLUM)) &
        ~(taxa["col:class"]).isin(OMITTED_CLASS) &
        ~(taxa["col:order"].isin(OMITTED_ORDER)) &
        ~(taxa["col:family"].isin(OMITTED_FAMILY))
    ]

    new_num_taxa = len(taxa)
    print(f"Filtered out {total_taxa - new_num_taxa} taxa. There are now {new_num_taxa} taxa.")

    # Rename columns to avoid confusion with "class" keyword and to match ID with vernacular names
    taxa = taxa.rename(columns={
        "col:class": "class_rank",
        "col:ID": "col:taxonID",
    })

    return taxa

# A function to read vernacular names into a dataframe
def read_names(names_file: Path) -> pd.DataFrame:
    print("Reading...")

    names = pd.read_csv(
        names_file,
        sep="\t",
        quoting=csv.QUOTE_NONE,
        engine="python",
        on_bad_lines="error",
        dtype=str,
        usecols=[
            "col:taxonID",
            "col:language",
            "col:transliteration",
        ]
    )

    total_names = len(names)
    print(f"Read in {total_names} names. Filtering...")

    # Filter out other languages
    names = names[
        (names["col:language"].isin(LANGUAGE))
    ]

    # Remove duplicates
    names = names.drop_duplicates(subset="col:taxonID")
    new_num_names = len(names)
    print(f"Filtered out {total_names - new_num_names}. There are now {new_num_names} names.")

    return names

# A function to take a dataframe and output the data into different json files by taxonomic rank
def output_taxa_data(taxa: pd.DataFrame) -> None:
    current_div = 1
    total_divs = len(RANKS)
    COLUMN_MAP = {
        "class": "class_rank",
    }

    # Loop through taxon ranks to divide them into different json files
    for division in RANKS:
        print(f"Parsing dataframe... ({current_div}/{total_divs})")

        # Filter by current taxon rank
        rank = taxa[taxa["rank"] == division]
        output = []

        # Loop through rows and add the dict structure to output
        for row in rank.itertuples(index=False):
            # construct scientificName manually for species
            scientificName = ""
            if (division == "species"): # to remove subgenus from it
                scientificName = f"{row.genus} {row.specificEpithet}"
            else:
                scientificName = row.scientificName
            taxonomy = {}
            for division2 in RANKS:
                if division2 == division:
                    break
                else:
                    attr = COLUMN_MAP.get(division2, division2)
                    taxonomy[division2] = getattr(row, attr)
            output.append(
                {
                    "scientificName": scientificName,
                    "commonName": str(row.transliteration).lower(),
                    "taxonomy": taxonomy
                }
            )

        print(f"Outputting to file... ({current_div}/{total_divs})")

        # Output the array of dicts to a json file
        file_path = PROCESSED / f"{division}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent="\t")
        current_div += 1


taxa = read_taxa(DATABASE_TAXON)
names = read_names(DATABASE_NAMES)

print("Merging...")
taxa = taxa.merge(names, on="col:taxonID", how="left")
taxa.columns = taxa.columns.str.removeprefix("col:")
taxa = taxa.fillna("")
print("Merged!")

output_taxa_data(taxa)
print("Done!")
