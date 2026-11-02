from pathlib import Path
from datetime import datetime
import csv
import shutil

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "documentation"
META = ROOT / "metadata"
PACKAGE = ROOT / "livraisons" / "v0_1_pre_nettoyage"

DOC.mkdir(parents=True, exist_ok=True)

def lire_csv(chemin):
    with chemin.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))

def enregistrer(nom, contenu):
    chemin = DOC / nom
    chemin.write_text(contenu.strip() + "\n", encoding="utf-8")
    print(f"[OK] {chemin.name}")
    return chemin

# Verification des preuves disponibles
preuves = {
    "volumes": META / "profilage" / "profilage_brut_resume.csv",
    "dictionnaire": META / "codifications" / "dictionnaire_baac_complet.csv",
    "modalites": META / "codifications" / "modalites_baac_finalisees.csv",
    "regles": META / "nettoyage" / "plan_nettoyage_a_valider.csv",
    "tests": META / "qualite" / "tests_avant_nettoyage.csv",
    "metier": META / "qualite" / "controle_metier_avant_nettoyage.csv",
}

for nom, chemin in preuves.items():
    if not chemin.exists():
        raise FileNotFoundError(f"Preuve manquante : {chemin}")

volumes = lire_csv(preuves["volumes"])
dictionnaire = lire_csv(preuves["dictionnaire"])
modalites = lire_csv(preuves["modalites"])
regles = lire_csv(preuves["regles"])
tests = lire_csv(preuves["tests"])
metier = lire_csv(preuves["metier"])

total = sum(int(r["lignes"]) for r in volumes)
doublons = sum(int(r["doublons_exacts"]) for r in volumes)
tests_ok = sum(r["statut"] == "OK" for r in tests)
definitions = sum(bool(r["definition"].strip()) for r in dictionnaire)
libelles = sum(bool(r["libelle"].strip()) for r in modalites)

if total != 1992145 or len(volumes) != 24:
    raise ValueError("Les volumes sources ne correspondent pas au bilan connu.")
if len(dictionnaire) != 64 or len(modalites) != 284:
    raise ValueError("Inventaire du dictionnaire ou des modalites inattendu.")
if tests_ok != len(tests):
    raise ValueError("Certains tests structurels ne sont pas reussis.")

date = datetime.now().strftime("%d/%m/%Y")

# ==============================================
# 1 - NOTE DE CADRAGE
# ==============================================

