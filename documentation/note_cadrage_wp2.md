# WP2 - Note de cadrage : Donnees et qualite

**Projet :** Exploitation decisionnelle des donnees BAAC 2019-2024
**Version :** 0.1 - Avant nettoyage
**Date de consolidation :** 01/11/2026
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

- 24 fichiers sources analyses.
- 1,992,145 lignes dans les quatre familles.
- Quatre tables Silver harmonisees.
- 64/64 entrees du dictionnaire avec definition.
- 284/284 codes avec libelle propose.
- 12/12 tests structurels reussis.
- 58 controles metier documentes.
- 164 doublons exacts supplementaires reperes.

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
