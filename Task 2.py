import pandas as pd
import json
import re
import os

# ==============================================================
# Helper Functions
# ==============================================================

def normalize_text(val):
    """Remove spaces & special characters, keep only A–Z, a–z, 0–9."""
    return re.sub(r'[^A-Za-z0-9]', '', str(val))

def safe_lower(val):
    """Convert to lowercase safely."""
    if val is None or pd.isna(val):
        return None
    return str(val).strip().lower()


# ==============================================================
# Load Input Files (must be in SAME folder as script)
# ==============================================================

ZOO_FILE = "zoo.csv"
CLASS_FILE = "class.csv"
META_FILE = "auxiliary_metadata.json"

zoo = pd.read_csv(ZOO_FILE)
cls = pd.read_csv(CLASS_FILE)

with open(META_FILE, "r", encoding="utf-8") as f:
    meta_raw = json.load(f)

# ==============================================================
# 1. NAME NORMALIZATION (CSV)
# ==============================================================

# Normalize column names
zoo.columns = [normalize_text(c) for c in zoo.columns]
cls.columns = [normalize_text(c) for c in cls.columns]

# Normalize animal_name
zoo["animal_name"] = zoo["animal_name"].apply(normalize_text)
if "animal_name" in cls.columns:
    cls["animal_name"] = cls["animal_name"].apply(normalize_text)

# ==============================================================
# 2. FIX JSON INCONSISTENCIES
# ==============================================================

def fix_meta(entry):
    e = dict(entry)

    # Normalize animal_name
    e["animal_name"] = normalize_text(e.get("animal_name", ""))

    # ------ STANDARDIZE conservation_status ------
    cons_keys = ["conservation", "conservationStatus", "status", "conservation_status"]
    cons_val = None
    for k in cons_keys:
        if k in e:
            cons_val = e[k]
            if k != "conservation_status":
                e.pop(k, None)
    if cons_val is not None:
        e["conservation_status"] = safe_lower(cons_val)

    # ------ STANDARDIZE habitat → habitat_type ------
    habitat_keys = ["habitta", "habitats", "habitat", "habitat_type", "location"]
    habitat_val = None
    for k in habitat_keys:
        if k in e:
            habitat_val = e[k]
            if k != "habitat_type":
                e.pop(k, None)
    if habitat_val is not None:
        e["habitat_type"] = safe_lower(habitat_val)

    # Fix habitat values
    habitat_map = {
        "fresh water": "freshwater",
        "freshwater": "freshwater",
        "marine/coastal": "marine",
        "marine": "marine",
        "forest": "forest",
        "grassland": "grassland",
        "desert": "desert",
    }
    if "habitat_type" in e and e["habitat_type"] in habitat_map:
        e["habitat_type"] = habitat_map[e["habitat_type"]]

    # ------ STANDARDIZE diet ------
    diet_keys = ["diet", "diet_type", "food", "feeding"]
    diet_val = None
    for k in diet_keys:
        if k in e:
            diet_val = e[k]
            if k != "diet":
                e.pop(k, None)
    if diet_val is not None:
        e["diet"] = safe_lower(diet_val)

    # Fix typos
    diet_map = {
        "herbviore": "herbivore",
        "herbivore": "herbivore",
        "carnivor": "carnivore",
        "carnivore": "carnivore",
        "omnivor": "omnivore",
        "omnivore": "omnivore",
        "filterfeeder": "filter-feeder",
        "filter-feeder": "filter-feeder",
        "insectivore": "insectivore"
    }
    if "diet" in e and e["diet"] in diet_map:
        e["diet"] = diet_map[e["diet"]]

    return e


fixed_meta = [fix_meta(m) for m in meta_raw]
meta_df = pd.DataFrame(fixed_meta)
meta_df["animal_name"] = meta_df["animal_name"].apply(normalize_text)

# ==============================================================
# 3. MERGE ALL DATASETS
# ==============================================================

merged = zoo.merge(cls, on="animal_name", how="left", suffixes=("", "_cls"))
merged = merged.merge(meta_df, on="animal_name", how="left", suffixes=("", "_meta"))

# ==============================================================
# 4. HANDLE MISSING AUXILIARY DATA
# ==============================================================

required_aux_cols = ["diet", "habitat_type", "conservation_status"]
merged = merged.dropna(subset=required_aux_cols)

# ==============================================================
# 5. FEATURE ENGINEERING
# ==============================================================

# Feature 1: warm-blooded
# Explanation: mammals & birds → indicated by hair=1 or feathers=1
merged["warm_blooded"] = merged.apply(
    lambda r: 1 if (r.get("hair") == 1 or r.get("feathers") == 1) else 0,
    axis=1
)

# Feature 2: mobility_score
# Explanation: combines legs + tail + flight capability
merged["mobility_score"] = (
    merged["legs"].fillna(0)
    + merged["tail"].fillna(0)
    + merged["airborne"].fillna(0) * 2
)

# ==============================================================
# 6. SAVE FINAL OUTPUT
# ==============================================================

OUTPUT_FILE = "final_merged_cleaned_dataset.csv"
merged.to_csv(OUTPUT_FILE, index=False)

print("============================================================")
print(" CLEANING COMPLETE — FINAL FILE CREATED")
print(f" Saved as: {OUTPUT_FILE}")
print("============================================================")

