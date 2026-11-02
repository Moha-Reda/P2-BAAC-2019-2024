from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DOSSIER = ROOT / "metadata" / "codifications"

SOURCE = DOSSIER / "modalites_uniques_a_documenter.csv"
SORTIE = DOSSIER / "modalites_uniques_enrichies.csv"
CONFLITS = DOSSIER / "conflits_modalites.csv"

CODES = {
    ("caracteristiques", "lum"): {
        "1": "Plein jour",
        "2": "Crepuscule ou aube",
        "3": "Nuit sans eclairage public",
        "4": "Nuit avec eclairage public non allume",
        "5": "Nuit avec eclairage public allume"
    },
    ("caracteristiques", "agg"): {
        "1": "Hors agglomeration",
        "2": "En agglomeration"
    },
    ("caracteristiques", "int"): {
        "1": "Hors intersection",
        "2": "Intersection en X",
        "3": "Intersection en T",
        "4": "Intersection en Y",
        "5": "Intersection a plus de 4 branches",
        "6": "Giratoire",
        "7": "Place",
        "8": "Passage a niveau",
        "9": "Autre intersection"
    },
    ("caracteristiques", "atm"): {
        "-1": "Non renseigne",
        "1": "Normale",
        "2": "Pluie legere",
        "3": "Pluie forte",
        "4": "Neige ou grele",
        "5": "Brouillard ou fumee",
        "6": "Vent fort ou tempete",
        "7": "Temps eblouissant",
        "8": "Temps couvert",
        "9": "Autre"
    },
    ("caracteristiques", "col"): {
        "-1": "Non renseigne",
        "1": "Deux vehicules - frontale",
        "2": "Deux vehicules - par l'arriere",
        "3": "Deux vehicules - par le cote",
        "4": "Trois vehicules ou plus - en chaine",
        "5": "Trois vehicules ou plus - collisions multiples",
        "6": "Autre collision",
        "7": "Sans collision"
    },
    ("lieux", "catr"): {
        "1": "Autoroute",
        "2": "Route nationale",
        "3": "Route departementale",
        "4": "Voie communale",
        "5": "Hors reseau public",
        "6": "Parc de stationnement ouvert a la circulation",
        "7": "Route de metropole urbaine",
        "9": "Autre"
    },
    ("lieux", "circ"): {
        "-1": "Non renseigne",
        "1": "Sens unique",
        "2": "Bidirectionnelle",
        "3": "Chaussees separees",
        "4": "Voies d'affectation variable"
    },
    ("lieux", "vosp"): {
        "-1": "Non renseigne",
        "0": "Sans objet",
        "1": "Piste cyclable",
        "2": "Bande cyclable",
        "3": "Voie reservee"
    },
    ("lieux", "prof"): {
        "-1": "Non renseigne",
        "1": "Plat",
        "2": "Pente",
        "3": "Sommet de cote",
        "4": "Bas de cote"
    },
    ("lieux", "plan"): {
        "-1": "Non renseigne",
        "1": "Partie rectiligne",
        "2": "Courbe a gauche",
        "3": "Courbe a droite",
        "4": "En S"
    },
    ("lieux", "surf"): {
        "-1": "Non renseigne",
        "1": "Normale",
        "2": "Mouillee",
        "3": "Flaques",
        "4": "Inondee",
        "5": "Enneigee",
        "6": "Boue",
        "7": "Verglacee",
        "8": "Corps gras ou huile",
        "9": "Autre"
    },
    ("usagers", "catu"): {
        "1": "Conducteur",
        "2": "Passager",
        "3": "Pieton"
    },
    ("usagers", "grav"): {
        "1": "Indemne",
        "2": "Tue",
        "3": "Blesse hospitalise",
        "4": "Blesse leger"
    },
    ("usagers", "sexe"): {
        "1": "Masculin",
        "2": "Feminin"
    },
    ("usagers", "trajet"): {
        "-1": "Non renseigne",
        "0": "Non renseigne",
        "1": "Domicile - travail",
        "2": "Domicile - ecole",
        "3": "Courses - achats",
        "4": "Utilisation professionnelle",
        "5": "Promenade - loisirs",
        "9": "Autre"
    },
    ("usagers", "etatp"): {
        "-1": "Non renseigne",
        "1": "Seul",
        "2": "Accompagne",
        "3": "En groupe"
    }
}

df = pd.read_csv(
    SOURCE,
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig"
)

ajouts = 0
conflits = []

for i, row in df.iterrows():
    cle = (row["famille"], row["variable"])
    code = row["code"].strip()

    libelle = CODES.get(cle, {}).get(code)

    if libelle is None:
        continue

    ancien = row["libelle"].strip()

    if ancien and ancien != libelle:
        conflits.append({
            "famille": row["famille"],
            "variable": row["variable"],
            "code": code,
            "ancien_libelle": ancien,
            "libelle_onisr": libelle
        })
        continue

    if not ancien:
        df.at[i, "libelle"] = libelle
        ajouts += 1

    df.at[i, "statut"] = "ONISR_DOCUMENTE"

df["source"] = df["statut"].apply(
    lambda s: "ONISR - notice 2005-2024"
    if s == "ONISR_DOCUMENTE" else ""
)

df.to_csv(
    SORTIE,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(
    conflits,
    columns=[
        "famille", "variable", "code",
        "ancien_libelle", "libelle_onisr"
    ]
).to_csv(
    CONFLITS,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\n=== BILAN WP2-05 ===")
print("Codes distincts :", len(df))
print("Nouveaux libelles :", ajouts)
print("Codes documentes :", int(df["libelle"].ne("").sum()))
print("Codes a verifier :", int(df["libelle"].eq("").sum()))
print("Conflits :", len(conflits))
print("Referentiel :", SORTIE)
print("Rapport des conflits :", CONFLITS)
print("Fichiers Silver inchanges.")
