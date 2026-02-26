""" Run this script to create data for the asteroid targets listed in targets.txt using the JPL SBDB API. """

import os
import json
import requests
import time
import re
import unicodedata

API_BASE = "https://ssd-api.jpl.nasa.gov/sbdb.api"
OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

def load_targets(filename="targets.txt"):
    """Load asteroid targets from a text file (one per line, cleans tabs/spaces)"""
    targets = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Replace tabs and multiple spaces with a single space
                clean_line = re.sub(r"\s+", " ", line)
                targets.append(clean_line)
        print(f"Loaded {len(targets)} targets from {filename}")
        return targets
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return []

def normalize_name(name):
    """Normalize special characters to plain ASCII (e.g. Ignés → Ignes)"""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_name

def extract_numeric_id(name):
    """Extract numeric designation from names like '622467 Ignés'"""
    match = re.match(r"^\d+", name)
    return match.group(0) if match else None

def fetch_sbdb(target, phys_par=True, full_precision=False, close_approach=False):
    """Fetch asteroid data from JPL SBDB API"""
    params = {"sstr": target}
    if phys_par:
        params["phys-par"] = 1
    if full_precision:
        params["full_prec"] = 1
    if close_approach:
        params["close_approach"] = 1

    resp = requests.get(API_BASE, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    # If API returns a list, take first entry
    if isinstance(data, list):
        if len(data) > 0:
            data = data[0]
        else:
            raise ValueError(f"No data returned for {target}")

    if not isinstance(data, dict):
        raise ValueError(f"Unexpected API response for {target}: {type(data)}")

    return data

def summarize_and_save(target, data):
    """Save JSON safely and print summary"""
    safe_target = re.sub(r"[^\w\-]+", "_", normalize_name(target).strip())
    fname = os.path.join(OUT_DIR, f"{safe_target}.json")

    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Safe dictionary extraction
    obj = data.get("object", {}) if isinstance(data.get("object", {}), dict) else {}
    orbit = data.get("orbit", {}) if isinstance(data.get("orbit", {}), dict) else {}
    phys = data.get("phys_par", {}) if isinstance(data.get("phys_par", {}), dict) else {}

    name = obj.get("fullname") or obj.get("designation") or target
    epoch = orbit.get("epoch")
    elements = orbit.get("elements", {}) if isinstance(orbit.get("elements", {}), dict) else {}
    a = elements.get("a")
    e = elements.get("e")
    i = elements.get("i")
    diam = phys.get("diameter") or phys.get("diam")

    print(f"--- {target} ---")
    print(f"Name: {name}")
    if epoch:
        print(f"Epoch: {epoch}")
    print(f"a (AU): {a}; e: {e}; i (deg): {i}")
    print(f"Diameter: {diam if diam else 'N/A'}")
    print(f"Saved raw JSON to: {fname}\n")

if __name__ == "__main__":
    targets = load_targets("targets.txt")
    if not targets:
        print("No targets loaded. Exiting.")
        exit(1)

    print(f"\nStarting to fetch {len(targets)} asteroids...\n")
    success_count = 0
    error_count = 0

    for i, t in enumerate(targets, 1):
        safe_t = normalize_name(t)
        safe_filename = re.sub(r"[^\w\-]+", "_", safe_t.strip())
        fname = os.path.join(OUT_DIR, f"{safe_filename}.json")

        if os.path.exists(fname):
            print(f"[{i}/{len(targets)}] Skipping {t} (already downloaded)")
            continue

        query_name = extract_numeric_id(t) or safe_t

        try:
            print(f"[{i}/{len(targets)}] Fetching {t} (query: {query_name})...")
            data = fetch_sbdb(query_name)
            summarize_and_save(t, data)
            success_count += 1
            time.sleep(0.2)
        except Exception as exc:
            print(f"Error fetching {t}: {exc}\n")
            error_count += 1
            time.sleep(1)

    print(f"\n{'='*50}")
    print(f"Completed!")
    print(f"Successfully fetched: {success_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*50}")
