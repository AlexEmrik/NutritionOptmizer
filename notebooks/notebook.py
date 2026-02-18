import marimo

__generated_with = "0.1.0"
app = marimo.App()

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
def __(mo):
    num_ingredients = mo.ui.slider(3, 12, value=6, label="Max number of ingredients")
    num_ingredients
    return num_ingredients,

@app.cell
def __(load_foods, build_daily_recommended, optimize, num_ingredients):
    V = load_foods()
    d = build_daily_recommended()
    lam = 100 / num_ingredients.value
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

    macro_cols = ["Protein", "Carbs", "Fats", "Saturated Fat", "Cholesterol", "Sugars", "Fiber"]
    macro_data = pd.DataFrame({
        "nutrient": macro_cols,
        "total": [round(totals[c], 1) for c in macro_cols],
        "DRI": [round(d[c], 1) for c in macro_cols],
        "% of DRI": [round(totals[c] / d[c] * 100, 1) for c in macro_cols]
    })

    micro_cols = ["Calcium", "Iron", "Magnesium", "Vitamin A", "Vitamin C", "Vitamin D", "Vitamin B6", "Vitamin B12"]
    micro_data = pd.DataFrame({
        "nutrient": micro_cols,
        "total": [round(totals[c], 1) for c in micro_cols],
        "% of DRI": [round(totals[c] / d[c] * 100, 1) for c in micro_cols]
    })

    mo.vstack([
        mo.stat(label="Total Calories", value=f"{round(calories)} kcal"),
        mo.ui.table(pd.DataFrame(results)),
        mo.ui.table(macro_data),
        mo.ui.table(micro_data),
    ])
    return

if __name__ == "__main__":
    app.run()