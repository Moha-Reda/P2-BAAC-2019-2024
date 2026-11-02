from pathlib import Path
import shutil
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DOSSIER = ROOT / "metadata" / "codifications"

SOURCE = DOSSIER / "modalites_baac_finalisees.csv"
BACKUP = DOSSIER / "modalites_baac_avant_validation_finale.csv"
SORTIE = DOSSIER / "modalites_baac_finalisees.csv"
RESERVES = DOSSIER / "codifications_a_confirmer.csv"

df = pd.read_csv(
    SOURCE, sep=";", dtype=str,
    keep_default_na=False, encoding="utf-8-sig"
)

if not BACKUP.exists():
    shutil.copy2(SOURCE, BACKUP)

corrections = {
    ("caracteristiques", "int", "-1"):
        ("Non renseigne presume", "A_CONFIRMER"),
    ("caracteristiques", "lum", "-1"):
        ("Non renseigne presume", "A_CONFIRMER"),
    ("usagers", "grav", "-1"):
        ("Non renseigne presume", "A_CONFIRMER"),
    ("usagers", "sexe", "-1"):
        ("Non renseigne presume", "A_CONFIRMER"),
    ("vehicules", "catv", "-1"):
        ("Non renseigne presume", "A_CONFIRMER"),
    ("usagers", "actp", "7"):
        ("Quitte l'arret du transport collectif",
         "HISTORIQUE_A_CONFIRMER"),
    ("usagers", "actp", "8"):
        ("Accede a l'arret du transport collectif",
         "HISTORIQUE_A_CONFIRMER")
}

ajouts = 0

for i, row in df.iterrows():
    cle = (
        row["famille"],
        row["variable"],
        row["code"].strip()
    )

    if cle not in corrections:
        continue

    libelle, statut = corrections[cle]

    if row["libelle"].strip():
        raise ValueError(f"Libelle deja present : {cle}")

    df.at[i, "libelle"] = libelle
    df.at[i, "statut"] = statut
    ajouts += 1

if "source" not in df.columns:
    df["source"] = ""

for i, row in df.iterrows():
    if row["statut"] == "HISTORIQUE_A_CONFIRMER":
        df.at[i, "source"] = "Guide BAAC 2017"
    elif row["statut"] == "A_CONFIRMER":
        df.at[i, "source"] = "Interpretation provisoire"

reservations = df[
    df["statut"].isin([
        "A_CONFIRMER",
        "HISTORIQUE_A_CONFIRMER"
    ])
].copy()

reservations.to_csv(
    RESERVES, sep=";", index=False, encoding="utf-8-sig"
)

df.to_csv(
    SORTIE, sep=";", index=False, encoding="utf-8-sig"
)

print("=== BILAN WP2-05 ===")
print("Codes recenses :", len(df))
print("Nouveaux libelles :", ajouts)
print("Codes avec libelle :", df["libelle"].str.strip().ne("").sum())
print("Sans libelle :", df["libelle"].str.strip().eq("").sum())
print("Reserves nouvelles :", len(reservations))
print("Rapport des reserves :", RESERVES)
print("Fichiers Silver inchanges.")
