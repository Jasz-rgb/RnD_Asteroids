import os
import json
import requests
import time

API_BASE = "https://ssd-api.jpl.nasa.gov/sbdb.api"
OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

def load_targets(filename="targets.txt"):
    """Load asteroid targets from a text file (one per line)"""
    targets = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Skip empty lines and comments
                    targets.append(line)
        print(f"Loaded {len(targets)} targets from {filename}")
        return targets
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return []

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

    # If API returns a list, pick the first object
    if isinstance(data, list):
        if len(data) > 0:
            data = data[0]
        else:
            raise ValueError(f"No data returned for {target}")
    return data

def summarize_and_save(target, data):
    """Save JSON and print summary"""
    fname = os.path.join(OUT_DIR, f"{target.replace(' ','_')}.json")
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    obj = data.get("object", {}) or {}
    orbit = data.get("orbit", {}) or {}
    phys = data.get("phys_par", {}) or {}

    name = obj.get("fullname") or obj.get("designation") or target
    epoch = orbit.get("epoch")
    elements = orbit.get("elements", {})
    a = elements.get("a")     # semi-major axis (AU)
    e = elements.get("e")     # eccentricity
    i = elements.get("i")     # inclination (deg)
    diam = phys.get("diameter") or phys.get("diam")  # some entries use different keys

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
        fname = os.path.join(OUT_DIR, f"{t.replace(' ','_')}.json")
        if os.path.exists(fname):
            print(f"[{i}/{len(targets)}] Skipping {t} (already downloaded)")
            continue

        try:
            print(f"[{i}/{len(targets)}] Fetching {t}...")
            data = fetch_sbdb(t)
            summarize_and_save(t, data)
            success_count += 1
            time.sleep(0.2)  # slight delay to be polite to API
        except Exception as exc:
            print(f"Error fetching {t}: {exc}\n")
            error_count += 1
            time.sleep(1)  # wait a bit before retrying next asteroid
    
    print(f"\n{'='*50}")
    print(f"Completed!")
    print(f"Successfully fetched: {success_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*50}")
