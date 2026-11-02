from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
OUT = ROOT / "metadata" / "qualite"
OUT.mkdir(parents=True, exist_ok=True)

def lire(famille):
    return pd.read_csv(
        SILVER / f"{famille}_2019_2024.csv",
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )

carac = lire("caracteristiques")
usagers = lire("usagers")

resultats = []

def ajouter(controle, annee, total, anomalies, remarque):
    resultats.append({
        "controle": controle,
        "annee": annee,
        "lignes_controlees": total,
        "anomalies_potentielles": anomalies,
        "remarque": remarque
    })

for annee, df in carac.groupby("annee"):
    mois = pd.to_numeric(df["mois"], errors="coerce")
    jour = pd.to_numeric(df["jour"], errors="coerce")

    mois_invalides = int((mois.isna() | ~mois.between(1, 12)).sum())
    jour_invalides = int((jour.isna() | ~jour.between(1, 31)).sum())

    ajouter("mois_invalide", annee, len(df), mois_invalides,
            "Mois absent ou hors de 1 a 12")
    ajouter("jour_invalide", annee, len(df), jour_invalides,
            "Jour absent ou hors de 1 a 31")

    dates = pd.to_datetime(
        dict(
            year=pd.to_numeric(df["annee"], errors="coerce"),
            month=mois,
            day=jour
        ),
        errors="coerce"
    )

    ajouter("date_calendaire_invalide", annee, len(df),
            int(dates.isna().sum()),
            "Date impossible ou incomplete")

    for colonne, minimum, maximum in [
        ("lat", -90, 90),
        ("long", -180, 180)
    ]:
        valeurs = df[colonne].str.strip()
        numeriques = pd.to_numeric(
            valeurs.str.replace(",", ".", regex=False),
            errors="coerce"
        )

        absentes = int(valeurs.eq("").sum())
        non_numeriques = int(
            (valeurs.ne("") & numeriques.isna()).sum()
        )
        hors_limites = int(
            (numeriques.notna()
             & ~numeriques.between(minimum, maximum)).sum()
        )

        ajouter(f"{colonne}_absente", annee, len(df),
                absentes, "Coordonnee vide")
        ajouter(f"{colonne}_non_numerique", annee, len(df),
                non_numeriques, "Conversion numerique impossible")
        ajouter(f"{colonne}_hors_limites", annee, len(df),
                hors_limites, "Coordonnee hors limites geographiques")

for annee, df in usagers.groupby("annee"):
    if int(annee) >= 2021:
        vides = int(df["id_usager"].str.strip().eq("").sum())
        ajouter("id_usager_vide", annee, len(df), vides,
                "Identifiant absent alors que la colonne existe")

rapport = pd.DataFrame(resultats)

destination = OUT / "controle_metier_avant_nettoyage.csv"

rapport.to_csv(
    destination,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("=== WP2 : CONTROLES METIER AVANT NETTOYAGE ===")
print("Controles effectues :", len(rapport))
print("\nBilan par controle :")
print(
    rapport.groupby("controle")["anomalies_potentielles"]
    .sum().to_string()
)
print("\nRapport :", destination)
print("RAW et Silver inchanges.")
