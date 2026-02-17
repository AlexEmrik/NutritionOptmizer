import os
import zipfile
import urllib.request

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

USDA_URL = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_csv_2024-10-31.zip"
ZIP_NAME = "usda_foundation_foods.zip"

REQUIRED_FILES = ["food.csv", "food_nutrient.csv", "nutrient.csv"]


def main():
    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    missing = [f for f in REQUIRED_FILES if not os.path.exists(os.path.join(DATA_RAW_DIR, f))]

    if not missing:
        print("All required files already present.")
        return

    print(f"Missing: {missing}")
    zip_path = os.path.join(DATA_RAW_DIR, ZIP_NAME)

    print(f"Downloading from USDA FoodData Central...")
    urllib.request.urlretrieve(USDA_URL, zip_path)
    print("Download complete.")
    print("Extracting...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        for f in REQUIRED_FILES:
            for name in zf.namelist():
                if name.endswith("/" + f):
                    with zf.open(name) as src, open(os.path.join(DATA_RAW_DIR, f), "wb") as dst:
                        dst.write(src.read())
                    print(f"  Extracted {f}")
                    break
        os.remove(zip_path)
        print("Done.")


if __name__ == "__main__":
    main()