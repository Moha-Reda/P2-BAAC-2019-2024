"""
WP2-08 - NETTOYAGE BAAC 2019-2024
Tache WP2-08 (regles WP2-07)

Entree  : data/silver/{famille}_2019_2024.csv   (jamais modifies)
Sorties : data/clean/{famille}_2019_2024.csv     (CSV ; UTF-8 BOM)
          metadata/nettoyage/journal_transformations.csv
          metadata/nettoyage/controles_apres_nettoyage.csv

Principes (note de cadrage, section 9.3) :
- aucune ligne supprimee : les anomalies sont signalees par des colonnes flag_*
- les codes categoriels (0, -1...) sont CONSERVES : leur sens depend de la
  variable (0 = "Aucun", "Sans objet", "Inconnu"...). Ils deviennent des
  modalites "Non renseigne" dans les dimensions du WP3.
- seules les variables NUMERIQUES (mesures) voient leurs marqueurs
  d'absence (-1, N/A, #ERREUR...) remplaces par vide, car un -1 fausserait
  une moyenne ou une somme.
- les colonnes d'origine ne sont pas reecrites quand une valeur est
  invalidee : une colonne derivee est creee a cote.
- chaque regle est journalisee avec le nombre de valeurs touchees par annee.

Lancement : python scripts/nettoyer_baac.py
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
CLEAN = ROOT / "data" / "clean"
META = ROOT / "metadata" / "nettoyage"

FAMILLES = ["caracteristiques", "lieux", "vehicules", "usagers"]

# Marqueurs textuels d'absence observes dans le profilage (v2 : N/A, null ;
# nbv : #ERREUR dans certains millesimes)
MARQUEURS_VIDES = ["N/A", "n/a", "NA", "NULL", "null", "nan", "NaN", "#ERREUR", "#VALEURMULTI"]

# Parametres metier (a valider par le chef WP2, regle R017/R018)
VMA_MIN, VMA_MAX = 5, 130
AGE_MIN, AGE_MAX = 0, 110
NBV_MAX = 12

# Emprise approximative France metropolitaine + DROM-COM
ZONES_GEO = [
    # (lat_min, lat_max, long_min, long_max, nom)
    (41.0, 51.5, -5.5, 10.0, "metropole"),
    (15.5, 18.5, -63.5, -60.5, "antilles"),
    (1.5, 6.5, -55.0, -51.0, "guyane"),
    (-21.6, -20.7, 55.0, 56.0, "reunion"),
    (-13.2, -12.4, 44.8, 45.5, "mayotte"),
    (46.5, 47.5, -57.0, -55.9, "saint_pierre"),
    (-23.0, -9.0, -155.0, -134.0, "polynesie"),
    (-23.0, -19.0, 163.0, 169.0, "nouvelle_caledonie"),
    (-14.5, -13.0, -178.5, -175.5, "wallis_futuna"),
]

journal = []


def log(regle, famille, serie_masque, df, description):
    """Enregistre le nombre de valeurs touchees par annee pour une regle."""
    if serie_masque is None:
        return
    compte = serie_masque.groupby(df["annee"]).sum()
    for annee, n in compte.items():
        journal.append({
            "regle": regle, "famille": famille, "annee": annee,
            "valeurs_touchees": int(n), "description": description,
        })


def lire(famille):
    chemin = SILVER / f"{famille}_2019_2024.csv"
    if not chemin.exists():
        sys.exit(f"Fichier introuvable : {chemin} (as-tu fait 'git lfs pull' ?)")
    df = pd.read_csv(chemin, sep=";", dtype=str, encoding="utf-8-sig",
                     keep_default_na=False)
    if df.iloc[0, 0].startswith("version https://git-lfs"):
        sys.exit(f"{chemin} est un pointeur Git LFS : lance 'git lfs pull'.")
    return df


def ecrire(df, famille):
    CLEAN.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN / f"{famille}_2019_2024.csv", sep=";", index=False,
              encoding="utf-8-sig")


# --------------------------------------------------------------------------
# Regles communes
# --------------------------------------------------------------------------

def r009_espaces(df, famille):
    """R009 : suppression des espaces en debut/fin de valeur."""
    total = pd.Series(False, index=df.index)
    for c in df.columns:
        nettoye = df[c].str.strip()
        total |= nettoye != df[c]
        df[c] = nettoye
    log("R009", famille, total, df, "Espaces superflus supprimes")
    return df


def r010_marqueurs_vides(df, famille):
    """R010 : marqueurs textuels d'absence -> vide (toutes colonnes)."""
    total = pd.Series(False, index=df.index)
    for c in df.columns:
        m = df[c].isin(MARQUEURS_VIDES)
        total |= m
        df.loc[m, c] = ""
    log("R010", famille, total, df, "Marqueurs N/A, null, #ERREUR remplaces par vide")
    return df


