
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

for annee in [2023, 2024]:
    print(f"\n========== ANNÉE {annee} ==========")

    chemin_lieux = RAW / str(annee) / f"lieux_{annee}.csv"
    chemin_carac = RAW / str(annee) / f"caracteristiques_{annee}.csv"

    lieux = pd.read_csv(
        chemin_lieux,
        sep=";",
        dtype=str,
        keep_default_na=False
    )

    carac = pd.read_csv(
        chemin_carac,
        sep=";",
        dtype=str,
        keep_default_na=False
    )

    ids_lieux = lieux["Num_Acc"].str.strip()
    ids_carac = carac["Num_Acc"].str.strip()

    uniques_lieux = set(ids_lieux)
    uniques_carac = set(ids_carac)

    print("Lignes lieux :", len(lieux))
    print("Lignes caractéristiques :", len(carac))

    print("Identifiants uniques lieux :", len(uniques_lieux))
    print("Identifiants uniques caractéristiques :", len(uniques_carac))

    print("Identifiants répétés dans lieux :",
          ids_lieux.duplicated().sum())

    print("Lignes entièrement identiques dans lieux :",
          lieux.duplicated().sum())

    absents_carac = uniques_lieux - uniques_carac
    absents_lieux = uniques_carac - uniques_lieux

    print("IDs lieux absents de caractéristiques :", len(absents_carac))
    print("IDs caractéristiques absents de lieux :", len(absents_lieux))

    print("Exemples IDs répétés :",
          ids_lieux[ids_lieux.duplicated()].head(5).tolist())

    print("Exemples IDs absents de caractéristiques :",
          sorted(absents_carac)[:5])
