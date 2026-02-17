import cvxpy as cp
import pandas as pd
import numpy as np


class DietOptimizer:
    def __init__(self, foods_df):
        self.foods = foods_df.copy()
        if "fdc_id" in self.foods.columns:
            self.foods = self.foods.set_index("fdc_id")
        self.numeric_cols = self.foods.select_dtypes(include=[np.number]).columns.tolist()

        # Pre-compute nutrient density score
        nutrient_count = np.zeros(len(self.foods))
        for col in self.numeric_cols:
            vals = np.nan_to_num(self.foods[col].values, nan=0.0)
            nutrient_count += (vals > 0).astype(float)
        max_count = max(nutrient_count.max(), 1)
        self.density_penalty = 1.0 - (nutrient_count / max_count)

    HARD_CONSTRAINTS = {
        "Energy",
        "Protein",
        "Total lipid (fat)",
        "Carbohydrate, by difference",
    }

    PRIORITIES = {
        "Energy": 10.0,
        "Protein": 5.0,
        "Total lipid (fat)": 5.0,
        "Carbohydrate, by difference": 5.0,
        "Fiber, total dietary": 2.0,
        "Sugars, total including NLEA": 2.0,
    }

    def solve(self, constraints, max_ingredients=15, min_portion_grams=1):
        """
        Solve the diet problem.

        1. Solve full LP with hard constraints on energy+macros, soft on micros.
        2. Trim to top N foods by weight.
        3. Scale portions to hit calorie target (preserving ratios).
        """
        n_foods = len(self.foods)
        x = cp.Variable(n_foods, nonneg=True)

        cons = []
        deviations = []

        energy_min = None
        energy_max = None

        for nutrient, bounds in constraints.items():
            col = self._find_column(nutrient)
            if not col:
                continue

            values = np.nan_to_num(self.foods[col].values, nan=0.0)
            total = values @ x

            lo = bounds.get("min")
            hi = bounds.get("max")

            if nutrient == "Energy":
                energy_min = lo
                energy_max = hi

            # Hard constraints for energy + macros
            if nutrient in self.HARD_CONSTRAINTS:
                if lo is not None:
                    cons.append(total >= lo)
                if hi is not None:
                    cons.append(total <= hi)
            else:
                # Soft constraints for micros
                if lo is not None:
                    deviations.append(0.5 * cp.pos(lo - total) / max(lo, 1.0))
                if hi is not None:
                    deviations.append(0.5 * cp.pos(total - hi) / max(hi, 1.0))

            # Deviation from midpoint
            weight = self.PRIORITIES.get(nutrient, 1.0)
            if lo is not None and hi is not None:
                mid = (lo + hi) / 2.0
                span = hi - lo if hi > lo else 1.0
                deviations.append(weight * cp.abs(total - mid) / span)
            elif lo is not None:
                deviations.append(weight * cp.abs(total - lo * 1.1) / max(lo, 1.0))
            elif hi is not None:
                deviations.append(weight * cp.abs(total - hi * 0.5) / max(hi, 1.0))

        # Objective: hit nutrient targets + prefer nutrient-dense foods
        obj_terms = []
        if deviations:
            obj_terms.append(cp.sum(deviations))
        obj_terms.append(0.5 * self.density_penalty @ x)

        obj = cp.Minimize(sum(obj_terms))
        prob = cp.Problem(obj, cons)

        try:
            prob.solve(solver=cp.CLARABEL, verbose=False)
        except Exception:
            try:
                prob.solve(verbose=False)
            except Exception:
                return {"status": "Solver error", "diet": pd.DataFrame(), "nutrients": {}}

        if prob.status not in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
            return {"status": prob.status, "diet": pd.DataFrame(), "nutrients": {}}

        quantities = x.value
        grams = quantities * 100

        # Keep foods above minimum
        mask = grams >= min_portion_grams
        result_df = self.foods[mask].copy()
        result_df["amount_grams"] = grams[mask]

        # Trim to top N if needed
        if max_ingredients is not None and len(result_df) > max_ingredients:
            result_df = result_df.nlargest(max_ingredients, "amount_grams")

        # Scale to hit calorie target if we lost calories from trimming
        if energy_min is not None and "Energy" in result_df.columns:
            current_cal = (result_df["Energy"] * result_df["amount_grams"] / 100).sum()
            if current_cal > 0 and current_cal < energy_min:
                scale = energy_min / current_cal
                # Don't exceed calorie max
                if energy_max is not None:
                    scale = min(scale, energy_max / current_cal)
                result_df["amount_grams"] = result_df["amount_grams"] * scale

        # Calculate final nutrient totals
        totals = {}
        for col in self.numeric_cols:
            if col in result_df.columns:
                totals[col] = float(
                    (result_df[col] * result_df["amount_grams"] / 100).sum()
                )

        return {"status": "Optimal", "diet": result_df, "nutrients": totals}

    def _find_column(self, name):
        if name in self.foods.columns:
            return name
        return None