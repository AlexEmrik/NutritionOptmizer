# Nutrition Optimizer

An idea spawned from a question that was asked while eating lunch outside of Packard. 

A simple, interactive nutrition optimizer using **CVXPY** and **Marimo**.

The data is modeled as follows:

$$V \in \mathbb{R}^{m \times n}, \quad d \in \mathbb{R}^{m}, \quad x \in \mathbb{R}^{n}$$

Where $V$ is the matrix of foods and their nutritional values, $d$ is the vector of daily recommended nutritional values, and $x$ is the vector of the amount of each food to consume. $n$ is the number of foods and $m$ is the number of nutritional values.

$$\min_{x} \sum_{i} L_{\tau_i}(V_i x - d_i) + \lambda \|x\|_1$$

$$\text{subject to} \quad x \geq 0$$

where $\tau$ is the vector of quantile values for each nutrient, and $L_{\tau}(r)$ is the pinball loss function defined as:

$$L_{\tau}(r) = \tau \max(r, 0) + (1-\tau) \max(-r, 0)$$


We minimize the error of the current weights and our nutritional needs and $\lambda$ is used as a convex relaxation of cardinality. The larger $\lambda$ is, the more sparse the solution will be.

--- 

## Data
- [USDA FoodData Central](https://fdc.nal.usda.gov/fdc-app.html#/downloads)

Datasets are not tracked on Git.

---

##  Core Workflow

0. If you don't have uv installed, run `make uv` to install it. We use `uv` to manage the Python environment.
1. Run `make setup` this sets up the Python environment (creates venv and installs dependencies).
2. Run `scripts/1_dl_data.py` once to download the raw USDA data.
3. Run `scripts/2_clean_data.py` once to clean the raw USDA data.
4. Run `marimo edit notebooks/notebook.py` to launch the interactive optimizer.
    1. This will open a browser window with the UI where you can set the amount of foods you want your diet to consist of and the optimizer will find the best combination of foods to meet your daily nutritional needs and show it in a table.
    
## Project Structure

```
├── src/
│   └── food_optimizer/
│       ├── __init__.py          # Package init
│       └── optimizer.py         # Core optimization logic
├── notebooks/
│   └── notebook.py              # Interactive Marimo app
├── scripts/
│   ├── 1_dl_data.py             # Download raw USDA data
│   └── 2_clean_data.py          # Clean raw USDA data
├── data/                        # Data directory
│   ├── raw/                     # Raw CSVs from USDA
│   └── processed/               # Cleaned data for the app
└── Makefile                     # Setup commands
```