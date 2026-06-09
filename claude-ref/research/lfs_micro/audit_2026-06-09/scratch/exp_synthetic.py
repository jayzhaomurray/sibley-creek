# Audit experiments A-D: known-answer synthetic checks of run_wls / oaxaca_blinder /
# engine._compute_one_yoy. Read-only on production: only in-memory frames used.
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\jayzh\projects\macro-research-department")
sys.path.insert(0, str(ROOT))

from pipeline.lfs_micro.regression import run_wls, union_category_universe
from pipeline.lfs_micro.decompose import oaxaca_blinder
from pipeline.lfs_micro.engine import _compute_one_yoy
from pipeline.lfs_micro.spec import Spec

OK = []
FAIL = []


def check(name, cond, detail=""):
    (OK if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + ("  | " + detail if detail else ""))


def mk(n_m, n_f, wage_m, wage_f, w_m=1.0, w_f=1.0):
    """Two-group frame using 'gender' only. Baseline after sort = 'F'."""
    return pd.DataFrame({
        "wage": [wage_m] * n_m + [wage_f] * n_f,
        "weight": [w_m] * n_m + [w_f] * n_f,
        "gender": ["M"] * n_m + ["F"] * n_f,
    })


# ---------------- A1: pure composition shift, constant within-group wages -------
base = mk(500, 500, 20.0, 25.0)
curr = mk(800, 200, 20.0, 25.0)
rb = run_wls(base)
rc = run_wls(curr)
uni = union_category_universe(rb, rc)
rb = run_wls(base, category_universe=uni)
rc = run_wls(curr, category_universe=uni)
ob = oaxaca_blinder(rb, rc, ob_reference="base")

b_true = np.log(20.0) - np.log(25.0)
check("A1 coef recovery (base)", np.allclose(rb.coef, [np.log(25.0), b_true], atol=1e-10),
      f"coef={rb.coef}")
check("A1 col order", rb.col_names == ["intercept", "gender_M"])
comp_expected = (0.8 - 0.5) * b_true
check("A1 underlying == 0", abs(ob.underlying) < 1e-12, f"underlying={ob.underlying:.2e}")
check("A1 composition == dShare*beta", abs(ob.composition - comp_expected) < 1e-12,
      f"{ob.composition:.10f} vs {comp_expected:.10f}")
check("A1 C+U+I == total_fitted",
      abs(ob.composition + ob.underlying + ob.interaction - ob.total_fitted) < 1e-14)
check("A1 total_fitted == raw_mean (perfect fit)",
      abs(ob.total_fitted - ob.raw_mean_change) < 1e-12)
check("A1 group contribs sum to composition",
      abs(sum(ob.group_contributions.values()) - ob.composition) < 1e-14)

# ---------------- A2: pure wage growth, constant composition --------------------
base = mk(500, 500, 20.0, 25.0)
curr = mk(500, 500, 20.0 * 1.03, 25.0 * 1.03)
rb = run_wls(base); rc = run_wls(curr)
uni = union_category_universe(rb, rc)
rb = run_wls(base, category_universe=uni)
rc = run_wls(curr, category_universe=uni)
ob = oaxaca_blinder(rb, rc, ob_reference="base")
check("A2 underlying == log(1.03)", abs(ob.underlying - np.log(1.03)) < 1e-12,
      f"underlying={ob.underlying:.10f}")
check("A2 composition == 0", abs(ob.composition) < 1e-12)
check("A2 interaction == 0", abs(ob.interaction) < 1e-12)

# ---------------- A3: weights drive mean_X (survey-weighted shares) -------------
# equal row counts, but weight M rows 4x -> weighted share M = 0.8
base = mk(500, 500, 20.0, 25.0, w_m=1.0, w_f=1.0)
curr = mk(500, 500, 20.0, 25.0, w_m=4.0, w_f=1.0)
rb = run_wls(base); rc = run_wls(curr)
uni = union_category_universe(rb, rc)
rb = run_wls(base, category_universe=uni)
rc = run_wls(curr, category_universe=uni)
ob = oaxaca_blinder(rb, rc, ob_reference="base")
check("A3 weighted share via mean_X", abs(rc.mean_X[1] - 0.8) < 1e-12,
      f"mean_X[gender_M]={rc.mean_X[1]}")
check("A3 composition reflects weighted shares",
      abs(ob.composition - (0.8 - 0.5) * b_true) < 1e-12)

# ---------------- B: WLS coefficients vs normal-equations ground truth ----------
rng = np.random.default_rng(42)
n = 5000
df = pd.DataFrame({
    "gender": rng.choice(["M", "F"], n),
    "educ": rng.choice(["hs", "col", "uni"], n),
    "prov": rng.choice(["ON", "QC", "AB", "BC"], n),
    "weight": rng.uniform(0.5, 5.0, n),
})
logw = (3.0 + 0.1 * (df["gender"] == "M") + 0.2 * (df["educ"] == "uni")
        - 0.05 * (df["educ"] == "hs") + 0.07 * (df["prov"] == "AB")
        + rng.normal(0, 0.3, n))