cadrage = f"""
# WP2 - Note de cadrage : Donnees et qualite

**Projet :** Exploitation decisionnelle des donnees BAAC 2019-2024
**Version :** 0.1 - Avant nettoyage
**Date de consolidation :** {date}
**Statut :** Document de travail, validation WP0 et autres WP en attente

## 1. Contexte

Le WP2 assure la collecte, la comprehension, la preparation,
la documentation et le controle de qualite des donnees BAAC.

Les donnees doivent etre exploitables par les autres work packages,
notamment WP3 pour l'integration et la structuration decisionnelle.

## 2. Objectifs

1. Rassembler les fichiers officiels BAAC de 2019 a 2024.
2. Comparer les schemas des differentes annees.
3. Etablir un diagnostic de qualite initial.
4. Harmoniser les structures sans supprimer de lignes.
5. Documenter les variables et les valeurs codees.
6. Definir des regles de nettoyage explicites et verifiables.
7. Produire des fichiers reproductibles et utilisables par WP3.
8. Tracer les limites, anomalies, traitements et decisions.

## 3. Perimetre

### Inclus

- Periode 2019-2024.
- Quatre familles : caracteristiques, lieux, vehicules, usagers.
- 24 fichiers CSV sources.
- Profilage, harmonisation, codifications et tests.
- Preparation des regles de nettoyage.
- Documentation et interface vers WP3.

### Exclus de la version actuelle

- Suppression ou correction des enregistrements.
- Imputation des valeurs manquantes.
- Arbitrage definitif des anomalies metier.
- Construction de l'entrepot decisionnel de WP3.
- Validation definitive par les autres WP.

## 4. Organisation et responsabilites

La repartition officielle des responsabilites WP2 reste inchangee.
La centralisation de la preparation technique ne modifie pas les
attributions des membres ni les contributions effectivement realisees.

| Tache | Activite | Responsable prevu |
|---|---|---|
| WP2-01 | Cadrage et organisation | Mohamed Reda |
| WP2-02 | Inventaire et collecte | Raphael |
| WP2-03 | Comparaison des schemas | Melissandre |
| WP2-04 | Profilage initial | Justin |
| WP2-05 | Referentiel des codifications | Febbe |
| WP2-14 | Recueil des besoins des WP | Mohamed Reda |
| WP2-15 | Contrat d'interface WP2 vers WP3 | Raphael + WP3 |
| WP2-06 | Scripts d'harmonisation | Melissandre |
| WP2-06b | Livraison intermediaire v0.1 | Mohamed Reda |
| WP2-07 | Regles de nettoyage | Victor |
| WP2-08 | Execution du nettoyage | Victor |
| WP2-09 | Assurance qualite | Maha |
| WP2-10 | Profilage final avant/apres | Justin |
| WP2-11 | Dictionnaire et limites connues | Lucas |
| WP2-12 | README et documentation | Lucas |
| WP2-13 | Integration et validation v1.0 | Mohamed Reda |
| WP2-16 | Support et corrections | Mohamed Reda + Victor |
| WP2-17 | Chapitre du rapport en anglais | Lucas + equipe |
| WP2-18 | Presentation et soutenance | Mohamed Reda + equipe |

Les responsables doivent pouvoir relire, tester et expliquer les
livrables de leur domaine. Les temps passes et les validations doivent
rester fideles aux contributions reelles.

## 5. Jalons de reference

- 02/11/2026 : consolidation des besoins et du contrat d'interface.
- 06/11/2026 : objectif de livraison intermediaire v0.1.
- 13/11/2026 : objectif de livraison v1.0 apres nettoyage et validation.
- Novembre-decembre : support et documentation finale.
- Decembre-janvier : preparation de la presentation.

Une version de travail pre-nettoyage est assemblee avant ces jalons.
Elle ne constitue pas a elle seule une acceptation officielle.

## 6. Methodologie

Pipeline de reference :

RAW -> Inventaire -> Profilage -> Harmonisation Silver
-> Codifications -> Regles -> Nettoyage futur
-> Tests apres nettoyage -> Livraison.

Les fichiers RAW restent intacts.

Chaque transformation est associee a un script Python et,
lorsque disponible, a un rapport de controle.

## 7. Resultats deja obtenus

- {len(volumes)} fichiers sources analyses.
- {total:,} lignes dans les quatre familles.
- Quatre tables Silver harmonisees.
- {definitions}/{len(dictionnaire)} entrees du dictionnaire avec definition.
- {libelles}/{len(modalites)} codes avec libelle propose.
- {tests_ok}/{len(tests)} tests structurels reussis.
- {len(metier)} controles metier documentes.
- {doublons} doublons exacts supplementaires reperes.

Les controles ne remplacent pas une validation metier exhaustive.

## 8. Risques et points de vigilance

### Multiplicite de la table lieux

Plusieurs enregistrements peuvent correspondre au meme accident
en 2023 et 2024. Une jointure directe peut multiplier les lignes.

### Usagers 2019-2020

Absence de id_usager dans les sources d'origine. Des lignes
strictement identiques ne prouvent pas qu'il s'agit de la
meme personne.

### Valeurs speciales

Les valeurs vides, N/A, null, -1 et 0 doivent etre interpretees
en fonction des variables et des millesimes.

### Codifications

Un libelle renseigne ne constitue pas a lui seul la preuve
d'une validation officielle. Les correspondances doivent
etre relues avant leur usage metier definitif.

### Dependances externes

Besoins des WP1, WP3, WP4 et WP5-WP7 a confirmer.
Accord de WP3 sur le format, les cles et les cardinalites requis.

## 9. Regles de gouvernance

- Aucun effacement automatique des doublons.
- Aucune suppression de colonne sans arbitrage.
- Conservation de la provenance et de l'annee.
- Documentation des exceptions et reserves.
- Versionnement des livrables.
- Validation explicite des traitements avant nettoyage.

## 10. Criteres d'acceptation de la prochaine version

- Formats et nomenclature approuves par WP3.
- Besoins de variables confirmes par les autres WP.
- Regles de nettoyage arbitrees et documentees.
- Scripts reproductibles.
- Integrite referentielle controlee.
- Comparaison de qualite avant/apres nettoyage.
- README, dictionnaire, limites et rapports disponibles.

## 11. Etat actuel

La version pre-nettoyage est techniquement assemblee.
Le nettoyage n'a pas commence.
Le contrat d'interface et les decisions metier restent provisoires.

## 12. Documentation associee

- rapport_technique_wp2.md
- contrat_interface_wp2_wp3.md
- metadata/profilage/
- metadata/harmonisation/
- metadata/codifications/
- metadata/nettoyage/
- metadata/qualite/
- scripts/
"""

