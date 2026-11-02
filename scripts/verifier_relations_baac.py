
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
REPORT = ROOT / "metadata" / "harmonisation"

REPORT.mkdir(parents=True, exist_ok=True)

familles = ["caracteristiques", "lieux", "vehicules", "usagers"]

donnees = {}

for famille in familles:
    chemin = SILVER / f"{famille}_2019_2024.csv"

    donnees[famille] = pd.read_csv(
        chemin,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )

print("===== CONTROLE DES RELATIONS BAAC =====")

carac = donnees["caracteristiques"]

# Contrôle de l'identifiant accident
ids_reference = set(carac["Num_Acc"])

rapport = []

for famille in ["lieux", "vehicules", "usagers"]:
    df = donnees[famille]
    ids = set(df["Num_Acc"])

    absents = ids - ids_reference
    sans_reference = df[~df["Num_Acc"].isin(ids_reference)]

    print(f"\n{famille.upper()}")
    print("Lignes :", len(df))
    print("Identifiants distincts :", len(ids))
    print("Accidents sans correspondance :", len(absents))
    print("Lignes sans correspondance :", len(sans_reference))

    rapport.append({
        "controle": "Num_Acc",
        "famille": famille,
        "lignes": len(df),
        "identifiants_distincts": len(ids),
        "ids_sans_reference": len(absents),
        "lignes_sans_reference": len(sans_reference)
    })

# Contrôle des véhicules associés aux usagers
vehicules = donnees["vehicules"]
usagers = donnees["usagers"]

# Clé composite : accident + véhicule
cles_vehicules = set(
    zip(vehicules["Num_Acc"], vehicules["id_vehicule"])
)

cles_usagers = list(
    zip(usagers["Num_Acc"], usagers["id_vehicule"])
)

sans_vehicule = sum(
    cle not in cles_vehicules
    for cle in cles_usagers
)

print("\nUSAGERS -> VEHICULES")
print("Lignes usagers :", len(usagers))
print("Usagers sans véhicule correspondant :", sans_vehicule)

rapport.append({
    "controle": "Num_Acc + id_vehicule",
    "famille": "usagers_vehicules",
    "lignes": len(usagers),
    "identifiants_distincts": "",
    "ids_sans_reference": "",
    "lignes_sans_reference": sans_vehicule
})

pd.DataFrame(rapport).to_csv(
    REPORT / "rapport_relations_baac.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nRapport enregistré : rapport_relations_baac.csv")
