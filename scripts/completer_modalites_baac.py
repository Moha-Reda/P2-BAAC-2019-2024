from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DOSSIER = ROOT / "metadata" / "codifications"

SOURCE = DOSSIER / "modalites_uniques_enrichies.csv"
SORTIE = DOSSIER / "modalites_baac_finalisees.csv"
INCONNUS = DOSSIER / "modalites_restantes_a_verifier.csv"
CONFLITS = DOSSIER / "conflits_complement_modalites.csv"

# Correspondances de la notice ONISR du 21/10/2025
# Les codes deja documentes sont conserves.

CODES = {
    "lieux": {
        "infra": {
            "-1": "Non renseigne", "0": "Aucun",
            "1": "Souterrain ou tunnel",
            "2": "Pont ou autopont",
            "3": "Bretelle d'echangeur ou de raccordement",
            "4": "Voie ferree",
            "5": "Carrefour amenage",
            "6": "Zone pietonne",
            "7": "Zone de peage",
            "8": "Chantier",
            "9": "Autres"
        },
        "situ": {
            "-1": "Non renseigne", "0": "Aucun",
            "1": "Sur chaussee",
            "2": "Sur bande d'arret d'urgence",
            "3": "Sur accotement",
            "4": "Sur trottoir",
            "5": "Sur piste cyclable",
            "6": "Sur autre voie speciale",
            "8": "Autres"
        }
    },

    "vehicules": {
        "senc": {
            "-1": "Non renseigne", "0": "Inconnu",
            "1": "Repere ou adresse croissant",
            "2": "Repere ou adresse decroissant",
            "3": "Absence de repere"
        },
        "catv": {
            "0": "Indeterminable",
            "1": "Bicyclette",
            "2": "Cyclomoteur moins de 50 cm3",
            "3": "Voiturette",
            "4": "Ancienne categorie inutilisee",
            "5": "Ancienne categorie inutilisee",
            "6": "Ancienne categorie inutilisee",
            "7": "Voiture de tourisme seule",
            "8": "Ancienne categorie inutilisee",
            "9": "Ancienne categorie inutilisee",
            "10": "Vehicule utilitaire",
            "11": "Ancienne categorie inutilisee",
            "12": "Ancienne categorie inutilisee",
            "13": "Poids lourd de 3,5 a 7,5 tonnes",
            "14": "Poids lourd de plus de 7,5 tonnes",
            "15": "Poids lourd avec remorque",
            "16": "Tracteur routier seul",
            "17": "Tracteur routier avec semi-remorque",
            "18": "Ancienne categorie inutilisee",
            "19": "Ancienne categorie inutilisee",
            "20": "Engin special",
            "21": "Tracteur agricole",
            "30": "Scooter moins de 50 cm3",
            "31": "Motocyclette de 50 a 125 cm3",
            "32": "Scooter de 50 a 125 cm3",
            "33": "Motocyclette de plus de 125 cm3",
            "34": "Scooter de plus de 125 cm3",
            "35": "Quad leger",
            "36": "Quad lourd",
            "37": "Autobus",
            "38": "Autocar",
            "39": "Train",
            "40": "Tramway",
            "41": "Trois roues motorise jusqu'a 50 cm3",
            "42": "Trois roues motorise de 50 a 125 cm3",
            "43": "Trois roues motorise de plus de 125 cm3",
            "50": "EDP a moteur",
            "60": "EDP sans moteur",
            "80": "Velo a assistance electrique",
            "99": "Autre vehicule"
        },
        "obs": {
            "-1": "Non renseigne", "0": "Sans objet",
            "1": "Vehicule en stationnement",
            "2": "Arbre",
            "3": "Glissiere metallique",
            "4": "Glissiere beton",
            "5": "Autre glissiere",
            "6": "Batiment mur ou pile de pont",
            "7": "Support de signalisation ou appel d'urgence",
            "8": "Poteau",
            "9": "Mobilier urbain",
            "10": "Parapet",
            "11": "Ilot refuge ou borne haute",
            "12": "Bordure de trottoir",
            "13": "Fosse talus ou paroi rocheuse",
            "14": "Autre obstacle fixe sur chaussee",
            "15": "Autre obstacle sur trottoir ou accotement",
            "16": "Sortie de chaussee sans obstacle",
            "17": "Buse ou tete d'aqueduc"
        },
        "obsm": {
            "-1": "Non renseigne", "0": "Aucun",
            "1": "Pieton", "2": "Vehicule",
            "4": "Vehicule sur rail",
            "5": "Animal domestique",
            "6": "Animal sauvage",
            "9": "Autre"
        },
        "choc": {
            "-1": "Non renseigne", "0": "Aucun",
            "1": "Avant", "2": "Avant droit",
            "3": "Avant gauche", "4": "Arriere",
            "5": "Arriere droit", "6": "Arriere gauche",
            "7": "Cote droit", "8": "Cote gauche",
            "9": "Chocs multiples"
        },
        "manv": {
            "-1": "Non renseigne",
            "0": "Inconnue",
            "1": "Sans changement de direction",
            "2": "Meme sens meme file",
            "3": "Entre deux files",
            "4": "Marche arriere",
            "5": "A contresens",
            "6": "Franchit le terre-plein central",
            "7": "Couloir bus meme sens",
            "8": "Couloir bus sens inverse",
            "9": "Insertion",
            "10": "Demi-tour",
            "11": "Change de file a gauche",
            "12": "Change de file a droite",
            "13": "Deport a gauche",
            "14": "Deport a droite",
            "15": "Tourne a gauche",
            "16": "Tourne a droite",
            "17": "Depasse a gauche",
            "18": "Depasse a droite",
            "19": "Traverse la chaussee",
            "20": "Stationnement en manoeuvre",
            "21": "Manoeuvre d'evitement",
            "22": "Ouverture de porte",
            "23": "Arrete hors stationnement",
            "24": "En stationnement avec occupants",
            "25": "Circule sur trottoir",
            "26": "Autres manoeuvres"
        },
        "motor": {
            "-1": "Non renseigne",
            "0": "Inconnue",
            "1": "Hydrocarbures",
            "2": "Hybride electrique",
            "3": "Electrique",
            "4": "Hydrogene",
            "5": "Humaine",
            "6": "Autre"
        }
    },

    "usagers": {
        "locp": {
            "-1": "Non renseigne",
            "0": "Sans objet",
            "1": "Chaussee a plus de 50 m du passage pieton",
            "2": "Chaussee a moins de 50 m du passage pieton",
            "3": "Passage pieton sans signalisation lumineuse",
            "4": "Passage pieton avec signalisation lumineuse",
            "5": "Sur trottoir",
            "6": "Sur accotement",
            "7": "Sur refuge ou bande d'arret d'urgence",
            "8": "Sur contre-allee",
            "9": "Inconnue"
        },
        "actp": {
            "-1": "Non renseigne",
            "0": "Non renseigne ou sans objet",
            "1": "Sens du vehicule heurtant",
            "2": "Sens inverse du vehicule",
            "3": "Traversant",
            "4": "Masque",
            "5": "Jouant ou courant",
            "6": "Avec animal",
            "9": "Autre",
            "A": "Monte ou descend du vehicule",
            "B": "Inconnue"
        }
    }
}

