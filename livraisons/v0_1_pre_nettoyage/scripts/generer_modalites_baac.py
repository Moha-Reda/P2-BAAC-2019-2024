from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
OUT = ROOT / "metadata" / "codifications"
OUT.mkdir(parents=True, exist_ok=True)

variables = {
    "caracteristiques": ["lum", "agg", "int", "atm", "col"],
    "lieux": ["catr", "circ", "vosp", "prof", "plan", "surf", "infra", "situ"],
    "vehicules": ["senc", "catv", "obs", "obsm", "choc", "manv", "motor"],
    "usagers": ["catu", "grav", "sexe", "trajet", "secu1", "secu2", "secu3", "locp", "actp", "etatp"]
}

# Libelles confirmes dans la notice ONISR
libelles = {
    ("usagers", "grav", "1"): "Indemne",
    ("usagers", "grav", "2"): "Tue",
    ("usagers", "grav", "3"): "Blesse hospitalise",
    ("usagers", "grav", "4"): "Blesse leger",
    ("usagers", "catu", "1"): "Conducteur",
    ("usagers", "catu", "2"): "Passager",
    ("usagers", "catu", "3"): "Pieton",
    ("usagers", "sexe", "1"): "Masculin",
    ("usagers", "sexe", "2"): "Feminin"
}

resultats = []

for famille, colonnes in variables.items():
    fichier = SILVER / f"{famille}_2019_2024.csv"

    df = pd.read_csv(
        fichier, sep=";", dtype=str,
        keep_default_na=False, encoding="utf-8-sig"
    )

    for colonne in colonnes:
        if colonne not in df.columns:
            raise ValueError(f"Colonne absente : {famille}.{colonne}")

        compte = (
            df.groupby(["annee", colonne], dropna=False)
            .size()
            .reset_index(name="effectif")
        )

        for _, ligne in compte.iterrows():
            code = str(ligne[colonne]).strip()
            cle = (famille, colonne, code)
            libelle = libelles.get(cle, "")

            resultats.append({
                "famille": famille,
                "variable": colonne,
                "annee": ligne["annee"],
                "code": code,
                "libelle": libelle,
                "effectif": int(ligne["effectif"]),
                "statut": "LIBELLE_DOCUMENTE" if libelle else "A_VERIFIER"
            })

    print(f"[OK] {famille} : {len(colonnes)} variables analysees")

rapport = pd.DataFrame(resultats)
destination = OUT / "referentiel_modalites_baac.csv"

rapport.to_csv(
    destination, sep=";", index=False, encoding="utf-8-sig"
)

print("\n=== BILAN MODALITES BAAC ===")
print("Variables analysees :", sum(map(len, variables.values())))
print("Combinaisons annee/code :", len(rapport))
print("Codes distincts par variable :",
      rapport[["famille", "variable", "code"]].drop_duplicates().shape[0])
print("Libelles documentes :", rapport["libelle"].ne("").sum())
print("Combinaisons a verifier :", rapport["libelle"].eq("").sum())
print("Rapport :", destination)
print("\nAUCUNE DONNEE SILVER MODIFIEE")
