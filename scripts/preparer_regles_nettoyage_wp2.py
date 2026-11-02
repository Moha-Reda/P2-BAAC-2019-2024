from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DOSSIER = ROOT / "metadata" / "nettoyage"
SOURCE = DOSSIER / "registre_regles.csv"
SORTIE = DOSSIER / "plan_nettoyage_a_valider.csv"

regles = pd.read_csv(
    SOURCE,
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig"
)

precisions = {
    "R001": (
        "Renommage deja effectue dans Silver",
        "Verifier presence de Num_Acc et absence de Accident_Id",
        "Aucune suppression",
        "DEJA_APPLIQUE"
    ),
    "R002": (
        "Conserver id_usager vide pour 2019-2020",
        "Verifier colonne presente et valeurs vides sur ces annees",
        "Ne jamais generer de faux identifiants metier",
        "DEJA_APPLIQUE"
    ),
    "R003": (
        "Identifier les -1 de larrout sans modification",
        "Comparer les valeurs et la documentation par annee",
        "Pas de remplacement avant validation",
        "A_ARBITRER"
    ),
    "R004": (
        "Recenser les marqueurs vide N/A et null de v2",
        "Verifier les occurrences par annee",
        "Conserver les valeurs originales dans RAW",
        "A_ARBITRER"
    ),
    "R005": (
        "Conserver lartpc et documenter la completude",
        "Mesurer le taux de remplissage par annee",
        "Ne pas supprimer la colonne",
        "A_CONFIRMER"
    ),
    "R006": (
        "Conserver occutc et analyser son applicabilite",
        "Comparer les valeurs aux categories de vehicules",
        "Ne pas imputer automatiquement",
        "A_CONFIRMER"
    ),
    "R007": (
        "Conserver et signaler les repetitions usagers",
        "Reverifier les 164 doublons supplementaires",
        "Aucune suppression automatique",
        "A_ARBITRER"
    ),
    "R008": (
        "Preserver plusieurs lieux pour un accident",
        "Verifier cardinalite et avertir des risques de jointure",
        "Aucune deduplication sur Num_Acc seul",
        "A_CONFIRMER"
    )
}

manquants = set(regles["id"]) - set(precisions)
if manquants:
    raise ValueError(f"Regles sans precision : {sorted(manquants)}")

lignes = []

for _, r in regles.iterrows():
    action, test, precaution, decision = precisions[r["id"]]

    lignes.append({
        "id": r["id"],
        "famille": r["famille"],
        "variable": r["variable"],
        "annees": r["annees"],
        "probleme": r["probleme"],
        "action_prevue": action,
        "test_acceptation": test,
        "precaution": precaution,
        "decision": decision,
        "statut_initial": r["statut"]
    })

plan = pd.DataFrame(lignes)

if SORTIE.exists():
    raise FileExistsError(
        f"{SORTIE} existe deja : aucun ecrasement automatique"
    )

plan.to_csv(
    SORTIE,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("=== WP2-07 : PLAN DE NETTOYAGE ===")
print("Regles preparees :", len(plan))
print("\nRepartition :")
print(plan["decision"].value_counts().to_string())
print("\nFichier :", SORTIE)
print("Aucun nettoyage execute.")
print("Fichiers RAW et Silver inchanges.")
