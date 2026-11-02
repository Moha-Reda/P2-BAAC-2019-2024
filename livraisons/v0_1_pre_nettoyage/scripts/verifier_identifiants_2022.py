
from pathlib import Path
import pandas as pd

dossier = Path("data/raw/2022")

caracteristiques = pd.read_csv(
    dossier / "caracteristiques_2022.csv",
    sep=";",
    dtype=str,
    keep_default_na=False
)

lieux = pd.read_csv(
    dossier / "lieux_2022.csv",
    sep=";",
    dtype=str,
    keep_default_na=False
)

ids_caracteristiques = set(caracteristiques["Accident_Id"])
ids_lieux = set(lieux["Num_Acc"])

manquants_lieux = ids_caracteristiques - ids_lieux
manquants_caracteristiques = ids_lieux - ids_caracteristiques

print("=== VÉRIFICATION DES IDENTIFIANTS 2022 ===")

print("Lignes caractéristiques :", len(caracteristiques))
print("Lignes lieux :", len(lieux))

print("Identifiants uniques caractéristiques :", len(ids_caracteristiques))
print("Identifiants uniques lieux :", len(ids_lieux))

print("Doublons caractéristiques :",
      caracteristiques["Accident_Id"].duplicated().sum())

print("Doublons lieux :",
      lieux["Num_Acc"].duplicated().sum())

print("Identifiants absents de lieux :", len(manquants_lieux))
print("Identifiants absents de caractéristiques :",
      len(manquants_caracteristiques))

if not manquants_lieux and not manquants_caracteristiques:
    print("OK : tous les identifiants correspondent.")
else:
    print("ATTENTION : des différences ont été détectées.")
    print("Exemples absents de lieux :", sorted(manquants_lieux)[:5])
    print("Exemples absents de caractéristiques :",
          sorted(manquants_caracteristiques)[:5])
