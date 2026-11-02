# WP2 - BAAC 2019-2024

## Version pre-nettoyage v0.1

Statut : package de travail prepare, non encore livre ni valide.

## Objectif
Collecter, profiler, harmoniser et documenter les donnees
BAAC 2019-2024 avant les operations de nettoyage.

## Donnees
- 24 fichiers RAW sources
- 4 tables Silver harmonisees
- 1 992 145 lignes conservees
- CSV UTF-8-SIG, separateur point-virgule

## Harmonisations
- Accident_Id vers Num_Acc en 2022
- id_usager ajoute vide pour 2019-2020
- Normalisation des separateurs decimaux lat/long
- Ajout de la colonne annee

## Controles
- 12 tests structurels reussis
- 58 controles metier executes sans anomalie detectee
- 164 doublons exacts supplementaires identifies en 2019-2020
- Multiplicite des lieux en 2023-2024 preservee

## Documentation
- 64 entrees famille-variable avec definition
- 284 codes avec libelles proposes
- 7 reserves explicites sur les derniers codes
- Verification exhaustive des correspondances metier non achevee
- 8 regles de nettoyage preparees

## Restrictions
Aucune suppression ni nettoyage applique.
Les donnees RAW originales ne sont pas dans ce dossier.
Les besoins des autres WP et le contrat d'interface
WP2 vers WP3 restent a confirmer.

## Arborescence
- data/silver : tables harmonisees
- metadata/profilage : analyses de qualite
- metadata/harmonisation : controles et rapports
- metadata/codifications : dictionnaires et modalites
- metadata/nettoyage : regles a valider
- metadata/qualite : tests automatiques
- scripts : scripts Python reutilisables


## Documentation complementaire

- documentation/note_cadrage_wp2.md
- documentation/rapport_technique_wp2.md
- documentation/contrat_interface_wp2_wp3.md

Le contrat WP2 vers WP3 reste provisoire.
Le nettoyage n'a pas encore commence.
