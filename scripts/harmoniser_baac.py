
from pathlib import Path
import pandas as pd
import csv

# ============================================
# WP2 - HARMONISATION BAAC 2019-2024
# ============================================

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SILVER = ROOT / "data" / "silver"
METADATA = ROOT / "metadata" / "harmonisation"

ANNEES = range(2019, 2025)

FAMILLES = [
    "caracteristiques",
    "lieux",
    "vehicules",
    "usagers",
]

SILVER.mkdir(parents=True, exist_ok=True)
METADATA.mkdir(parents=True, exist_ok=True)

rapport = []
resultats = {}

# ============================================
# 1. LECTURE DES FICHIERS
# ============================================

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


# ============================================
# 2. HARMONISATION
# ============================================

def harmoniser(df, famille, annee):

    df = df.copy()

    # Normalisation de l'identifiant accident
    if famille == "caracteristiques" and annee == 2022:
        if "Accident_Id" not in df.columns:
            raise ValueError("Accident_Id absent en 2022")

        df = df.rename(
            columns={"Accident_Id": "Num_Acc"}
        )

    if "Num_Acc" not in df.columns:
        raise ValueError(
            f"Num_Acc absent : {famille} {annee}"
        )

    # id_usager absent avant 2021
    if famille == "usagers":
        if "id_usager" not in df.columns:
            if annee >= 2021:
                raise ValueError(
                    f"id_usager absent en {annee}"
                )
            df["id_usager"] = ""

    # Normalisation des coordonnées
    if famille == "caracteristiques":
        for colonne in ["lat", "long"]:
            if colonne not in df.columns:
                raise ValueError(
                    f"Colonne absente : {colonne}"
                )

            df[colonne] = (
                df[colonne]
                .str.strip()
                .str.replace(",", ".", regex=False)
            )

    # Ajout de l'année de provenance
    df["annee"] = str(annee)

    return df


# ============================================
# 3. TRAITEMENT DES 24 FICHIERS
# ============================================

for famille in FAMILLES:

    print(f"\n===== {famille.upper()} =====")

    fichiers = []
    colonnes_reference = None

    for annee in ANNEES:

        chemin = (
            RAW / str(annee) /
            f"{famille}_{annee}.csv"
        )

        if not chemin.exists():
            raise FileNotFoundError(chemin)

        df_brut = lire_csv(chemin)
        nb_avant = len(df_brut)

        df = harmoniser(
            df_brut, famille, annee
        )

        nb_apres = len(df)

        if nb_avant != nb_apres:
            raise ValueError(
                f"Perte de lignes : {famille} {annee}"
            )

        # Contrôle des colonnes entre années
        if colonnes_reference is None:
            colonnes_reference = list(df.columns)
        else:
            if set(df.columns) != set(colonnes_reference):
                raise ValueError(
                    f"Schéma incompatible : {famille} {annee}"
                )

            df = df.reindex(
                columns=colonnes_reference
            )

        fichiers.append(df)

        rapport.append({
            "famille": famille,
            "annee": annee,
            "lignes_avant": nb_avant,
            "lignes_apres": nb_apres,
            "difference": nb_apres - nb_avant,
            "colonnes": len(df.columns)
        })

        print(
            f"{annee} : {nb_apres:,} lignes "
            f"| {len(df.columns)} colonnes"
        )

    # Assemblage des six années
    resultat = pd.concat(
        fichiers,
        ignore_index=True
    )

    resultats[famille] = resultat


# ============================================
# 4. EXPORT DES FICHIERS SILVER
# ============================================

# On n'écrit les fichiers qu'après validation
# des schémas et comptages des 24 entrées.

for famille, resultat in resultats.items():

    destination = (
        SILVER / f"{famille}_2019_2024.csv"
    )

    resultat.to_csv(
        destination,
        sep=";",
        index=False,
        encoding="utf-8-sig",
        quoting=csv.QUOTE_MINIMAL
    )

    print(
        f"\n[EXPORT] {destination.name} : "
        f"{len(resultat):,} lignes"
    )


# ============================================
# 5. RAPPORT DE CONTRÔLE
# ============================================

df_rapport = pd.DataFrame(rapport)

df_rapport.to_csv(
    METADATA / "rapport_harmonisation.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\n====================================")
print("HARMONISATION TERMINÉE")
print("====================================")

print("Fichiers générés :", len(resultats))
print("Lignes avant :", df_rapport["lignes_avant"].sum())
print("Lignes après :", df_rapport["lignes_apres"].sum())

print(
    "Différence totale :",
    df_rapport["difference"].sum()
)

print("\nDossier de sortie :", SILVER)
