from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"

OUTPUT = DATA / "processed"

DATABASE_TAXON = DATA / "Taxon.tsv"
DATABASE_NAMES = DATA / "VernacularName.tsv"
DATABASE_SPECIES_PROFILE = DATA / "SpeciesProfile.tsv"

PROCESSED_TAXON = OUTPUT / "Taxon_Animalia.tsv"
PROCESSED_NAMES = OUTPUT / "VernacularName_Animalia_Eng.tsv"
PROCESSED_SPECIES_PROFILE = OUTPUT / "SpeciesProfile_Animalia.tsv"
PROCESSED_DATA = OUTPUT / "taxa.json"

CACHE = ROOT / "cache"
TAXA_EMBEDDINGS = CACHE / "taxa_embeddings.pt"

CLASS_DATA = OUTPUT / "classes.json"

KINGDOM = {"Animalia"}
STATUS = {"accepted"}
TAXON_RANKS = {"species", "variety"}

TAXON_COLS = [
    "dwc:taxonID",
    "dwc:taxonomicStatus",
    "dwc:taxonRank",
    "dwc:genericName",
    "dwc:specificEpithet",
    "dwc:kingdom",
    "dwc:phylum",
    "dwc:class",
    "dwc:order",
    "dwc:superfamily",
    "dwc:family",
    "dwc:subfamily",
    "dwc:tribe",
    "dwc:subtribe",
    "dwc:genus",
    "dwc:subgenus"
]

NAME_COLS = [
    "dwc:taxonID",
    "dcterms:language",
    "dwc:vernacularName"
]

PROFILE_COLS = [
    "dwc:taxonID",
    "gbif:isExtinct",
]

LANGUAGE = {"eng"}

EXTINCT = "false"

PHYLUM = {
    "Brachiopoda", # similar to bivalve molluscs
    "Chordata", # vertebrates
    "Cnidaria", # jellyfish, corals, anemones
    "Ctenophora", # comb jellies
    "Echinodermata", # starfish, urchins, sea cucumbers, etc.
    "Mollusca", # snails, octopi, etc.
    "Onychophora" # velvet worms
}

CLASS = {
    # Mammals
    "Mammalia",
    # Birds
    "Aves",
    # Reptiles
    "Reptilia",
    # Amphibians
    "Amphibia",
}

# probably use omitted here because there's a lot of orders

OMITTED_ORDER = {
    "Psocodea", # lice
    "Ixodida", # ticks
    "Trombidiformes", # mites
    "Sarcoptiformes", # more mites
}