enregistrer("note_cadrage_wp2.md", cadrage)

# ==============================================
# 2 - RAPPORT TECHNIQUE
# ==============================================

volumes_lignes = []
for famille in ("caracteristiques", "lieux", "vehicules", "usagers"):
    selection = [r for r in volumes if r["famille"] == famille]
    n = sum(int(r["lignes"]) for r in selection)
    d = sum(int(r["doublons_exacts"]) for r in selection)
    volumes_lignes.append(f"| {famille} | {n:,} | {d} |")

rapport = f"""
# WP2 - Rapport technique avant nettoyage

**Periode :** BAAC 2019-2024
**Date :** {date}
**Version :** 0.1 - Rapport des operations realisees

## 1. Environnement technique

- Python et Pandas.
- Fichiers CSV au separateur point-virgule.
- Dossiers RAW, Silver, metadata et scripts.
- Scripts Python conserves pour reproduction.

## 2. Collecte

24 fichiers CSV sources, organises par annee et famille.

Dossier de reference : data/raw/{{annee}}/

L'inventaire des sources est conserve dans
metadata/sources_inventory.csv lorsqu'il est disponible.

Les RAW ne sont pas modifies.

## 3. Volumes

| Famille | Lignes | Doublons exacts supplementaires |
|---|---:|---:|
{chr(10).join(volumes_lignes)}
| **Total** | **{total:,}** | **{doublons}** |

## 4. Analyse comparative des schemas

### Caracteristiques 2022

La colonne Accident_Id a ete harmonisee sous le nom Num_Acc.

### Usagers 2019-2020

La colonne id_usager n'existait pas dans ces sources.
Elle a ete ajoutee vide dans les tables harmonisees,
sans creation de faux identifiants.

### Colonne annee

Une colonne technique annee est ajoutee aux quatre familles.

## 5. Harmonisation

Script : scripts/harmoniser_baac.py

Operations effectuees :

1. Lecture des CSV annuels.
2. Adaptation des schemas connus.
3. Conversion de la virgule decimale en point pour lat/long.
4. Ajout de l'annee d'origine.
5. Concatenation des six annees par famille.
6. Export des quatre fichiers Silver.

Les quatre fichiers contiennent {total:,} lignes au total.
Aucune ligne n'a ete supprimee pendant l'harmonisation.

## 6. Profilage initial

Scripts principaux :

- scripts/profiler_baac.py
- scripts/analyser_valeurs_speciales.py
- scripts/generer_rapport_profilage_wp2.py

Resultats :

- {len(volumes)} fichiers profiles.
- {doublons} doublons exacts supplementaires.
- 19 combinaisons annee/colonne ayant au moins
  50 % de marqueurs textuels manquants dans le rapport initial.

Les codes -1 et 0 ne sont pas consideres
systematiquement comme manquants.

## 7. Analyse des doublons

### Usagers 2019

- 101 doublons supplementaires.
- 187 lignes impliquees.
- 65 accidents concernes.

### Usagers 2020

- 63 doublons supplementaires.
- 112 lignes impliquees.
- 37 accidents concernes.

Decision : conserver les lignes avant arbitrage metier.

## 8. Particularites de lieux

### 2023

- 70 860 lignes.
- 54 822 accidents distincts.
- 15 870 accidents avec plusieurs lignes.

### 2024

- 70 248 lignes.
- 54 402 accidents distincts.
- 15 645 accidents avec plusieurs lignes.

Attention aux jointures un-a-plusieurs et aux
comptages d'accidents sans DISTINCT.

## 9. Integrite referentielle

Relations controlees :

- lieux.Num_Acc vers caracteristiques.Num_Acc
- vehicules.Num_Acc vers caracteristiques.Num_Acc
- usagers.Num_Acc vers caracteristiques.Num_Acc
- usagers.(Num_Acc, id_vehicule) vers vehicules

Les controles executes n'ont trouve aucune ligne
sans correspondance pour ces cles.

Unicite observee :

- Num_Acc dans caracteristiques.
- (Num_Acc, id_vehicule) dans vehicules.

## 10. Codifications

- {len(dictionnaire)} entrees famille-variable dans le dictionnaire.
- {definitions} descriptions generales renseignees.
- {len(modalites)} codes distincts par famille-variable.
- {libelles} codes avec libelle propose.
- 7 reserves explicites ajoutees lors de la finalisation.

Limite : les libelles proposes necessitent une
verification documentaire, notamment sur les
changements de modalites selon les annees.

## 11. Tests automatiques

- {len(tests)} tests structurels executes.
- {tests_ok} tests structurels reussis.
- {len(metier)} controles metier annee/critere realises.
- Aucune anomalie signalee par le rapport metier utilise.

Les dates, coordonnees, cles et correspondances ont
ete controlees selon les tests disponibles.

La validite geographique mondiale ne prouve pas
qu'un point soit situe en France ou dans les DROM.

## 12. Regles de nettoyage preparees

Nombre de regles : {len(regles)}.

- R001 : renommage de cle 2022.
- R002 : colonne id_usager absente en 2019-2020.
- R003 : valeurs -1 dans larrout.
- R004 : marqueurs dans v2.
- R005 : forte incompletude de lartpc.
- R006 : applicabilite de occutc.
- R007 : doublons usagers 2019-2020.
- R008 : multiplicite de lieux 2023-2024.

Aucun nettoyage applique a ce stade.

## 13. Fichiers de preuve

- metadata/profilage/profilage_brut_resume.csv
- metadata/profilage/profilage_brut_colonnes.csv
- metadata/profilage/analyse_valeurs_speciales.csv
- metadata/harmonisation/rapport_harmonisation.csv
- metadata/harmonisation/rapport_relations_baac.csv
- metadata/harmonisation/rapport_cles_baac.csv
- metadata/codifications/dictionnaire_baac_complet.csv
- metadata/codifications/modalites_baac_finalisees.csv
- metadata/nettoyage/plan_nettoyage_a_valider.csv
- metadata/qualite/tests_avant_nettoyage.csv
- metadata/qualite/controle_metier_avant_nettoyage.csv

## 14. Prochaine phase

1. Confirmer les besoins des autres WP.
2. Valider le contrat d'interface avec WP3.
3. Arbitrer les regles de nettoyage.
4. Executer les transformations dans une sortie distincte.
5. Comparer les indicateurs avant/apres.
6. Faire valider la version nettoyee.

## 15. Conclusion

La collecte, l'harmonisation, le profilage et une
premiere campagne de controles sont executes.

Le travail est reproductible et les fichiers originaux
sont preserves. La validation metier exhaustive et
le nettoyage restent a realiser.
"""

