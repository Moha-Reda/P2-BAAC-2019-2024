from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
OUT = ROOT / "metadata" / "qualite"
OUT.mkdir(parents=True, exist_ok=True)

ATTENDUS = {
    "caracteristiques": 327628,
    "lieux": 359512,
    "vehicules": 559847,
    "usagers": 745158
}

tables = {}
tests = []
volumes = []

def enregistrer(nom, resultat, detail):
    tests.append({
        "test": nom,
        "statut": "OK" if resultat else "ECHEC",
        "detail": str(detail)
    })
    print(f"[{'OK' if resultat else 'ECHEC'}] {nom} : {detail}")

print("=== WP2 : TESTS AVANT NETTOYAGE ===")

# Chargement des fichiers et controle des volumes
for famille, attendu in ATTENDUS.items():
    chemin = SILVER / f"{famille}_2019_2024.csv"

    df = pd.read_csv(
        chemin,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )

    tables[famille] = df

    enregistrer(
        f"volume_{famille}",
        len(df) == attendu,
        f"{len(df)} lignes / {attendu} attendues"
    )

    for annee, groupe in df.groupby("annee"):
        volumes.append({
            "famille": famille,
            "annee": annee,
            "lignes_avant_nettoyage": len(groupe),
            "doublons_exacts": int(groupe.duplicated().sum())
        })

# Unicite des identifiants principaux
carac = tables["caracteristiques"]
veh = tables["vehicules"]
usagers = tables["usagers"]
lieux = tables["lieux"]

enregistrer(
    "unicite_accidents",
    not carac["Num_Acc"].duplicated().any(),
    "Num_Acc dans caracteristiques"
)

enregistrer(
    "unicite_vehicules",
    not veh.duplicated(["Num_Acc", "id_vehicule"]).any(),
    "Num_Acc + id_vehicule dans vehicules"
)

# Integrite referentielle
ids_accidents = set(carac["Num_Acc"])

for famille in ["lieux", "vehicules", "usagers"]:
    df = tables[famille]
    absents = int((~df["Num_Acc"].isin(ids_accidents)).sum())

    enregistrer(
        f"references_accidents_{famille}",
        absents == 0,
        f"{absents} lignes sans accident correspondant"
    )

cles_veh = pd.MultiIndex.from_frame(
    veh[["Num_Acc", "id_vehicule"]]
)

cles_usagers = pd.MultiIndex.from_frame(
    usagers[["Num_Acc", "id_vehicule"]]
)

sans_vehicule = int((~cles_usagers.isin(cles_veh)).sum())

enregistrer(
    "references_usagers_vehicules",
    sans_vehicule == 0,
    f"{sans_vehicule} usagers sans vehicule correspondant"
)

# Caracteristiques specifiques du perimetre BAAC
anciens = usagers[usagers["annee"].isin(["2019", "2020"])]

enregistrer(
    "id_usager_2019_2020",
    anciens["id_usager"].eq("").all(),
    "Identifiants absents conserves vides"
)

enregistrer(
    "annees_couvertes",
    all(
        sorted(df["annee"].unique().tolist())
        == [str(a) for a in range(2019, 2025)]
        for df in tables.values()
    ),
    "2019 a 2024 dans chaque table"
)

# Export des rapports
pd.DataFrame(tests).to_csv(
    OUT / "tests_avant_nettoyage.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(volumes).to_csv(
    OUT / "reference_volumes_avant_nettoyage.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

echecs = sum(t["statut"] == "ECHEC" for t in tests)

print("\n=== BILAN QUALITE ===")
print("Tests executes :", len(tests))
print("Tests reussis :", len(tests) - echecs)
print("Tests en echec :", echecs)
print("Rapports :", OUT)
print("Aucune donnee modifiee.")

if echecs:
    raise SystemExit(1)
