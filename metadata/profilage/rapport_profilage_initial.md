# WP2 - Rapport de profilage initial BAAC

## 1. Perimetre
- Periode : 2019-2024
- Fichiers RAW analyses : 24
- Lignes analysees : 1992145
- Familles : caracteristiques, lieux, vehicules, usagers

## 2. Volumes par famille
- caracteristiques : 327628 lignes, 6 fichiers, 0 doublons exacts supplementaires
- lieux : 359512 lignes, 6 fichiers, 0 doublons exacts supplementaires
- usagers : 745158 lignes, 6 fichiers, 164 doublons exacts supplementaires
- vehicules : 559847 lignes, 6 fichiers, 0 doublons exacts supplementaires

## 3. Qualite initiale
- Doublons exacts supplementaires : 164
- Combinaisons annee/colonne avec >= 50 % de marqueurs manquants : 19
- Attention : les codes metier -1 et 0 ne sont pas automatiquement des valeurs manquantes.
- Les repetitions ne sont pas supprimees.

## 4. Particularites documentees
- Caracteristiques 2022 : Accident_Id renomme Num_Acc dans Silver.
- Usagers 2019-2020 : id_usager absent de la source.
- Lieux 2023-2024 : plusieurs lignes par accident.
- Usagers 2019-2020 : 164 doublons exacts supplementaires signales.
- Valeurs speciales : vide, N/A, null et -1 selon les variables et annees.

## 5. Controles
- Controles de relations reportes : 4
- Controles de cles reportes : 8
- Voir les rapports CSV pour les valeurs exactes.

## 6. Codifications
- 64 entrees famille-variable documentees.
- 284 codes distincts avec libelles proposes.
- 7 reserves explicites a confirmer.
- Revue officielle des correspondances encore necessaire.

## 7. Limites et decisions
- Aucune suppression de donnees a cette etape.
- Nettoyage non commence.
- Les besoins des autres WP restent a confirmer.
- Les taux de valeurs manquantes sont issus du profilage technique initial.

## 8. Fichiers de preuve
- metadata/profilage/
- metadata/harmonisation/
- metadata/codifications/
- metadata/nettoyage/registre_regles.csv
