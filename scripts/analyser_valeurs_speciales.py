
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "metadata" / "profilage"

VARIABLES = {
    "lieux": ["lartpc", "larrout", "v2"],
    "vehicules": ["occutc"]
}

resultats = []

for annee in range(2019, 2025):
    for famille, colonnes in VARIABLES.items():
        chemin = RAW / str(annee) / f"{famille}_{annee}.csv"

        try:
            df = pd.read_csv(
                chemin,
                sep=";",
                dtype=str,
                encoding="utf-8-sig",
                keep_default_na=False
            )
        except UnicodeDecodeError:
            df = pd.read_csv(
                chemin,
                sep=";",
                dtype=str,
                encoding="cp1252",
                keep_default_na=False
            )

        for colonne in colonnes:
            valeurs = df[colonne].astype(str).str.strip()
            normalisees = valeurs.str.lower()

            resultats.append({
                "annee": annee,
                "famille": famille,
                "colonne": colonne,
                "total_lignes": len(df),
                "vides": int(valeurs.eq("").sum()),
                "n_a": int(normalisees.eq("n/a").sum()),
                "null": int(normalisees.eq("null").sum()),
                "moins_1": int(valeurs.eq("-1").sum()),
                "zero": int(valeurs.eq("0").sum()),
                "autres_valeurs": int(
                    (~normalisees.isin(
                        ["", "n/a", "null", "-1", "0"]
                    )).sum()
                )
            })

rapport = pd.DataFrame(resultats)

OUTPUT.mkdir(parents=True, exist_ok=True)

destination = OUTPUT / "analyse_valeurs_speciales.csv"

rapport.to_csv(
    destination,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\n=== ANALYSE DES VALEURS SPÉCIALES ===")
print(rapport.to_string(index=False))
print(f"\nRapport enregistré : {destination}")
