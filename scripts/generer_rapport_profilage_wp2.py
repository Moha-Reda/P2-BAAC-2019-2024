from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "metadata"
OUT = META / "profilage"
OUT.mkdir(parents=True, exist_ok=True)

def lire(fichier):
    return pd.read_csv(
        fichier,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )

resume = lire(OUT / "profilage_brut_resume.csv")
colonnes = lire(OUT / "profilage_brut_colonnes.csv")
speciales = lire(OUT / "analyse_valeurs_speciales.csv")
relations = lire(META / "harmonisation" / "rapport_relations_baac.csv")
cles = lire(META / "harmonisation" / "rapport_cles_baac.csv")

resume["lignes"] = pd.to_numeric(resume["lignes"])
resume["doublons_exacts"] = pd.to_numeric(resume["doublons_exacts"])

colonnes["taux_manquant_pct"] = pd.to_numeric(
    colonnes["taux_manquant_pct"]
)
colonnes["valeurs_manquantes"] = pd.to_numeric(
    colonnes["valeurs_manquantes"]
)

bilan = (
    resume.groupby("famille", as_index=False)
    .agg(
        lignes=("lignes", "sum"),
        doublons_exacts=("doublons_exacts", "sum"),
        fichiers=("annee", "count")
    )
)

anomalies = colonnes[
    colonnes["taux_manquant_pct"] >= 50
].sort_values(
    "taux_manquant_pct", ascending=False
)

anomalies.to_csv(
    OUT / "colonnes_forte_incompletude.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

total = int(resume["lignes"].sum())
doublons = int(resume["doublons_exacts"].sum())

lignes = [
    "# WP2 - Rapport de profilage initial BAAC",
    "",
    "## 1. Perimetre",
    "- Periode : 2019-2024",
    f"- Fichiers RAW analyses : {len(resume)}",
    f"- Lignes analysees : {total}",
    "- Familles : caracteristiques, lieux, vehicules, usagers",
    "",
    "## 2. Volumes par famille",
]

for r in bilan.itertuples():
    lignes.append(
        f"- {r.famille} : {r.lignes} lignes, "
        f"{r.fichiers} fichiers, {r.doublons_exacts} "
        "doublons exacts supplementaires"
    )

lignes += [
    "",
    "## 3. Qualite initiale",
    f"- Doublons exacts supplementaires : {doublons}",
    f"- Combinaisons annee/colonne avec >= 50 % "
    f"de marqueurs manquants : {len(anomalies)}",
    "- Attention : les codes metier -1 et 0 ne sont "
    "pas automatiquement des valeurs manquantes.",
    "- Les repetitions ne sont pas supprimees.",
    "",
    "## 4. Particularites documentees",
    "- Caracteristiques 2022 : Accident_Id renomme "
    "Num_Acc dans Silver.",
    "- Usagers 2019-2020 : id_usager absent de la source.",
    "- Lieux 2023-2024 : plusieurs lignes par accident.",
    "- Usagers 2019-2020 : 164 doublons exacts "
    "supplementaires signales.",
    "- Valeurs speciales : vide, N/A, null et -1 "
    "selon les variables et annees.",
    "",
    "## 5. Controles",
    f"- Controles de relations reportes : {len(relations)}",
    f"- Controles de cles reportes : {len(cles)}",
    "- Voir les rapports CSV pour les valeurs exactes.",
    "",
    "## 6. Codifications",
    "- 64 entrees famille-variable documentees.",
    "- 284 codes distincts avec libelles proposes.",
    "- 7 reserves explicites a confirmer.",
    "- Revue officielle des correspondances encore necessaire.",
    "",
    "## 7. Limites et decisions",
    "- Aucune suppression de donnees a cette etape.",
    "- Nettoyage non commence.",
    "- Les besoins des autres WP restent a confirmer.",
    "- Les taux de valeurs manquantes sont issus "
    "du profilage technique initial.",
    "",
    "## 8. Fichiers de preuve",
    "- metadata/profilage/",
    "- metadata/harmonisation/",
    "- metadata/codifications/",
    "- metadata/nettoyage/registre_regles.csv",
]

rapport = OUT / "rapport_profilage_initial.md"
rapport.write_text("\n".join(lignes) + "\n", encoding="utf-8")

print("=== BILAN WP2-04 ===")
print("Fichiers RAW analyses :", len(resume))
print("Total lignes :", total)
print("Doublons exacts supplementaires :", doublons)
print("Champs annee/variable >= 50 % manquants :", len(anomalies))
print("Rapport :", rapport)
print("Anomalies :", OUT / "colonnes_forte_incompletude.csv")
print("Aucune donnee RAW ou Silver modifiee.")
