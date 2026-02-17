import json
import os

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "clean_foods.parquet")
NUTRIENTS_CONFIG = os.path.join(PROJECT_ROOT, "configs", "nutrients.json")


def load_csv(filename):
    path = os.path.join(RAW_DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"Error: {path} not found. Run scripts/1_dl_data.py first.")
        return None
    print(f"Loading {filename}...")
    return pd.read_csv(path, low_memory=False)


def main():
    # Load nutrient IDs from config
    with open(NUTRIENTS_CONFIG) as f:
        nutrient_config = json.load(f)
    nutrient_ids = [n["id"] for n in nutrient_config]
    nutrient_names = {n["id"]: n["name"] for n in nutrient_config}

    print(f"Tracking {len(nutrient_ids)} nutrients from config.")

    foods = load_csv("food.csv")
    nutrients = load_csv("food_nutrient.csv")

    if foods is None or nutrients is None:
        return

    print("Filtering relevant nutrients...")
    valid = nutrients[nutrients["nutrient_id"].isin(nutrient_ids)].copy()
    valid["col_name"] = valid["nutrient_id"].map(nutrient_names)

    print("Pivoting data...")
    matrix = valid.pivot_table(
        index="fdc_id",
        columns="col_name",
        values="amount",
        aggfunc="mean",
    )

    print("Merging with food descriptions...")
    food_info = foods[["fdc_id", "description"]].copy()
    clean = food_info.merge(matrix, left_on="fdc_id", right_index=True, how="inner")
    clean = clean.fillna(0)

    numeric_cols = clean.select_dtypes(include="number").columns
    clean = clean.groupby("description")[numeric_cols].mean().reset_index()

    clean = clean[clean["Energy"] > 0]
    # Drop rows with no meaningful nutrient data (all macros near zero)
    macro_cols = ["Energy", "Protein", "Carbohydrate, by difference", "Total lipid (fat)"]
    has_data = clean[macro_cols].sum(axis=1) > 1
    clean = clean[has_data]

    # Replace USDA energy with calculated Atwater energy
    clean["Energy"] = (
        4 * clean["Protein"]
        + 4 * clean["Carbohydrate, by difference"]
        + 9 * clean["Total lipid (fat)"]
    ).round(1)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print(f"Saving {len(clean)} foods to {OUTPUT_FILE}...")
    clean.to_parquet(OUTPUT_FILE, index=False)
    print("Done.")


if __name__ == "__main__":
    main()