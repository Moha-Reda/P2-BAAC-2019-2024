# WP2 - Rapport technique avant nettoyage

**Periode :** BAAC 2019-2024
**Date :** 01/11/2026
**Version :** 0.1 - Rapport des operations realisees

## 1. Environnement technique

- Python et Pandas.
- Fichiers CSV au separateur point-virgule.
- Dossiers RAW, Silver, metadata et scripts.
- Scripts Python conserves pour reproduction.

## 2. Collecte

24 fichiers CSV sources, organises par annee et famille.

Dossier de reference : data/raw/{annee}/

L'inventaire des sources est conserve dans
metadata/sources_inventory.csv lorsqu'il est disponible.

Les RAW ne sont pas modifies.

## 3. Volumes

| Famille | Lignes | Doublons exacts supplementaires |
|---|---:|---:|
| caracteristiques | 327,628 | 0 |
| lieux | 359,512 | 0 |
| vehicules | 559,847 | 0 |
| usagers | 745,158 | 164 |
| **Total** | **1,992,145** | **164** |

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

Les quatre fichiers contiennent 1,992,145 lignes au total.
Aucune ligne n'a ete supprimee pendant l'harmonisation.

## 6. Profilage initial

Scripts principaux :

- scripts/profiler_baac.py
- scripts/analyser_valeurs_speciales.py
- scripts/generer_rapport_profilage_wp2.py

Resultats :

- 24 fichiers profiles.
- 164 doublons exacts supplementaires.
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

- 64 entrees famille-variable dans le dictionnaire.
- 64 descriptions generales renseignees.
- 284 codes distincts par famille-variable.
- 284 codes avec libelle propose.
- 7 reserves explicites ajoutees lors de la finalisation.

Limite : les libelles proposes necessitent une
verification documentaire, notamment sur les
changements de modalites selon les annees.

## 11. Tests automatiques

- 12 tests structurels executes.
- 12 tests structurels reussis.
- 58 controles metier annee/critere realises.
- Aucune anomalie signalee par le rapport metier utilise.

Les dates, coordonnees, cles et correspondances ont
ete controlees selon les tests disponibles.

La validite geographique mondiale ne prouve pas
qu'un point soit situe en France ou dans les DROM.

## 12. Regles de nettoyage preparees

Nombre de regles : 8.

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
