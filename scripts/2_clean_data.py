import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "clean_foods.parquet")
USDA_DIR = os.path.join(RAW_DATA_DIR, "FoodData_Central_csv_2024-10-31")

NUTRIENTS = [
    'Total lipid (fat)',
    'Fatty acids, total saturated',
    'Cholesterol',
    'Carbohydrate, by difference',
    'Fiber, total dietary',
    'Protein',
    'Total Sugars',
    'Vitamin A, IU',
    'Vitamin C, total ascorbic acid',
    'Vitamin D (D2 + D3)',
    'Vitamin B-6',
    'Vitamin B-12',
    'Calcium, Ca',
    'Iron, Fe',
    'Magnesium, Mg',
]

RENAME = {
    'Total lipid (fat)': 'Fats',
    'Fatty acids, total saturated': 'Saturated Fat',
    'Carbohydrate, by difference': 'Carbs',
    'Fiber, total dietary': 'Fiber',
    'Total Sugars': 'Sugars',
    'Vitamin A, IU': 'Vitamin A',
    'Vitamin C, total ascorbic acid': 'Vitamin C',
    'Vitamin D (D2 + D3)': 'Vitamin D',
    'Vitamin B-6': 'Vitamin B6',
    'Vitamin B-12': 'Vitamin B12',
    'Calcium, Ca': 'Calcium',
    'Iron, Fe': 'Iron',
    'Magnesium, Mg': 'Magnesium',
}

EXCLUDE_PATTERNS = [
    'Powder',
    'Babyfood',
    'Formula',
    'Beverage,',
    'Beverages',
    'Low calorie',
    'Sugarless',
    'Cereals ready-to-eat',
    'Candies',
    'Spices',
    'Sugar free',
]


def main():
    food = pd.read_csv(os.path.join(USDA_DIR, "food.csv"), low_memory=False)
    nutrients = pd.read_csv(os.path.join(USDA_DIR, "food_nutrient.csv"), low_memory=False)
    nutrient_names = pd.read_csv(os.path.join(USDA_DIR, "nutrient.csv"), low_memory=False)

    nutrient_map = dict(zip(nutrient_names["id"], nutrient_names["name"]))
    matrix = nutrients.pivot_table(index="fdc_id", columns="nutrient_id", values="amount", aggfunc="mean")
    matrix.columns = [nutrient_map.get(c, c) for c in matrix.columns]

    clean = food[["fdc_id", "description"]].merge(matrix[NUTRIENTS], left_on="fdc_id", right_index=True, how="inner")
    clean = clean.dropna(subset=NUTRIENTS)
    clean = clean.rename(columns=RENAME)
    clean = clean.groupby("description").mean(numeric_only=True).reset_index()

    pattern = '|'.join(EXCLUDE_PATTERNS)
    clean = clean[~clean['description'].str.contains(pattern, na=False, case=False)]    

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    clean.to_parquet(OUTPUT_FILE, index=False)
    print(f"Saved {len(clean)} foods to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()