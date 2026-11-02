
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
META = ROOT / "metadata" / "codifications"

META.mkdir(parents=True, exist_ok=True)

familles = [
    "caracteristiques",
    "lieux",
    "vehicules",
    "usagers"
]

reference = pd.read_csv(
    META / "referentiel_baac.csv",
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig"
)

definitions = {
    (row["famille"], row["variable"]): row
    for _, row in reference.iterrows()
}

resultats = []

for famille in familles:
    chemin = SILVER / f"{famille}_2019_2024.csv"

    df = pd.read_csv(
        chemin,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )

    for colonne in df.columns:
        valeurs = df[colonne].astype(str).str.strip()
        normalisees = valeurs.str.lower()

        marqueurs = normalisees.isin(
            ["", "n/a", "na", "null", "nan"]
        )

        definition = definitions.get((famille, colonne), {})

        exemples = valeurs[
            ~marqueurs
        ].drop_duplicates().head(5).tolist()

        resultats.append({
            "famille": famille,
            "variable": colonne,
            "definition": definition.get("definition", ""),
            "unite": definition.get("unite", ""),
            "lignes": len(df),
            "valeurs_distinctes": int(valeurs.nunique()),
            "valeurs_vides": int(valeurs.eq("").sum()),
            "marqueurs_textuels": int(
                (marqueurs & valeurs.ne("")).sum()
            ),
            "valeurs_moins_1": int(valeurs.eq("-1").sum()),
            "exemples": " | ".join(exemples),
            "regle_provisoire": definition.get(
                "regle_provisoire", ""
            ),
            "statut": definition.get(
                "statut", "A_DOCUMENTER"
            )
        })

    print(
        f"[OK] {famille} : "
        f"{len(df.columns)} colonnes documentées techniquement"
    )

dictionnaire = pd.DataFrame(resultats)

destination = META / "dictionnaire_baac_complet.csv"

dictionnaire.to_csv(
    destination,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\n===== DICTIONNAIRE BAAC =====")
print("Variables recensées :", len(dictionnaire))
print(
    "Variables à documenter :",
    (dictionnaire["statut"] == "A_DOCUMENTER").sum()
)
print("Fichier :", destination)