df["wage"] = np.exp(logw)
res = run_wls(df)
# independent ground truth: solve (X'WX) b = X'Wy with hand-built design
# Column order follows REGRESSOR_GROUPS: educ before gender before prov.
X = np.column_stack([
    np.ones(n),
    (df["educ"] == "hs").astype(float),        # sorted: col, hs, uni -> baseline col
    (df["educ"] == "uni").astype(float),
    (df["gender"] == "M").astype(float),       # baseline F
    (df["prov"] == "BC").astype(float),        # sorted: AB,BC,ON,QC -> baseline AB
    (df["prov"] == "ON").astype(float),
    (df["prov"] == "QC").astype(float),
])
W = df["weight"].values
b_truth = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * logw))
expected_cols = ["intercept", "educ_hs", "educ_uni", "gender_M", "prov_BC", "prov_ON", "prov_QC"]
check("B col_names as expected", res.col_names == expected_cols, str(res.col_names))
check("B WLS coef == normal-equations truth", np.allclose(res.coef, b_truth, atol=1e-8),
      f"max|diff|={np.max(np.abs(res.coef - b_truth)):.2e}")
# weighted R2 ground truth
yhat = X @ b_truth
mlw = (W * logw).sum() / W.sum()
r2_truth = 1 - (W * (logw - yhat) ** 2).sum() / (W * (logw - mlw) ** 2).sum()
check("B weighted R2 matches", abs(res.r_squared - r2_truth) < 1e-10,
      f"{res.r_squared} vs {r2_truth}")

# ---------------- C: thin-category pruning row-alignment (the old bug) ----------
# Put 10 poison rows (wage=$1000, thin educ cat 'zz') at the TOP of the frame.
# If y/X alignment is right, fit on remaining rows must equal fit with poison
# rows never present.
rng = np.random.default_rng(7)
n = 2000
clean = pd.DataFrame({
    "gender": rng.choice(["M", "F"], n),
    "educ": rng.choice(["hs", "col", "uni"], n),
    "weight": rng.uniform(0.5, 5.0, n),
})
clean["wage"] = np.exp(3.0 + 0.1 * (clean["gender"] == "M")
                       + 0.2 * (clean["educ"] == "uni") + rng.normal(0, 0.3, n))
poison = pd.DataFrame({
    "gender": ["M"] * 10, "educ": ["zz"] * 10, "weight": [1.0] * 10,
    "wage": [1000.0] * 10,
})
with_poison = pd.concat([poison, clean], ignore_index=True)  # poison rows FIRST
res_p = run_wls(with_poison, min_cell_count=30)
res_c = run_wls(clean, min_cell_count=30)
check("C thin cat dropped", res_p.dropped_cells.get("educ") == ["zz"], str(res_p.dropped_cells))
check("C n_obs == clean n", res_p.n_obs == n, f"{res_p.n_obs}")
check("C coef identical to never-poisoned fit", np.allclose(res_p.coef, res_c.coef, atol=1e-12),
      f"max|diff|={np.max(np.abs(res_p.coef - res_c.coef)):.2e}")
check("C R2 identical to never-poisoned fit", abs(res_p.r_squared - res_c.r_squared) < 1e-12,
      f"r2={res_p.r_squared:.4f}")

# ---------------- D: category present in base, absent in curr (union -> all-zero col)
# Forces rank deficiency in curr month only; engine common-column pruning must
# keep the months conformable and the decomposition fail-closed-or-correct.
def mk3(n_a, n_b, n_c, wa, wb, wc):
    return pd.DataFrame({
        "wage": [wa] * n_a + [wb] * n_b + [wc] * n_c,
        "weight": 1.0,
        "educ": ["aa"] * n_a + ["bb"] * n_b + ["cc"] * n_c,
    })

base = mk3(400, 400, 200, 20.0, 25.0, 30.0)
curr = mk3(500, 500, 0, 20.0, 25.0, 30.0)   # 'cc' disappears
spec = Spec(weighted=True, smoothing="raw", ob_reference="base", min_cell_count=30)
row = _compute_one_yoy("2025-01", curr, base, spec)
check("D engine returns a row (not None)", row is not None)
if row is not None:
    # within-group wages constant -> underlying must be ~0 even with the
    # disappearing category (composition explains everything)
    check("D underlying ~ 0 under constant group wages", abs(row["underlying_lp"]) < 1e-10,
          f"underlying_lp={row['underlying_lp']:.2e}")
    tot = row["total_fitted_lp"]
    csum = row["underlying_lp"] + row["composition_lp"]
    # two-fold: total - (C+U) = interaction; here dB=0 so interaction=0
    check("D C+U == total (dB=0 -> no interaction)", abs(tot - csum) < 1e-10,
          f"total={tot:.6f} C+U={csum:.6f}")

print()
print(f"=== {len(OK)} passed, {len(FAIL)} failed ===")
if FAIL:
    print("FAILED:", FAIL)
