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
STATUS = {"accepted", "provisionally accepted"}

OMITTED_PHYLUM = {
    # animalia
    "Bryozoa", # tiny colonial aquatic invertebrates
    "Entoprocta", # tiny sessile aquatic invertebrates
    "Cycliophora", # microscopic commensal organisms found on lobsters' mouthparts
    "Dicyemida", # kidney parasites of cephalopods
    "Gastrotricha", # simple microscopic aquatic organisms
    "Gnathostomulida", # nearly microscopic marine animals similar to flatworms
    "Kinorhyncha", # tiny marine invertebrates that live in mud and sand
    "Loricifera", # tiny marine armored animals that attach themselves to sediment
    "Micrognathozoa", # microscopic freshwater animals
    "Orthonectida", # microscopic parasites of marine invertebrates
    "Placozoa", # extremely simple microscopic organisms
    "Rotifera", # nearly microscopic zooplankton
    "Tardigrada", # microscopic relatives of arthropods
    "Xenacoelomorpha", # small marine flatworm-like animals
}

OMITTED_CLASS = {
    # arthropoda
    "Mystacocarida", # tiny marine crustaceans
    "Copepoda", # near microscopic crutstaceans found basically everywhere there's water
    "Tantulocarida", # microscopic parasitic crustaceans
    "Cephalocarida", # "horseshoe shrimp" -- near microscopic crustaceans
    "Protura", # tiny soil-dwelling hexapods
    # platyhelminthes
    "Monogenea", # parasitic flatworms found on the skin and gills of fish -- mostly microscopic
    "Trematoda", # flukes -- small parasites that you do NOT want to see
    "Cestoda", # tapeworms (yuck)
}

OMITTED_ORDER = {
    # arachnida
    "Sarcoptiformes", # microscopic mites
}

OMITTED_FAMILY = {
    # trombidiformes
    "Demodecidae", # microscopic mammalian mites
    "Tanaupodidae", # there is zero information on these guys
    "Allotanaupodidae", # also zero information
    "Tarsonemidae", # microscopic thread-footed mites
    "Tydeidae", # nearly microscopic soft-bodied mites
    "Veigaiidae", # microscopic free-living mites
}

COLLAPSE_TO_PHYLUM = {
    # animalia
    "Nematomorpha", # horsehair worms
    "Chaetognatha", # arrow worms
    "Priapulida", # penis worms
}

COLLAPSE_TO_CLASS = {

}


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
