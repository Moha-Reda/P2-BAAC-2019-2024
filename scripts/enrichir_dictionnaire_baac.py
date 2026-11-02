
from pathlib import Path
import pandas as pd

fichier = Path("metadata/codifications/dictionnaire_baac_complet.csv")

df = pd.read_csv(
    fichier,
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig"
)

definitions = {
    "num_acc": "Identifiant unique de l'accident",
    "jour": "Jour de l'accident",
    "mois": "Mois de l'accident",
    "an": "Annee de l'accident dans la source BAAC",
    "hrmn": "Heure et minutes de l'accident",
    "lum": "Conditions d'eclairage de l'accident",
    "dep": "Code du departement",
    "com": "Code INSEE de la commune",
    "agg": "Localisation en ou hors agglomeration",
    "int": "Type d'intersection",
    "atm": "Conditions atmospheriques",
    "col": "Type de collision",
    "adr": "Adresse du lieu de l'accident",
    "lat": "Latitude en WGS84",
    "long": "Longitude en WGS84",
    "annee": "Annee d'origine ajoutee pendant l'harmonisation"
}

masque = df["famille"].eq("caracteristiques")

compteur = 0

for index in df.index[masque]:
    variable = df.at[index, "variable"].lower()

    if variable in definitions:
        df.at[index, "definition"] = definitions[variable]
        df.at[index, "statut"] = "DEFINITION_DOCUMENTEE"
        compteur += 1

df.to_csv(
    fichier,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("Definitions enrichies :", compteur)
print("Variables restant a documenter :",
      (df["statut"] == "A_DOCUMENTER").sum())

print("\nCARACTERISTIQUES :")
print(
    df[df["famille"] == "caracteristiques"][
        ["variable", "definition", "statut"]
    ].to_string(index=False)
)
