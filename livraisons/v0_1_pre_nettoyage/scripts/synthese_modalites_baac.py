from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DOSSIER = ROOT / "metadata" / "codifications"

SOURCE = DOSSIER / "referentiel_modalites_baac.csv"

df = pd.read_csv(
    SOURCE,
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig"
)

df["effectif"] = pd.to_numeric(df["effectif"], errors="raise")

# Une ligne par famille + variable + code, toutes annees confondues
codes = (
    df.groupby(
        ["famille", "variable", "code"],
        as_index=False,
        dropna=False
    )
    .agg(
        effectif_total=("effectif", "sum"),
        annees_presentes=("annee", "nunique"),
        libelle=("libelle", "first")
    )
)

# Reconnaitre uniquement les marqueurs textuels explicites.
# Ne pas classifier automatiquement 0 ou -1.
marqueurs = {"", "n/a", "na", "null", "nan"}

codes["type"] = codes["code"].str.strip().str.lower().apply(
    lambda x: "MARQUEUR_TEXTUEL" if x in marqueurs
    else "CODE_A_INTERPRETER"
)

codes["statut"] = codes["libelle"].apply(
    lambda x: "LIBELLE_DOCUMENTE" if x.strip()
    else "A_VERIFIER"
)

codes = codes.sort_values(
    ["famille", "variable", "effectif_total"],
    ascending=[True, True, False]
)

destination = DOSSIER / "modalites_uniques_a_documenter.csv"

codes.to_csv(
    destination,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("=== SYNTHESE WP2-05 ===")
print("Codes famille-variable :", len(codes))
print("Codes avec libelle :", codes["libelle"].ne("").sum())
print("Codes sans libelle :", codes["libelle"].eq("").sum())
print("Marqueurs textuels :", (codes["type"] == "MARQUEUR_TEXTUEL").sum())

print("\n=== REPARTITION PAR FAMILLE ===")
print(codes.groupby("famille").size().to_string())

print("\n=== TOP 20 DES CODES SANS LIBELLE ===")
non_documentes = codes[
    (codes["libelle"] == "") &
    (codes["type"] == "CODE_A_INTERPRETER")
]

print(
    non_documentes.nlargest(20, "effectif_total")[
        ["famille", "variable", "code", "effectif_total"]
    ].to_string(index=False)
)

print("\nFichier cree :", destination)
print("Fichiers Silver inchanges.")