securite = {
    "-1": "Non renseigne",
    "0": "Aucun equipement",
    "1": "Ceinture",
    "2": "Casque",
    "3": "Dispositif enfants",
    "4": "Gilet reflechissant",
    "5": "Airbag deux ou trois roues",
    "6": "Gants deux ou trois roues",
    "7": "Gants et airbag deux ou trois roues",
    "8": "Non determinable",
    "9": "Autre"
}

for variable in ("secu1", "secu2", "secu3"):
    CODES["usagers"][variable] = securite

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
    famille = row["famille"]
    variable = row["variable"]
    original = row["code"].strip()

    # Exemple catv : 07 dans la notice, 7 dans les CSV
    code = original
    if famille == "vehicules" and variable == "catv":
        if code.isdigit():
            code = str(int(code))

    libelle = CODES.get(famille, {}).get(variable, {}).get(code)
    if libelle is None:
        continue

    ancien = row["libelle"].strip()

    if ancien and ancien != libelle:
        conflits.append({
            "famille": famille,
            "variable": variable,
            "code": original,
            "ancien": ancien,
            "propose": libelle
        })
        continue

    if not ancien:
        df.at[i, "libelle"] = libelle
        ajouts += 1

    df.at[i, "statut"] = "ONISR_DOCUMENTE"

    if "source" in df.columns:
        df.at[i, "source"] = "ONISR - Notice BAAC 21/10/2025"

df.to_csv(
    SORTIE, sep=";", index=False, encoding="utf-8-sig"
)

restants = df[df["libelle"].str.strip().eq("")].copy()

restants.to_csv(
    INCONNUS, sep=";", index=False, encoding="utf-8-sig"
)

pd.DataFrame(
    conflits,
    columns=["famille", "variable", "code", "ancien", "propose"]
).to_csv(
    CONFLITS, sep=";", index=False, encoding="utf-8-sig"
)

print("\n=== WP2-05 : BILAN GLOBAL ===")
print("Codes recenses :", len(df))
print("Nouveaux libelles :", ajouts)
print("Codes avec libelle :", int(df["libelle"].str.strip().ne("").sum()))
print("Codes restant a verifier :", len(restants))
print("Conflits :", len(conflits))
print("Referentiel :", SORTIE)
print("Codes non documentes :", INCONNUS)
print("Fichiers Silver inchanges.")
