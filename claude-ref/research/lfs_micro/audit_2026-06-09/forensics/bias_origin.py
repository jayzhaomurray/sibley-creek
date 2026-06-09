# Chase the +0.088pp systematic bias: conversion convention, composition link,
# AR structure, worst-year inspection. READ-ONLY.
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(r"C:\Users\jayzh\projects\macro-research-department")
OUT = ROOT / "claude-ref" / "research" / "lfs_micro" / "audit_2026-06-09" / "forensics"

boc = pd.read_csv(ROOT / "data" / "raw" / "lfs_micro.csv", parse_dates=["date"]) \
        .rename(columns={"value": "boc"})
ours = pd.read_csv(ROOT / "data" / "processed" / "lfs_micro_replication.csv",
                   parse_dates=["date"])
m = pd.merge(ours, boc, on="date", how="inner")

def fit(pred, name):
    r = pred - m["boc"]
    print(f"{name:38s} RMSE={np.sqrt((r**2).mean()):.4f} "
          f"bias={r.mean():+.4f} sd={r.std(ddof=1):.4f} "
          f"corr={pred.corr(m['boc']):.4f}")
    return r

print("=== Conversion-convention test ===")
lp = np.log1p(m["underlying_pct"] / 100.0)  # recover underlying_lp
r_pct = fit(m["underlying_pct"], "exp()-1 conversion (current)")
r_lp = fit(lp * 100.0, "100*delta-log (no exp conversion)")
print(f"mean convexity term (pct - lp*100): {(m['underlying_pct'] - lp*100).mean():+.4f}pp")

print("\n=== Alternative constructions vs BoC ===")
# total minus composition in pct space (arithmetic, not log, decomposition)
fit(m["raw_mean_pct"] - m["composition_pct"], "raw_mean_pct - composition_pct")
fit(m["total_fitted_pct"] - m["composition_pct"], "total_fitted - composition (pct)")
# include the interaction in underlying
fit(m["underlying_pct"] + m["interaction_pct"], "underlying + interaction")
# de-meaned: how good is pure shape match?
dm = m["underlying_pct"] - (m["underlying_pct"].mean() - m["boc"].mean())
fit(dm, "ours minus constant bias")

print("\n=== Residual structure regression ===")
resid = m["underlying_pct"] - m["boc"]
X = np.column_stack([
    np.ones(len(m)),
    m["composition_pct"].values,
    m["raw_mean_pct"].values,
])
beta, res_ss, *_ = np.linalg.lstsq(X, resid.values, rcond=None)
fitted = X @ beta
r2 = 1 - ((resid - fitted) ** 2).sum() / ((resid - resid.mean()) ** 2).sum()
print(f"resid ~ const + composition + raw_mean: "
      f"b = {np.round(beta, 4).tolist()}, R^2 = {r2:.3f}")
rmse_after = np.sqrt(((resid - fitted) ** 2).mean())
print(f"RMSE after removing fitted structure: {rmse_after:.4f}pp")

# AR(1) variance decomposition of the de-meaned residual
e = (resid - resid.mean()).values
rho = np.sum(e[1:] * e[:-1]) / np.sum(e ** 2)
innov = e[1:] - rho * e[:-1]
print(f"\nAR(1) rho = {rho:.3f}; innovation sd = {innov.std(ddof=1):.4f}pp "
      f"(persistent-component share of residual var = {1 - innov.var(ddof=1)/np.var(e, ddof=1):.2%})")

print("\n=== Worst months ===")
m["resid"] = resid
w = m.reindex(m["resid"].abs().sort_values(ascending=False).index)[
    ["date", "underlying_pct", "boc", "resid", "composition_pct", "raw_mean_pct"]
].head(10)
print(w.to_string(index=False))

print("\n=== Rolling 12m mean of residual (level-shift view) ===")
rr = pd.Series(resid.values, index=m["date"]).rolling(12).mean().dropna()
print(rr.iloc[::6].round(3).to_string())
