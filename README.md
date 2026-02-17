# Nutrition Optimizer

An idea spawned from a question that was asked while eating lunch outside of Packard. 

A simple, interactive nutrition optimizer using **CVXPY** and **Marimo**.

--- 

## Data
- [USDA FoodData Central](https://fdc.nal.usda.gov/fdc-app.html#/downloads)

Datasets are not tracked on Git.

---

##  Core Workflow

0. If you don't have uv installed, run `make uv` to install it. We use `uv` to manage the Python environment.
1. Run `make setup` this sets up the Python environment (creates venv and installs dependencies).
2. Run `scripts/1_dl_data.py` once to download or setup all the necessary data.
3. Run `scripts/2_clean_data.py` once to process the raw data into `clean_foods.parquet`.
4. Run `marimo edit notebooks/notebook.py` to launch the interactive optimizer.
    1. This will open a browser window with the UI where you can set constraints and generate diets.

## Project Structure

```
├── src/
│   └── food_optimizer/
│       ├── __init__.py          # Package init
│       └── optimizer.py         # Core optimization logic
├── notebooks/
│   └── notebook.py              # Interactive Marimo app
├── scripts/
│   ├── 1_dl_data.py             # Download/Setup raw USDA data
│   └── 2_clean_data.py          # Process raw CSVs into clean_foods.parquet
├── configs/
│   ├── nutrients.json           # Nutrient definitions
│   ├── constraints.json         # Default min/max bounds
│   └── presets.json             # Bulk/Cut etc.
├── data/                        # Data directory
│   ├── raw/                     # Raw CSVs from USDA
│   └── processed/               # Cleaned data for the app
└── Makefile                     # Setup commands
```