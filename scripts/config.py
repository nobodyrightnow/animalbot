from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"

OUTPUT = DATA / "processed"

DATABASE_TAXON = DATA / "Taxon.tsv"
DATABASE_NAMES = DATA / "VernacularName.tsv"
PROCESSED_TAXON = OUTPUT / "Taxon_Animalia.tsv"
PROCESSED_NAMES = OUTPUT / "VernacularName_Animalia_Eng.tsv"

PROCESSED_DATA = OUTPUT / "taxa.json"

CACHE = ROOT / "cache"
TAXA_EMBEDDINGS = CACHE / "taxa_embeddings.pt"

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

LANGUAGE = {"eng"}

# i wrote omitted phylum before realizing it would've been much easier to pick the ones to include instead... i'll keep them both for reference, so you can switch things around if you desire
# note that these are only animal phyla

PHYLUM = {
    "Arthropoda", # insects, spiders, etc.
    "Brachiopoda", # similar to bivalve molluscs
    "Chordata", # vertebrates
    "Cnidaria", # jellyfish, corals, anemones
    "Ctenophora", # comb jellies
    "Echinodermata", # starfish, urchins, sea cucumbers, etc.
    "Mollusca", # snails, octopi, etc.
    "Onychophora" # velvet worms
}

OMITTED_PHYLUM = {
    # Filter out (mostly) unphotographable animals by phylum
    "Cycliophora", # microscopic commensal aquatic animals
    "Micrognathozoa", # microscopic freshwater animal
    "Nematoda", # nematodes
    "Loricifera", # microscopic sediment-dwelling animal
    "Bryozoa", # bryozoans
    "Ectoprocta", # another name for Bryozoa, just in case
    "Kinorhyncha", # microscopic mud and sand-dwelling marine invertebrates
    "Dicyemida", # cephalopod kidney parasites
    "Rhombozoa", # another name for dicyemida, just in case
    "Gastrotricha", # microscopic hairy cylindrical invertebrates
    "Gnathostomulida", # jaw worms
    "Hemichordata", # microscopic marine worm-shaped organisms
    "Orthonectida", # simple microscopic parasites
    "Placozoa", # simple blob-like animals
    "Chaetognatha", # arrow worms
    "Rotifera", # microscopic zooplankton
    "Tardigrada", # tardigrades
    "Monoblastozoa", # a phylum made around a species described by one guy who was probably lying
    # Filter out extinct phylums
    "Proarticulata",
    "Petalonamae",
    "Trilobozoa",
    "Vetulicolia", # disputed phylum, but just in case
    "Agmata", # proposed phylum, but just in case
    "Saccorhytida",
    # Filter out certain kinds of animals to reduce scope
    "Annelida", # worms
    "Chaetognatha", # arrow worms
    "Nematomorpha", # horsehair worms
    "Nemertea", # ribbon worms
    "Phoronida", # horseshoe worms
    "Priapulida", # penis worms
    "Platyhelminthes", # flatworms
    "Porifera", # spongebobs
    "Xenacoelomorpha", # flatworm-like animals
    "Entoprocta" # sessile organisms similar to bryozoans
}

# use "omitted" for the rest of these specifications; there's way too many to include manually

OMITTED_CLASS = {
    "Myxozoa", # cnidarian parasites
    "Polypodiozoa", # cnidarian parasites
    "Octocorallia", # soft corals
    "Hexacorallia", # other corals and anemones
}

OMITTED_ORDER = {
    "Psocodea", # lice
    "Ixodida", # ticks
    "Trombidiformes", # mites
    "Sarcoptiformes", # more mites
}