def numerique(df, famille, col, regle, nouvelle_col=None, mini=None, maxi=None):
    """Convertit une mesure en nombre : -1 et non-numeriques -> vide,
    hors bornes -> vide + flag. L'original reste dans `col` si nouvelle_col."""
    cible = nouvelle_col or col
    brut = df[col].str.replace(",", ".", regex=False)
    val = pd.to_numeric(brut, errors="coerce")
    non_renseigne = (val == -1) | (val.isna() & (brut != ""))
    val[val == -1] = np.nan
    hors = pd.Series(False, index=df.index)
    if mini is not None:
        hors |= val < mini
    if maxi is not None:
        hors |= val > maxi
    val[hors] = np.nan
    df[cible] = val.map(lambda x: "" if pd.isna(x) else (str(int(x)) if float(x).is_integer() else str(x)))
    log(regle, famille, non_renseigne, df, f"{col} : -1 ou non numerique -> vide")
    if mini is not None or maxi is not None:
        df[f"flag_{cible}_hors_bornes"] = hors.astype(int).astype(str)
        log(regle, famille, hors, df, f"{col} hors [{mini}, {maxi}] -> vide + flag")
    return df


# --------------------------------------------------------------------------
# Caracteristiques
# --------------------------------------------------------------------------

def nettoyer_caracteristiques(df):
    f = "caracteristiques"

    # R012 : dep sur 2 caracteres (01..95, 2A, 2B, 971...), com sur 5
    dep_avant = df["dep"].copy()
    est_chiffre = df["dep"].str.fullmatch(r"\d")
    df.loc[est_chiffre, "dep"] = "0" + df.loc[est_chiffre, "dep"]
    com_court = df["com"].str.fullmatch(r"\d{1,4}")
    df.loc[com_court, "com"] = df.loc[com_court, "com"].str.zfill(5)
    log("R012", f, (dep_avant != df["dep"]) | com_court, df,
        "Codes dep/com completes par des zeros a gauche")

    # R013 : heure HH:MM + colonne heure
    h = df["hrmn"].str.replace(":", "", regex=False).str.zfill(4)
    valide = h.str.fullmatch(r"([01]\d|2[0-3])[0-5]\d")
    modifie = valide & ((h.str[:2] + ":" + h.str[2:]) != df["hrmn"])
    df.loc[valide, "hrmn"] = h[valide].str[:2] + ":" + h[valide].str[2:]
    df["heure"] = np.where(valide, h.str[:2].astype(str).str.lstrip("0").replace("", "0"), "")
    df["flag_heure_invalide"] = (~valide).astype(int).astype(str)
    log("R013", f, modifie, df, "hrmn normalise au format HH:MM")
    log("R013", f, ~valide, df, "hrmn invalide -> flag (heure vide)")

    # R014 : date complete de l'accident (AAAA-MM-JJ), controle annee == an
    date = pd.to_datetime(
        df["an"].str.zfill(4) + "-" + df["mois"].str.zfill(2) + "-" + df["jour"].str.zfill(2),
        format="%Y-%m-%d", errors="coerce")
    df["date_accident"] = date.dt.strftime("%Y-%m-%d").fillna("")
    df["jour_semaine"] = date.dt.dayofweek.add(1).astype("Int64").astype(str).replace("<NA>", "")
    incoherent = date.isna() | (df["an"] != df["annee"])
    df["flag_date_invalide"] = incoherent.astype(int).astype(str)
    log("R014", f, incoherent, df, "Date invalide ou an different du millesime -> flag")

    # R015 : coordonnees numeriques, (0,0) -> vide, hors territoire -> flag
    lat = pd.to_numeric(df["lat"], errors="coerce")
    lon = pd.to_numeric(df["long"], errors="coerce")
    zero = (lat == 0) & (lon == 0)
    lat[zero] = np.nan
    lon[zero] = np.nan
    dans_zone = pd.Series(False, index=df.index)
    for la1, la2, lo1, lo2, _ in ZONES_GEO:
        dans_zone |= lat.between(la1, la2) & lon.between(lo1, lo2)
    hors = lat.notna() & lon.notna() & ~dans_zone
    df["lat"] = lat.map(lambda x: "" if pd.isna(x) else repr(float(x)))
    df["long"] = lon.map(lambda x: "" if pd.isna(x) else repr(float(x)))
    df["flag_coord_hors_territoire"] = hors.astype(int).astype(str)
    log("R015", f, zero, df, "Coordonnees (0,0) -> vide")
    log("R015", f, hors, df, "Coordonnees hors territoire francais -> flag (conservees)")
    return df


# --------------------------------------------------------------------------
# Lieux
# --------------------------------------------------------------------------

def nettoyer_lieux(df):
    f = "lieux"
    # R003 / R016 : largeurs et nombre de voies = mesures
    df = numerique(df, f, "larrout", "R003", "larrout_num")
    df = numerique(df, f, "lartpc", "R005", "lartpc_num")
    df = numerique(df, f, "nbv", "R016", "nbv_num", mini=0, maxi=NBV_MAX)
    # R017 : vitesse maximale autorisee
    df = numerique(df, f, "vma", "R017", "vma_num", mini=VMA_MIN, maxi=VMA_MAX)

    # R008 : plusieurs lieux par accident (2023-2024) -> conserves + compteur
    df["nb_lieux_accident"] = df.groupby("Num_Acc")["Num_Acc"].transform("size").astype(str)
    df["rang_lieu"] = (df.groupby("Num_Acc").cumcount() + 1).astype(str)
    log("R008", f, df["rang_lieu"] != "1", df,
        "Lignes de lieux supplementaires conservees (rang_lieu > 1)")
    return df


