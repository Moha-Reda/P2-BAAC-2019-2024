
from pathlib import Path
import pandas as pd

# ==========================================
# WP2-05 - ENRICHISSEMENT DU DICTIONNAIRE BAAC
# Periode : 2019-2024
# ==========================================

ROOT = Path(__file__).resolve().parent.parent

FICHIER = (
    ROOT / "metadata" / "codifications"
    / "dictionnaire_baac_complet.csv"
)

BACKUP = (
    ROOT / "metadata" / "codifications"
    / "dictionnaire_baac_avant_enrichissement.csv"
)

# 1. Lecture du dictionnaire

df = pd.read_csv(
    FICHIER,
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig"
)

# 2. Sauvegarde avant modification

if not BACKUP.exists():
    df.to_csv(
        BACKUP,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

# 3. Definitions des variables

definitions = {
    "lieux": {
        "Num_Acc": "Identifiant de l'accident",
        "catr": "Categorie de route",
        "voie": "Numero ou designation de la route",
        "v1": "Indice numerique du numero de route",
        "v2": "Indice alphanumerique de la route",
        "circ": "Regime de circulation",
        "nbv": "Nombre total de voies de circulation",
        "vosp": "Presence et nature d'une voie reservee",
        "prof": "Profil en long de la route",
        "pr": "Numero du point de repere routier",
        "pr1": "Distance en metres au point de repere",
        "plan": "Trace en plan de la route",
        "lartpc": "Largeur du terre-plein central en metres",
        "larrout": "Largeur de la chaussee en metres",
        "surf": "Etat de la surface de la chaussee",
        "infra": "Amenagement ou infrastructure",
        "situ": "Situation de l'accident sur la voirie",
        "vma": "Vitesse maximale autorisee",
        "annee": "Annee d'origine ajoutee pendant l'harmonisation"
    },

    "vehicules": {
        "Num_Acc": "Identifiant de l'accident",
        "id_vehicule": "Identifiant du vehicule",
        "num_veh": "Identifiant alphanumerique du vehicule",
        "senc": "Sens de circulation du vehicule",
        "catv": "Categorie du vehicule",
        "obs": "Obstacle fixe heurte",
        "obsm": "Obstacle mobile heurte",
        "choc": "Point de choc initial du vehicule",
        "manv": "Manoeuvre principale avant l'accident",
        "motor": "Type de motorisation du vehicule",
        "occutc": "Nombre d'occupants du transport en commun",
        "annee": "Annee d'origine ajoutee pendant l'harmonisation"
    },

    "usagers": {
        "Num_Acc": "Identifiant de l'accident",
        "id_usager": "Identifiant de l'usager lorsqu'il est disponible",
        "id_vehicule": "Identifiant du vehicule associe a l'usager",
        "num_veh": "Identifiant alphanumerique du vehicule associe",
        "place": "Place occupee dans le vehicule",
        "catu": "Categorie de l'usager",
        "grav": "Gravite des blessures de l'usager",
        "sexe": "Sexe de l'usager",
        "an_nais": "Annee de naissance de l'usager",
        "trajet": "Motif du deplacement",
        "secu1": "Premier equipement de securite renseigne",
        "secu2": "Deuxieme equipement de securite renseigne",
        "secu3": "Troisieme equipement de securite renseigne",
        "locp": "Localisation du pieton",
        "actp": "Action du pieton",
        "etatp": "Situation du pieton seul ou accompagne",
        "annee": "Annee d'origine ajoutee pendant l'harmonisation"
    }
}

# 4. Enrichissement sans ecraser l'existant

ajoutees = 0
deja_documentees = 0

for index, row in df.iterrows():
    famille = row["famille"]
    variable = row["variable"]

    definition = definitions.get(famille, {}).get(variable)

    if definition is None:
        continue

    if row["definition"].strip():
        deja_documentees += 1
        continue

    df.at[index, "definition"] = definition
    df.at[index, "statut"] = "DEFINITION_DOCUMENTEE"
    ajoutees += 1

# 5. Enregistrement

df.to_csv(
    FICHIER,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# 6. Controle final

sans_definition = df["definition"].str.strip().eq("")

print("\n===== BILAN DICTIONNAIRE BAAC =====")

print("Definitions ajoutees :", ajoutees)
print("Definitions deja presentes :", deja_documentees)
print("Total des entrees :", len(df))
print("Definitions remplies :", int((~sans_definition).sum()))
print("Definitions manquantes :", int(sans_definition.sum()))

print("\n===== BILAN PAR FAMILLE =====")

for famille, groupe in df.groupby("famille"):
    nb = groupe["definition"].str.strip().ne("").sum()
    print(f"{famille} : {nb}/{len(groupe)} definitions")

if sans_definition.any():
    print("\nVariables sans definition :")
    print(
        df.loc[sans_definition, ["famille", "variable"]]
        .to_string(index=False)
    )

print("\nSauvegarde :", BACKUP)
print("Dictionnaire :", FICHIER)
print("\nTraitement termine.")
