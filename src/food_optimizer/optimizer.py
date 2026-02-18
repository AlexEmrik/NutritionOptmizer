import cvxpy as cp
import pandas as pd
import numpy as np
import os

def load_foods():
    base = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(base, '..', '..', 'data', 'processed', 'clean_foods.parquet')
    foods = pd.read_parquet(parquet_path)
    foods = foods.set_index('description')
    foods = foods.drop(columns=['fdc_id'])
    return foods

def build_daily_recommended():
    return pd.Series([
        78.0,     # Fats (g)
        20.0,     # Saturated Fat (g)
        300.0,    # Cholesterol (mg)
        275.0,    # Carbs (g)
        28.0,     # Fiber (g)
        50.0,     # Protein (g)
        50.0,     # Sugars (g)
        5000.0,   # Vitamin A (IU)
        90.0,     # Vitamin C (mg)
        20.0,     # Vitamin D (µg)
        2.0,      # Vitamin B6 (mg)
        6.0,      # Vitamin B12 (µg)
        1300.0,   # Calcium (mg)
        18.0,     # Iron (mg)
        420.0,    # Magnesium (mg)
    ],
    index=[
        "Fats", "Saturated Fat", "Cholesterol", "Carbs", "Fiber",
        "Protein", "Sugars", "Vitamin A", "Vitamin C", "Vitamin D",
        "Vitamin B6", "Vitamin B12", "Calcium", "Iron", "Magnesium",
    ])
taus = np.array([
    0.8,   # Fats
    0.3,   # Saturated Fat
    0.8,   # Cholesterol
    0.5,   # Carbs
    0.5,   # Fiber
    0.8,   # Protein
    0.2,   # Sugars 
    0.5,   # Vitamin A
    0.5,   # Vitamin C
    0.5,   # Vitamin D
    0.5,   # Vitamin B6
    0.5,   # Vitamin B12
    0.5,   # Calcium
    0.5,   # Iron
    0.5,   # Magnesium
])

def pinball(r, taus):
    return cp.sum(cp.multiply(taus, cp.pos(r)) + cp.multiply(1 - taus, cp.neg(r)))

def optimize(V, d, lam):
    n = len(V)
    x = cp.Variable(n)
    residual = V.values.T @ x - d
    objective = cp.Minimize(pinball(residual, taus) + lam * cp.norm(x, 1))
    constraints = [
        x >= 0,
        #V['Sugars'].values @ x <= 0.5,
       # V['Saturated Fat'].values @ x <= 0.2,
        #V['Cholesterol'].values @ x <= 3
    ]
    problem = cp.Problem(objective, constraints)
    problem.solve()
    return x.value