# --------------------------------------------------------------------------
# Vehicules
# --------------------------------------------------------------------------

def nettoyer_vehicules(df):
    f = "vehicules"
    # R006 : occupants transport en commun = mesure, vide si non applicable
    df = numerique(df, f, "occutc", "R006", "occutc_num")
    return df


# --------------------------------------------------------------------------
# Usagers
# --------------------------------------------------------------------------

def nettoyer_usagers(df):
    f = "usagers"

    # R007 : doublons exacts signales, jamais supprimes
    cols = [c for c in df.columns if c != "annee"]
    doublon = df.duplicated(subset=cols + ["annee"], keep="first")
    df["flag_doublon_exact"] = doublon.astype(int).astype(str)
    log("R007", f, doublon, df, "Doublon exact signale (conserve)")

    # R018 : age a la date de l'accident
    an_nais = pd.to_numeric(df["an_nais"], errors="coerce")
    age = pd.to_numeric(df["annee"]) - an_nais
    hors = age.notna() & ((age < AGE_MIN) | (age > AGE_MAX))
    age[hors] = np.nan
    df["age"] = age.map(lambda x: "" if pd.isna(x) else str(int(x)))
    df["flag_age_hors_bornes"] = hors.astype(int).astype(str)
    log("R018", f, hors, df, f"Age hors [{AGE_MIN}, {AGE_MAX}] -> vide + flag")

    # R019 : indicateurs de gravite (1 indemne, 2 tue, 3 hospitalise, 4 leger)
    df["est_tue"] = (df["grav"] == "2").astype(int).astype(str)
    df["est_blesse_hospitalise"] = (df["grav"] == "3").astype(int).astype(str)
    df["est_blesse_leger"] = (df["grav"] == "4").astype(int).astype(str)
    df["est_indemne"] = (df["grav"] == "1").astype(int).astype(str)
    return df


TRAITEMENTS = {
    "caracteristiques": nettoyer_caracteristiques,
    "lieux": nettoyer_lieux,
    "vehicules": nettoyer_vehicules,
    "usagers": nettoyer_usagers,
}


# --------------------------------------------------------------------------
# Controles apres nettoyage
# --------------------------------------------------------------------------

def controler(tables, volumes_avant):
    res = []

    def ajoute(nom, ok, detail=""):
        res.append({"controle": nom, "resultat": "OK" if ok else "ECHEC", "detail": detail})

    for f, df in tables.items():
        ajoute(f"Volume conserve - {f}", len(df) == volumes_avant[f],
               f"{volumes_avant[f]} -> {len(df)}")

    car = tables["caracteristiques"]
    ajoute("Num_Acc unique dans caracteristiques", car["Num_Acc"].is_unique)
    ajoute("(Num_Acc, id_vehicule) unique dans vehicules",
           not tables["vehicules"].duplicated(["Num_Acc", "id_vehicule"]).any())
    acc = set(car["Num_Acc"])
    for f in ["lieux", "vehicules", "usagers"]:
        orphelins = (~tables[f]["Num_Acc"].isin(acc)).sum()
        ajoute(f"Aucun orphelin Num_Acc - {f}", orphelins == 0, f"{orphelins} orphelins")
    veh = set(zip(tables["vehicules"]["Num_Acc"], tables["vehicules"]["id_vehicule"]))
    us = tables["usagers"]
    orph = sum((a, v) not in veh for a, v in zip(us["Num_Acc"], us["id_vehicule"]))
    ajoute("Usagers relies a un vehicule existant", orph == 0, f"{orph} orphelins")
    ajoute("Aucune valeur -1 dans les mesures numeriques",
           not any((tables["lieux"][c] == "-1").any() for c in ["vma_num", "nbv_num", "larrout_num"]))
    return pd.DataFrame(res)


def main():
    META.mkdir(parents=True, exist_ok=True)
    tables, volumes = {}, {}
    for f in FAMILLES:
        print(f"Nettoyage {f}...")
        df = lire(f)
        volumes[f] = len(df)
        df = r009_espaces(df, f)
        df = r010_marqueurs_vides(df, f)
        df = TRAITEMENTS[f](df)
        tables[f] = df

    controles = controler(tables, volumes)
    controles.to_csv(META / "controles_apres_nettoyage.csv", sep=";", index=False, encoding="utf-8-sig")
    pd.DataFrame(journal).to_csv(META / "journal_transformations.csv", sep=";", index=False, encoding="utf-8-sig")
    print(controles.to_string(index=False))

    if (controles["resultat"] == "ECHEC").any():
        sys.exit("\nCertains controles ont echoue : fichiers propres NON ecrits.")
    for f, df in tables.items():
        ecrire(df, f)
    print(f"\nFichiers propres ecrits dans {CLEAN}")


if __name__ == "__main__":
    main()
