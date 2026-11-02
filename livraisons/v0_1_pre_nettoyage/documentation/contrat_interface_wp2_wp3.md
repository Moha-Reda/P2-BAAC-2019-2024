# Contrat d'interface provisoire WP2 vers WP3

**Version :** 0.1
**Date :** 01/11/2026
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
