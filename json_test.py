import os
import json

folder = "sbdb_data"
asteroid_data = []

for file in os.listdir(folder):
    if file.endswith(".json"):
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            data = json.load(f)

        obj = data.get("object", {})
        orbit = data.get("orbit", {})
        phys_par = data.get("phys_par", [])

        # Extract orbital elements
        elements = orbit.get("elements", [])
        elem_dict = {e["name"]: float(e["value"]) for e in elements if "value" in e}

        # Extract physical parameters
        phys_dict = {}
        for p in phys_par:
            if p["name"] in ["diameter", "rot_per", "albedo"]:
                try:
                    phys_dict[p["name"]] = float(p["value"])
                except:
                    phys_dict[p["name"]] = None

        asteroid_data.append({
            "name": obj.get("fullname") or obj.get("shortname") or file.replace(".json",""),
            "orbit": elem_dict,
            "phys": phys_dict
        })

# Save combined file
with open("asteroids_master.json", "w", encoding="utf-8") as f:
    json.dump(asteroid_data, f, indent=2)

print("Combined asteroid data saved to asteroids_master.json")
