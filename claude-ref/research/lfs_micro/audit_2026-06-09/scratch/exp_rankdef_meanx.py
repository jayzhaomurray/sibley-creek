# Bug-3 isolation: when run_wls hits the internal rank-deficiency path with
# non-unit weights, mean_X must be the WEIGHTED CATEGORY SHARES computed from
# the UNSCALED pruned design (the old bug returned the sqrt(w)-scaled matrix).
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\jayzh\projects\macro-research-department")
sys.path.insert(0, str(ROOT))
from pipeline.lfs_micro.regression import run_wls

# Universe forces an all-zero column (educ 'cc' absent from df) -> rank deficient.
n = 900
rng = np.random.default_rng(3)
df = pd.DataFrame({
    "educ": ["aa"] * 300 + ["bb"] * 600,
    "weight": np.r_[np.full(300, 5.0), np.full(600, 1.0)],  # weighted share aa = 1500/2100
})
df["wage"] = np.where(df["educ"] == "aa", 20.0, 30.0) * np.exp(rng.normal(0, 0.05, n))
res = run_wls(df, category_universe={"educ": ["aa", "bb", "cc"]})

print("col_names:", res.col_names)
assert "educ_cc" not in res.col_names, "deficient all-zero column should be dropped"
share_bb = 600 * 1.0 / (300 * 5.0 + 600 * 1.0)
i = res.col_names.index("educ_bb")
print(f"mean_X[educ_bb] = {res.mean_X[i]:.6f}  expected weighted share = {share_bb:.6f}")
assert abs(res.mean_X[i] - share_bb) < 1e-12, "mean_X poisoned (scaled-matrix bug regressed)"
print(f"intercept mean_X = {res.mean_X[res.col_names.index('intercept')]:.6f} (must be 1.0)")
assert abs(res.mean_X[res.col_names.index("intercept")] - 1.0) < 1e-12
# coef sanity: intercept ~ log(20), educ_bb ~ log(30/20)
print(f"coef = {res.coef}, R2 = {res.r_squared:.4f}")
assert abs(res.coef[0] - np.log(20)) < 0.02 and abs(res.coef[i] - np.log(1.5)) < 0.02
assert res.r_squared > 0.8
print("PASS: rank-deficiency path returns unscaled-matrix shares; bug-3 fix is real")
