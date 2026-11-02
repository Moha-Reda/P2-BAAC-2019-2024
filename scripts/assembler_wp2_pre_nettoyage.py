from pathlib import Path
from datetime import datetime
import shutil
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "livraisons" / "v0_1_pre_nettoyage"
META = ROOT / "metadata"

sources = [
    ROOT / "data" / "silver",
    META / "harmonisation",
    META / "profilage",
    META / "codifications",
    META / "nettoyage",
    META / "qualite",
    ROOT / "scripts",
]

for source in sources:
    if not source.exists():
        raise FileNotFoundError(f"Source manquante : {source}")

if DEST.exists():
    raise FileExistsError(
        f"Dossier deja existant : {DEST}. "
        "Aucun ecrasement automatique."
    )

DEST.mkdir(parents=True)

for source in sources:
    if source.name == "silver":
        cible = DEST / "data" / "silver"
    elif source.name == "scripts":
        cible = DEST / "scripts"
    else:
        cible = DEST / "metadata" / source.name

    cible.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        cible,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )

readme = """# WP2 - BAAC 2019-2024

## Version pre-nettoyage v0.1

Statut : package de travail prepare, non encore livre ni valide.

## Objectif
Collecter, profiler, harmoniser et documenter les donnees
BAAC 2019-2024 avant les operations de nettoyage.

## Donnees
- 24 fichiers RAW sources
- 4 tables Silver harmonisees
- 1 992 145 lignes conservees
- CSV UTF-8-SIG, separateur point-virgule

## Harmonisations
- Accident_Id vers Num_Acc en 2022
- id_usager ajoute vide pour 2019-2020
- Normalisation des separateurs decimaux lat/long
- Ajout de la colonne annee

## Controles
- 12 tests structurels reussis
- 58 controles metier executes sans anomalie detectee
- 164 doublons exacts supplementaires identifies en 2019-2020
- Multiplicite des lieux en 2023-2024 preservee

## Documentation
- 64 entrees famille-variable avec definition
- 284 codes avec libelles proposes
- 7 reserves explicites sur les derniers codes
- Verification exhaustive des correspondances metier non achevee
- 8 regles de nettoyage preparees

## Restrictions
Aucune suppression ni nettoyage applique.
Les donnees RAW originales ne sont pas dans ce dossier.
Les besoins des autres WP et le contrat d'interface
WP2 vers WP3 restent a confirmer.

## Arborescence
- data/silver : tables harmonisees
- metadata/profilage : analyses de qualite
- metadata/harmonisation : controles et rapports
- metadata/codifications : dictionnaires et modalites
- metadata/nettoyage : regles a valider
- metadata/qualite : tests automatiques
- scripts : scripts Python reutilisables
"""

(DEST / "README.md").write_text(readme, encoding="utf-8")

inventaire = []
for fichier in DEST.rglob("*"):
    if fichier.is_file():
        inventaire.append({
            "chemin": fichier.relative_to(DEST).as_posix(),
            "taille_octets": fichier.stat().st_size
        })

pd.DataFrame(inventaire).to_csv(
    DEST / "inventaire_livraison.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("=== WP2 : PACKAGE PRE-NETTOYAGE ===")
print("Fichiers regroupes :", len(inventaire))
print("README : OK")
print("Inventaire : OK")
print("Dossier :", DEST)
print("Statut : PREPARE, NON ENCORE VALIDE")
print("RAW et Silver originaux inchanges.")