enregistrer("rapport_technique_wp2.md", rapport)

# ==============================================
# 3 - CONTRAT WP2 VERS WP3
# ==============================================

contrat = f"""
# Contrat d'interface provisoire WP2 vers WP3

**Version :** 0.1
**Date :** {date}
**Statut :** PROPOSITION - non encore acceptee par WP3

## 1. Objet

Definir les donnees, formats, cles et limites transmis
par WP2 a WP3 pour integration dans la zone decisionnelle.

## 2. Jeux de donnees fournis

| Fichier | Grain principal | Lignes |
|---|---|---:|
| caracteristiques_2019_2024.csv | Accident | 327 628 |
| lieux_2019_2024.csv | Enregistrement de lieu | 359 512 |
| vehicules_2019_2024.csv | Vehicule d'un accident | 559 847 |
| usagers_2019_2024.csv | Enregistrement d'usager | 745 158 |

Chemin relatif : data/silver/

## 3. Format actuel propose

- Format : CSV.
- Separateur : point-virgule.
- Encodage : UTF-8 avec BOM.
- Premiere ligne : noms des colonnes.
- Periode : 2019 a 2024.
- Colonne technique : annee.
- Lecture initiale recommandee : toutes les colonnes
  sous forme de texte pour preserver les codes et identifiants.
- Conversion vers des types cibles selon les variables
  et les regles validees par WP3.

Ces conventions representent le format actuel des exports.
L'acceptation formelle de WP3 reste necessaire.

## 4. Cles et cardinalites

### Caracteristiques vers vehicules

- Cle accident : Num_Acc.
- Relation observee : un accident vers plusieurs vehicules.
- Cle unique des vehicules : (Num_Acc, id_vehicule).

### Caracteristiques vers usagers

- Cle accident : Num_Acc.
- Plusieurs usagers peuvent appartenir au meme accident.
- id_usager n'est pas disponible dans les sources 2019-2020.

### Caracteristiques vers lieux

- Cle accident : Num_Acc.
- Les donnees 2023 et 2024 peuvent contenir
  plusieurs lignes de lieux pour un accident.
- Ne pas imposer de contrainte UNIQUE sur lieux.Num_Acc.

### Vehicules vers usagers

- Jointure recommandee :
  vehicules.Num_Acc = usagers.Num_Acc
  ET vehicules.id_vehicule = usagers.id_vehicule.

## 5. Regles de jointure

Attention : joindre simultanement lieux, vehicules
et usagers sur Num_Acc seul peut multiplier les lignes.

Pour calculer le nombre d'accidents :
COUNT(DISTINCT Num_Acc), au bon niveau de granularite.

Pour les statistiques usagers :
travailler au niveau des enregistrements usagers,
avec une politique explicite sur les doublons 2019-2020.

Pour les statistiques vehicules :
utiliser la cle composite accident-vehicule.

La strategie de modelisation finale revient a WP3.

## 6. Transformations deja appliquees

- Accident_Id renomme Num_Acc pour caracteristiques 2022.
- id_usager ajoute vide pour 2019-2020.
- lat/long harmonises avec point decimal.
- Colonne annee ajoutee.
- Aucun retrait de lignes.

## 7. Restrictions et limites

- Tables harmonisees mais non nettoyees.
- 164 doublons exacts supplementaires dans
  les usagers 2019-2020, conserves.
- Multiplicite de lieux en 2023-2024.
- Valeurs speciales variables selon les colonnes.
- Certaines codifications necessitent encore validation.
- Pas de garantie de qualite metier exhaustive.

## 8. Dictionnaire et documentation

WP2 fournit :

- dictionnaire_baac_complet.csv
- modalites_baac_finalisees.csv
- codifications_a_confirmer.csv
- rapports de profilage et d'integrite
- scripts de transformation
- registre et plan des regles de nettoyage

## 9. Points a confirmer avec WP3

- [ ] Separateur et encodage acceptes.
- [ ] Noms des fichiers et des colonnes acceptes.
- [ ] Types cibles des donnees.
- [ ] Gestion des valeurs non renseignees.
- [ ] Strategie de jointure avec lieux.
- [ ] Gestion des doublons d'usagers 2019-2020.
- [ ] Strategie d'identification des usagers sans id_usager.
- [ ] Besoins sur les colonnes obligatoires.
- [ ] Methode de depot et de versionnement.
- [ ] Regles d'acceptation de la livraison.

## 10. Critere de validation de l'interface

Ce document deviendra un contrat valide lorsque
les representants WP2 et WP3 auront confirme
les points precedents et consigne leur accord.

Aucune acceptation n'est presumee a ce stade.
"""

