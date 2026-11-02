
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
REPORT = ROOT / "metadata" / "harmonisation"

FAMILLES = {
    "caracteristiques": ["Num_Acc"],
    "lieux": None,
    "vehicules": ["Num_Acc", "id_vehicule"],
    "usagers": None,
}

resultats = []

for famille, cles_uniques in FAMILLES.items():
    fichier = SILVER / f"{famille}_2019_2024.csv"

    df = pd.read_csv(
        fichier,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )

    colonnes_cles = ["Num_Acc"]

    if famille in ["vehicules", "usagers"]:
        colonnes_cles.append("id_vehicule")

    for colonne in colonnes_cles:
        valeurs = df[colonne].astype(str).str.strip()
        vides = valeurs.eq("").sum()

        resultats.append({
            "famille": famille,
            "controle": f"valeurs_vides_{colonne}",
            "valeur": int(vides)
        })

        print(f"{famille} - {colonne} vide : {vides}")

    if cles_uniques:
        doublons = df.duplicated(subset=cles_uniques).sum()

        resultats.append({
            "famille": famille,
            "controle": "doublons_cle_unique",
            "valeur": int(doublons)
        })

        print(f"{famille} - doublons clé : {doublons}")

REPORT.mkdir(parents=True, exist_ok=True)

pd.DataFrame(resultats).to_csv(
    REPORT / "rapport_cles_baac.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nRapport enregistré : rapport_cles_baac.csv")
