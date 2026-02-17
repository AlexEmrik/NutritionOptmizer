import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import json
    import os

    from food_optimizer.optimizer import DietOptimizer

    return DietOptimizer, json, mo, os, pd


@app.cell(hide_code=True)
def _(DietOptimizer, json, os, pd):
    def get_path(path):
        if os.path.exists(path):
            return path
        up_path = os.path.join("..", path)
        if os.path.exists(up_path):
            return up_path
        return path

    foods = pd.read_parquet(get_path("data/processed/clean_foods.parquet"))

    with open(get_path("configs/constraints.json"), "r") as f:
        default_constraints = json.load(f)

    with open(get_path("configs/presets.json"), "r") as f:
        presets = json.load(f)

    with open(get_path("configs/nutrients.json"), "r") as f:
        nutrients_config = json.load(f)

    optimizer = DietOptimizer(foods)

    return default_constraints, nutrients_config, optimizer, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Diet Optimizer

        Find an optimal combination of foods that meets your nutritional targets.
        Pick a **preset** or select **Custom** to fine-tune constraints.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo, presets):
    preset_names = ["Custom"] + list(presets.keys())
    preset_dropdown = mo.ui.dropdown(
        options=preset_names,
        value=preset_names[1] if len(preset_names) > 1 else "Custom",
        label="Preset",
    )

    max_ingredients = mo.ui.slider(
        start=3, stop=25, step=1, value=10, label="Max ingredients"
    )

    mo.vstack(
        [
            mo.md("### Settings"),
            mo.hstack(
                [preset_dropdown, max_ingredients],
                justify="start",
                gap=1,
            ),
        ]
    )
    return max_ingredients, preset_dropdown


@app.cell(hide_code=True)
def _(default_constraints, mo, nutrients_config, preset_dropdown, presets):
    selected = preset_dropdown.value

    def _build(base):
        _sliders = {}
        for _nutrient, _bounds in base.items():
            lo = _bounds.get("min") or 0
            hi = _bounds.get("max")
            if hi is None or hi == 0:
                hi = lo * 3 if lo > 0 else 1000
            max_stop = int(hi * 2) if int(hi * 2) > 100 else 100
            step_size = int(hi / 100) if int(hi / 100) > 0 else 1
            _sliders[_nutrient] = mo.ui.range_slider(
                start=0,
                stop=max_stop,
                step=step_size,
                value=[int(lo), int(hi)],
                label=_nutrient,
            )
        return _sliders

    cat_map = {n["name"]: n.get("category", "Other") for n in nutrients_config}

    def _grouped_ui(slider_dict):
        groups = {}
        for _sname, _slider in slider_dict.items():
            cat = cat_map.get(_sname, "Other")
            groups.setdefault(cat, []).append(_slider)
        sections = []
        for cat, cat_sliders in groups.items():
            sections.append(mo.md(f"**{cat}**"))
            sections.append(mo.hstack(cat_sliders, wrap=True, gap=0.5))
        return sections

    if selected == "Custom":
        sliders = _build(default_constraints)
        constraints_output = mo.vstack(
            [mo.md("### Custom Constraints")] + _grouped_ui(sliders)
        )
    else:
        merged = {k: dict(v) for k, v in default_constraints.items()}
        if selected in presets:
            for _pk, _pv in presets[selected].get("constraints", {}).items():
                if _pk in merged:
                    merged[_pk].update(_pv)
                else:
                    merged[_pk] = _pv
        sliders = _build(merged)
        constraints_output = mo.md("")

    constraints_output
    return (sliders,)


@app.cell(hide_code=True)
def _(max_ingredients, optimizer, sliders):
    def _get_constraints():
        return {
            _nutrient: {"min": _val.value[0], "max": _val.value[1]}
            for _nutrient, _val in sliders.items()
        }

    result = optimizer.solve(
        constraints=_get_constraints(),
        max_ingredients=max_ingredients.value,
    )
    return (result,)


@app.cell(hide_code=True)
def _(mo, nutrients_config, pd, result, sliders):
    def _build_nutrient_table(nutrient_totals):
        nutrient_units = {n["name"]: n["unit"] for n in nutrients_config}
        rows = []
        for _nname, _nvalue in sorted(nutrient_totals.items()):
            if _nname in nutrient_units:
                _bounds = sliders.get(_nname)
                lo = _bounds.value[0] if _bounds is not None else 0
                hi = _bounds.value[1] if _bounds is not None else _nvalue
                mid = (lo + hi) / 2.0 if (lo + hi) > 0 else 1
                rows.append(
                    {
                        "Nutrient": _nname,
                        "Actual": round(_nvalue, 1),
                        "Target": round(mid, 1),
                        "Min": lo,
                        "Max": hi,
                        "Unit": nutrient_units[_nname],
                        "% of Target": round(_nvalue / mid * 100, 1) if mid > 0 else 0,
                    }
                )
        return pd.DataFrame(rows)

    if result["status"] == "Optimal":
        diet = result["diet"]
        nutrients = result["nutrients"]

        display_diet = diet[["description", "amount_grams"]].copy()
        display_diet["calories"] = (diet["Energy"] * diet["amount_grams"] / 100).round(0)
        display_diet.columns = ["Food", "Amount (g)", "Calories"]
        display_diet["Amount (g)"] = display_diet["Amount (g)"].round(1)
        display_diet = display_diet.sort_values("Calories", ascending=False)
        display_diet = display_diet.reset_index(drop=True)

        n_foods = len(display_diet)
        nutrient_df = _build_nutrient_table(nutrients)
        nutrient_df_macros = nutrient_df[nutrient_df["Nutrient"].isin(["Protein", "Carbohydrate, by difference", "Total lipid (fat)"])]
        nutrient_df_macros = nutrient_df_macros.drop(columns=["Min", "Max", "Unit"]).reset_index(drop=True)
        nutrient_df_macros.rename(columns={'Carbohydrate, by difference':'Carbs', 'Total lipid (fat)':'Fat', 'Actual':'Amount (g)', 'Target':'Target (g)'}, inplace=True)

        nutrient_df_micros = nutrient_df[~nutrient_df["Nutrient"].isin(
            ["Energy", "Protein", "Carbohydrate, by difference", "Total lipid (fat)"]
        )].reset_index(drop=True)
        total_cal = display_diet["Calories"].sum()

        results_output = mo.vstack(
            [
                mo.md(f"### Results — {n_foods} foods, {total_cal:.0f} kcal"),
                mo.md("#### Food Breakdown"),
                mo.ui.table(display_diet, selection=None),
                mo.accordion(
                    {"Macros": mo.ui.table(nutrient_df_macros, selection=None)},
                ),
                mo.accordion(
                    {"Nutrient Details": mo.ui.table(nutrient_df_micros, selection=None)}
                ),
            ]
        )
    else:
        results_output = mo.callout(
            mo.md(
                f"**No solution found** (status: {result['status']})\n\n"
                "Try relaxing constraints or allowing more ingredients."
            ),
            kind="warn",
        )

    results_output
    return


if __name__ == "__main__":
    app.run()