enregistrer("contrat_interface_wp2_wp3.md", contrat)

# ==============================================
# 4 - SYNCHRONISATION DU PACKAGE
# ==============================================

if not PACKAGE.exists():
    raise FileNotFoundError(
        "Le dossier v0_1_pre_nettoyage n'existe pas."
    )

cible = PACKAGE / "documentation"
cible.mkdir(parents=True, exist_ok=True)

for fichier in DOC.glob("*.md"):
    shutil.copy2(fichier, cible / fichier.name)

# Mettre a jour le README sans l'ecraser
readme = PACKAGE / "README.md"
ajout = """
## Documentation complementaire

- documentation/note_cadrage_wp2.md
- documentation/rapport_technique_wp2.md
- documentation/contrat_interface_wp2_wp3.md

Le contrat WP2 vers WP3 reste provisoire.
Le nettoyage n'a pas encore commence.
"""

contenu = readme.read_text(encoding="utf-8")
if "## Documentation complementaire" not in contenu:
    with readme.open("a", encoding="utf-8") as f:
        f.write("\n" + ajout)

# Recalculer l'inventaire sans s'y inclure lui-meme
inventaire = []

for fichier in sorted(PACKAGE.rglob("*")):
    if fichier.is_file() and fichier.name != "inventaire_livraison.csv":
        inventaire.append({
            "chemin": fichier.relative_to(PACKAGE).as_posix(),
            "taille_octets": fichier.stat().st_size
        })

with (PACKAGE / "inventaire_livraison.csv").open(
    "w", newline="", encoding="utf-8-sig"
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["chemin", "taille_octets"],
        delimiter=";"
    )
    writer.writeheader()
    writer.writerows(inventaire)

print("\n=== DOCUMENTATION WP2 : BILAN ===")
print("Note de cadrage : OK")
print("Rapport technique : OK")
print("Contrat WP2-WP3 provisoire : OK")
print("Documentation integree au package : OK")
print("Inventaire actualise :", len(inventaire), "fichiers")
print("Dossier documentation :", DOC)
print("Package :", PACKAGE)
print("RAW et Silver inchanges.")
