import cvxpy as cp
import numpy as np
import pandas as pd
import os

def load_foods():
    base = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(base, '..', '..', 'data', 'processed', 'clean_foods.parquet')
    foods = pd.read_parquet(parquet_path)
    foods = foods.set_index('description')
    foods = foods.drop(columns=['fdc_id', 'Energy'])
    foods = foods.rename(columns={'Calcium, Ca': 'Calcium', 'Carbohydrate, by difference': 'Carbs', 'Fiber, total dietary':'Fiber','Iron, Fe':'Iron', 'Magnesium, Mg': 'Magnesium', 'Potassium, K': 'Potassium', 'Sodium, Na': 'Salt', 'Sugars, total including NLEA': 'Sugars', 'Total lipid (fat)': 'Fats', 'Vitamin A, RAE': 'Vitamin A', 'Vitamin C, total ascorbic acid': 'Vitamin C', 'Vitamin D (D2 + D3)': 'Vitamin D', 'Vitamin K (phylloquinone)':'Vitamin K', 'Zinc, Zn': 'Zinc'})
    return foods

# Daily Value of nutritions based on https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels
def build_daily_recommended():
    return pd.Series([
        1300.0,   # Calcium (mg)
        275.0,    # Carbs (g)
        28.0,     # Fiber (g)
        18.0,     # Iron (mg)
        420.0,    # Magnesium (mg)
        4700.0,   # Potassium (mg)
        50.0,     # Protein (g)
        2300.0,   # Salt == Sodium (mg)
        50.0,     # Sugars (g)
        78.0,     # Fats (g)
        900.0,    # Vitamin A (µg RAE)
        90.0,     # Vitamin C (mg)
        20.0,     # Vitamin D (µg)
        120.0,    # Vitamin K (µg)
        11.0      # Zinc (mg)
    ],
    index=[
        "Calcium",
        "Carbs",
        "Fiber",
        "Iron",
        "Magnesium",
        "Potassium",
        "Protein",
        "Salt",
        "Sugars",
        "Fats",
        "Vitamin A",
        "Vitamin C",
        "Vitamin D",
        "Vitamin K",
        "Zinc"
    ])

def optimize(V, d, lam):
    n = len(V)
    x = cp.Variable(n)
    # L2 norm for accuracy, L1 norm for sparsity
    objective = cp.Minimize(cp.norm(V.values.T @ x - d, 2) + lam * cp.norm(x, 1))
    # Constraints: non-negative, max 500 grams
    constraints = [x >= 0, x <= 5]
    problem = cp.Problem(objective, constraints)
    problem.solve()
    return x.value