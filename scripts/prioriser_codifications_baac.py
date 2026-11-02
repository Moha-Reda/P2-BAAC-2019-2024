from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DOSSIER = ROOT / "metadata" / "codifications"

source = DOSSIER / "modalites_uniques_enrichies.csv"

df = pd.read_csv(
    source,
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig"
)

df["effectif_total"] = pd.to_numeric(df["effectif_total"])

# Codes avec libelle mais validation encore necessaire
df["validation_metier"] = "A_CONFIRMER_NOTICE"

# Les codes sans libelle sont prioritaires
inconnus = df[df["libelle"].str.strip().eq("")].copy()

inconnus = inconnus.sort_values(
    "effectif_total",
    ascending=False
)

inconnus["priorite"] = [
    "P1" if i < 40 else "P2" if i < 100 else "P3"
    for i in range(len(inconnus))
]

# Synthese par variable
resume = (
    df.assign(
        documente=df["libelle"].str.strip().ne("")
    )
    .groupby(["famille", "variable"], as_index=False)
    .agg(
        codes_total=("code", "size"),
        codes_documentes=("documente", "sum"),
        occurrences_totales=("effectif_total", "sum")
    )
)

occurrences_documentees = (
    df[df["libelle"].str.strip().ne("")]
    .groupby(["famille", "variable"])["effectif_total"]
    .sum()
)

resume["occurrences_documentees"] = [
    int(occurrences_documentees.get(
        (r.famille, r.variable), 0
    ))
    for r in resume.itertuples()
]

resume["couverture_pct"] = (
    resume["occurrences_documentees"]
    / resume["occurrences_totales"] * 100
).round(2)

inconnus.to_csv(
    DOSSIER / "codes_prioritaires_a_verifier.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

resume.to_csv(
    DOSSIER / "couverture_codifications.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("=== WP2-05 : PRIORISATION ===")
print("Codes sans libelle :", len(inconnus))
print("Codes P1 :", (inconnus["priorite"] == "P1").sum())
print("Codes P2 :", (inconnus["priorite"] == "P2").sum())
print("Codes P3 :", (inconnus["priorite"] == "P3").sum())

print("\n=== TOP 25 A VERIFIER ===")
print(
    inconnus[
        ["famille", "variable", "code",
         "effectif_total", "priorite"]
    ].head(25).to_string(index=False)
)

print("\n=== COUVERTURE PAR VARIABLE ===")
print(
    resume.sort_values("couverture_pct")[
        ["famille", "variable", "codes_total",
         "codes_documentes", "couverture_pct"]
    ].to_string(index=False)
)

print("\nRapports enregistres.")
print("Aucune donnee Silver modifiee.")
