#!/usr/bin/env python3
"""Téléchargement reproductible des 24 fichiers BAAC 2019-2024 depuis data.gouv.fr.

Usage:
    pip install requests
    python wp2_download_baac.py --dry-run
    python wp2_download_baac.py
    python wp2_download_baac.py --root /chemin/vers/WP2

Ne modifie jamais le contenu des CSV d'origine.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DATASET_ID = "53698f4ca3a729239d2036df"
API_URL = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_ID}/"
YEARS = range(2019, 2025)
FAMILIES = ("caracteristiques", "lieux", "vehicules", "usagers")


def normalize(text):
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def classify(resource):
    """Classe selon le nom de la ressource, jamais selon le contenu des lignes."""
    title = resource.get("title") or ""
    filename = unquote(Path(urlparse(resource.get("url") or "").path).name)
    label = normalize(f"{title} {filename}")
    if "immatricul" in label:  # Ressource distincte, hors 4 tables BAAC
        return None
    fmt = normalize(str(resource.get("format") or ""))
    if fmt and fmt != "csv" and not filename.lower().endswith(".csv"):
        return None
    if not (".csv" in label or fmt == "csv"):
        return None
    years = {int(y) for y in re.findall(r"(?<!\d)(20(?:19|2[0-4]))(?!\d)", label)}
    years = years.intersection(YEARS)
    if len(years) != 1:
        return None
    year = next(iter(years))
    # Les noms de sources BAAC varient : caract_2024, caracteristiques-2019, etc.
    aliases = {
        "caracteristiques": r"(?:caract|caracteristiques?)",
        "lieux": r"lieux?",
        "vehicules": r"vehicules?",
        "usagers": r"usagers?",
    }
    matches = [key for key, pattern in aliases.items()
               if re.search(rf"(?<![a-z]){pattern}(?![a-z])", label)]
    if len(matches) != 1:
        return None
    return year, matches[0]


def session_with_retries():
    session = requests.Session()
    session.headers.update({"User-Agent": "WP2-BAAC-collecte/1.0 (academic reproducibility)"})
    retry = Retry(total=4, connect=4, read=4, backoff_factor=1,
                  status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


def checksum(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download(session, url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    if tmp.exists():
        tmp.unlink()
    try:
        with session.get(url, stream=True, timeout=(20, 120)) as response:
            response.raise_for_status()
            with tmp.open("wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        if not tmp.stat().st_size:
            raise ValueError("Fichier téléchargé vide")
        # Détection simple d'une page HTML reçue par erreur.
        with tmp.open("rb") as f:
            signature = f.read(512).lstrip().lower()
        if signature.startswith((b"<!doctype html", b"<html")):
            raise ValueError("Le serveur a renvoyé du HTML plutôt qu'un CSV")
        tmp.replace(dest)
    finally:
        if tmp.exists():
            tmp.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("WP2_BAAC"), help="Dossier projet")
    parser.add_argument("--dry-run", action="store_true", help="Prévisualiser sans télécharger")
    parser.add_argument("--overwrite", action="store_true", help="Retélécharger les fichiers existants")
    args = parser.parse_args()
    root = args.root
    print(f"Lecture des métadonnées officielles : {API_URL}")
    session = session_with_retries()
    try:
        response = session.get(API_URL, timeout=(20, 60))
        response.raise_for_status()
        dataset = response.json()
    except (requests.RequestException, ValueError) as exc:
        sys.exit(f"ERREUR : API data.gouv.fr inaccessible : {exc}")

    found = {}
    for res in dataset.get("resources", []):
        key = classify(res)
        if key:
            found.setdefault(key, []).append(res)
    required = [(y, f) for y in YEARS for f in FAMILIES]
    missing = [k for k in required if k not in found]
    ambiguous = {k: v for k, v in found.items() if len(v) != 1}
    if missing or ambiguous:
        if missing:
            print("Ressources absentes :", ", ".join(f"{f}_{y}" for y, f in missing), file=sys.stderr)
        if ambiguous:
            print("Ressources ambiguës (plusieurs versions) :", file=sys.stderr)
            for key, choices in ambiguous.items():
                print(f"  {key}: {[c.get('title') for c in choices]}", file=sys.stderr)
        sys.exit("ARRÊT : sélection non univoque. Vérifier les ressources sur data.gouv.fr avant de continuer.")

    print(f"24 ressources BAAC identifiées (4 familles × 6 ans).")
    manifest = []
    for year, family in required:
        res = found[(year, family)][0]
        url = res.get("url")
        if not url or not url.startswith("https://"):
            sys.exit(f"URL invalide pour {family}_{year}: {url}")
        dest = root / "data" / "raw" / str(year) / f"{family}_{year}.csv"
        if args.dry_run:
            print(f"[SIMULATION] {res.get('title')} -> {dest}")
            continue
        status = "déjà présent" if dest.is_file() and dest.stat().st_size > 0 and not args.overwrite else "téléchargé"
        try:
            if status == "téléchargé":
                download(session, url, dest)
            sha = checksum(dest)
            print(f"[{status}] {family}_{year} | {dest.stat().st_size:,} octets")
        except (OSError, ValueError, requests.RequestException) as exc:
            sys.exit(f"ERREUR sur {family}_{year} : {exc}")
        manifest.append({
            "year": year, "family": family, "filename": dest.name,
            "source_title": res.get("title", ""), "resource_id": res.get("id", ""),
            "source_url": url, "resource_last_modified": res.get("last_modified", ""),
            "bytes": dest.stat().st_size, "sha256": sha, "status": status,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        })
        time.sleep(0.1)

    if args.dry_run:
        print("Simulation terminée : aucun téléchargement ni dossier créé.")
        return
    meta = root / "metadata"
    meta.mkdir(parents=True, exist_ok=True)
    with (meta / "sources_inventory.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)
    (meta / "dataset_metadata.json").write_text(
        json.dumps({"id": dataset.get("id"), "title": dataset.get("title"),
                    "url": API_URL, "download_count": len(manifest)},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    for folder in ("silver", "clean", "delivery"):
        (root / "data" / folder).mkdir(parents=True, exist_ok=True)
    print(f"\nSUCCÈS : {len(manifest)} fichiers collectés.")
    print(f"Inventaire : {meta / 'sources_inventory.csv'}")
    print("Les fichiers bruts restent inchangés. Ne pas mélanger les 4 tables.")


if __name__ == "__main__":
    main()
