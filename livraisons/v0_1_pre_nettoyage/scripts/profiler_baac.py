
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "metadata" / "profilage"

REPORT.mkdir(parents=True, exist_ok=True)

FAMILLES = [
    "caracteristiques", "lieux", "vehicules", "usagers"
]

ANNEES = range(2019, 2025)

resume = []
details = []

def lire_csv(chemin):
    for encodage in ["utf-8-sig", "cp1252"]:
        try:
            return pd.read_csv(
                chemin,
                sep=";",
                dtype=str,
                encoding=encodage,
                keep_default_na=False,
                on_bad_lines="error"
            )
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Encodage non reconnu : {chemin}")

for annee in ANNEES:
    for famille in FAMILLES:
        fichier = RAW / str(annee) / f"{famille}_{annee}.csv"
        df = lire_csv(fichier)

        n = len(df)
        doublons = int(df.duplicated().sum())

        resume.append({
            "annee": annee,
            "famille": famille,
            "lignes": n,
            "colonnes": len(df.columns),
            "doublons_exacts": doublons
        })

        for col in df.columns:
            valeurs = df[col].astype(str).str.strip()

            # Règle provisoire : distinguer les champs vides
            # et quelques marqueurs textuels explicites.
            manquants = valeurs.str.lower().isin(
                ["", "n/a", "na", "null", "nan"]
            )

            nb_manquants = int(manquants.sum())

            details.append({
                "annee": annee,
                "famille": famille,
                "colonne": col,
                "lignes": n,
                "valeurs_manquantes": nb_manquants,
                "taux_manquant_pct": round(
                    nb_manquants / n * 100, 2
                ) if n else 0,
                "valeurs_distinctes": int(valeurs.nunique()),
                "colonne_entierement_vide": nb_manquants == n
            })

        print(
            f"[OK] {annee} | {famille} | "
            f"{n:,} lignes | {len(df.columns)} colonnes | "
            f"{doublons} doublons exacts"
        )

pd.DataFrame(resume).to_csv(
    REPORT / "profilage_brut_resume.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(details).to_csv(
    REPORT / "profilage_brut_colonnes.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nPROFILAGE INITIAL TERMINÉ")
print("Fichiers analysés :", len(resume))
print("Rapports disponibles dans :", REPORT)
