import marimo

__generated_with = "0.1.0"
app = marimo.App()

@app.cell
def __(mo):
    num_ingredients = mo.ui.slider(3, 12, value=6, label="Max number of ingredients")
    num_ingredients
    return num_ingredients,

@app.cell
def __():
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
    
    import marimo as mo
    import pandas as pd
    from food_optimizer.optimizer import load_foods, build_daily_recommended, optimize
    return mo, pd, load_foods, build_daily_recommended, optimize

@app.cell
def __(load_foods, build_daily_recommended, optimize, num_ingredients):
    V = load_foods()
    d = build_daily_recommended()
    if num_ingredients.value == 3:
        lam = 500
    elif num_ingredients.value == 4:
        lam = 200
    elif num_ingredients.value == 5:
        lam = 100
    elif num_ingredients.value == 6:
        lam = 50
    elif num_ingredients.value == 7:
        lam = 30
    elif num_ingredients.value == 8:
        lam = 20
    elif num_ingredients.value == 9:
        lam = 15
    elif num_ingredients.value == 10:
        lam = 12
    elif num_ingredients.value == 11:
        lam = 7
    elif num_ingredients.value == 12:
        lam = 6
    x_val = optimize(V, d, lam=lam)
    return V, d, x_val

@app.cell
def __(V, x_val, pd):
    totals = pd.Series(0.0, index=V.columns)
    results = []
    for i, val in enumerate(x_val):
        if val > 0.05:
            name = V.index[i]
            grams = val * 100
            results.append({"food": name, "grams": round(grams)})
            totals += V.iloc[i] * val
    return results, totals

@app.cell
def __(results, totals, d, mo, pd):
    calories = totals['Protein'] * 4 + totals['Carbs'] * 4 + totals['Fats'] * 9

    foods_table = mo.ui.table(pd.DataFrame(results))

    macro_cols = ["Protein", "Carbs", "Fats"]
    macro_data = pd.DataFrame({
        "nutrient": macro_cols,
        "total": [round(totals[c], 1) for c in macro_cols],
        "% of DRI": [round(totals[c] / d[c] * 100, 1) for c in macro_cols]
    })

    micro_cols = ["Calcium", "Fiber", "Iron", "Magnesium", "Potassium", "Salt", "Sugars", "Vitamin A", "Vitamin C", "Vitamin D", "Vitamin K", "Zinc"]
    micro_data = pd.DataFrame({
        "nutrient": micro_cols,
        "total": [round(totals[c], 1) for c in micro_cols],
        "% of DRI": [round(totals[c] / d[c] * 100, 1) for c in micro_cols]
    })

    mo.vstack([
        mo.stat(label="Total Calories", value=f"{round(calories)} kcal"),
        foods_table,
        mo.ui.table(macro_data),
        mo.ui.table(micro_data, page_size=12),
    ])
    return

if __name__ == "__main__":
    app.run()