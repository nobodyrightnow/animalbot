from pathlib import Path
import inflect

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"

PROCESSED = DATA / "processed"

DATABASE_TAXON = DATA / "Taxon.tsv"
DATABASE_NAMES = DATA / "VernacularName.tsv"
DATABASE_SPECIES_PROFILE = DATA / "SpeciesProfile.tsv"

CACHE = DATA / "cache"

TAXA_EMBEDDINGS = CACHE / "taxa_embeddings.pt"

RANKS = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]
LANGUAGE = {"eng"}

a_an = inflect.engine()

def article(name):
    return a_an.a(name)

# openCLIP template prompts
PROMPT_TEMPLATES = {
    "scientific_NON_SPECIES": [
        lambda r, c: f"an organism in the {r} {c}",
        lambda r, c: f"a member of the {r} {c}",
        lambda r, c: f"a specimen belonging to the {r} {c}",
        lambda r, c: f"an organism belonging to the {r} {c}",
        lambda r, c: f"an image of a member of the {r} {c}",
        lambda r, c: f"a representative of the {r} {c}",
    ],
    "common_and_species": [
        lambda c: f"a photograph of {article(c)}",
        lambda c: f"an image of {article(c)}",
        lambda c: f"a wildlife photo of {article(c)}",
        lambda c: f"a close-up photograph of {article(c)}",
        lambda c: f"a field photograph of {article(c)}",
        lambda c: f"a biological specimen of {article(c)}",
    ]
}
