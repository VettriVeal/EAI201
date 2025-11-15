# ------------------------------------------------------------
# UPDATE THESE 3 PATHS ONLY (PUT YOUR CORRECT FILE LOCATIONS)
# ------------------------------------------------------------

ZOO_FILE = r"C:/Users/ub13-glab-010/Downloads/zoo.csv"
CLASS_FILE = r"C:/Users/ub13-glab-010/Downloads/class.csv"
META_FILE = r"C:/Users/ub13-glab-010/Downloads/auxiliary_metadata.json"

# ------------------------------------------------------------
# DO NOT EDIT BELOW THIS LINE
# ------------------------------------------------------------

import pandas as pd
import numpy as np
import json
import re
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

def normalize_text(val):
    return re.sub(r'[^A-Za-z0-9]', '', str(val))

def safe_lower(val):
    if val is None or pd.isna(val): return None
    return str(val).strip().lower()


# ---------------- Load Files ------------------

zoo = pd.read_csv(ZOO_FILE)
cls = pd.read_csv(CLASS_FILE)

with open(META_FILE, "r") as f:
    meta_raw = json.load(f)


# ---------------- Normalize Zoo ------------------

if "animal_name" in zoo.columns:
    zoo["animal_name"] = zoo["animal_name"].apply(normalize_text)
else:
    zoo["animal_name"] = zoo[zoo.columns[0]].apply(normalize_text)


# ---------------- Process class.csv ------------------

class_type_col = None
class_names_col = None

for c in cls.columns:
    key = normalize_text(c).lower()
    if key in ("classtype", "class", "classtypename"):
        class_type_col = c
    if "animal" in key or "name" in key:
        class_names_col = c

rows = []
for _, r in cls.iterrows():
    ctype = str(r[class_type_col])
    names = str(r[class_names_col])
    parts = [p.strip() for p in names.split(",") if p.strip()]
    for name in parts:
        rows.append({
            "animal_name": normalize_text(name),
            "class_type": ctype
        })

class_map = pd.DataFrame(rows)


# ---------------- Clean JSON metadata ------------------

def fix_meta(d):
    new = {}

    # find name
    name_val = None
    for k in d.keys():
        if "name" in k.lower():
            name_val = d[k]
            break
    if name_val is None:
        return None

    new["animal_name"] = normalize_text(name_val)

    # conservation
    for key in ["conservation", "conservation_status", "status"]:
        if key in d:
            new["conservation_status"] = safe_lower(d[key])
            break

    # habitat
    for key in ["habitat", "habitats", "habitta", "location"]:
        if key in d:
            val = safe_lower(d[key])
            if val:
                if "fresh" in val:
                    val = "freshwater"
                elif "marine" in val:
                    val = "marine"
                elif "forest" in val:
                    val = "forest"
                elif "grass" in val:
                    val = "grassland"
            new["habitat_type"] = val
            break

    # diet
    for key in ["diet", "diet_type", "food"]:
        if key in d:
            val = safe_lower(d[key])
            diet_fix = {
                "herbviore": "herbivore",
                "herbivore": "herbivore",
                "carnivor": "carnivore",
                "carnivore": "carnivore",
                "omnivor": "omnivore",
                "omnivore": "omnivore",
                "filterfeeder": "filter-feeder"
            }
            new["diet"] = diet_fix.get(val, val)
            break

    return new

meta_df = pd.DataFrame([m for m in (fix_meta(x) for x in meta_raw) if m])


# ---------------- Merge datasets ------------------

df = zoo.merge(class_map, on="animal_name", how="left")
df = df.merge(meta_df, on="animal_name", how="left")


# ---------------- Feature Engineering ------------------

df["warm_blooded"] = df.apply(
    lambda r: 1 if (r.get("hair") == 1 or r.get("feathers") == 1) else 0, axis=1
)

df["mobility_score"] = (
    df["legs"].fillna(0)
    + df["tail"].fillna(0)
    + df["airborne"].fillna(0) * 2
)


# ---------------- Drop missing auxiliary data ------------------

aux_cols = ["diet", "habitat_type", "conservation_status"]
df_clean = df.dropna(subset=aux_cols)


# ---------------- Stats ------------------

class_counts = df_clean["class_type"].value_counts()
imbalance_ratio = class_counts.max() / class_counts.min()

num_cols = df_clean.select_dtypes(include=[np.number]).columns
variances = df_clean[num_cols].var()
low_variance = variances[variances < 0.01].index.tolist()

corr = df_clean[num_cols].corr()
high_corr_pairs = []
for i in range(len(num_cols)):
    for j in range(i + 1, len(num_cols)):
        c = corr.iloc[i, j]
        if abs(c) > 0.8:
            high_corr_pairs.append((num_cols[i], num_cols[j], c))


# ---------------- Plots ------------------

# 1. Bar plot
plt.figure(figsize=(8, 5))
plt.bar(class_counts.index, class_counts.values)
plt.title("Class Counts with Error Bars")
plt.xticks(rotation=45)
plt.savefig("class_counts_errorbar.png")
plt.close()

# 2. Hexbin
top = class_counts.index[:6]
fig, ax = plt.subplots(2, 3, figsize=(15, 8))
ax = ax.flatten()
for i, c in enumerate(top):
    sub = df_clean[df_clean["class_type"] == c]
    if len(sub) < 5:
        ax[i].text(0.5, 0.5, "Too few points", ha="center")
    else:
        hb = ax[i].hexbin(sub["legs"], sub["mobility_score"], gridsize=20)
    ax[i].set_title(c)
plt.savefig("hexbin_legs_mobility_by_class.png")
plt.close()

# 3. Swarm-like
plt.figure(figsize=(10, 6))
pos = {c: i for i, c in enumerate(class_counts.index)}
for _, r in df_clean.iterrows():
    plt.scatter(pos[r["class_type"]] + np.random.normal(0, 0.08),
                r["mobility_score"], s=20, alpha=0.6)
plt.xticks(range(len(pos)), pos.keys(), rotation=45)
plt.savefig("swarm_like_mobility_by_class.png")
plt.close()

# 4. Clustermap-like heatmap
corr = df_clean[num_cols].corr()
dist = 1 - corr.abs()
dist_matrix = dist.values.copy()
np.fill_diagonal(dist_matrix, 0)
dist_matrix = (dist_matrix + dist_matrix.T) / 2
Z = linkage(squareform(dist_matrix), method="average")
order = leaves_list(Z)
ordered_cols = corr.columns[order]
ordered_corr = corr.loc[ordered_cols, ordered_cols]

plt.figure(figsize=(10, 8))
plt.imshow(ordered_corr.values)
plt.xticks(range(len(ordered_cols)), ordered_cols, rotation=90)
plt.yticks(range(len(ordered_cols)), ordered_cols)
plt.colorbar()
plt.savefig("clustermap_like_heatmap.png")
plt.close()


print("\nProcessing complete! All plots saved.")
