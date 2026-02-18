import os
import urllib.request
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

USDA_URL = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_csv_2024-10-31.zip"
USDA_DIR = os.path.join(RAW_DATA_DIR, "FoodData_Central_csv_2024-10-31")


def main():
    if not os.path.exists(USDA_DIR):
        print("Downloading USDA data...")
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        zip_path = os.path.join(RAW_DATA_DIR, "usda.zip")
        urllib.request.urlretrieve(USDA_URL, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(RAW_DATA_DIR)
        print("Done.")
    else:
        print("Data already downloaded.")


if __name__ == "__main__":
    main()