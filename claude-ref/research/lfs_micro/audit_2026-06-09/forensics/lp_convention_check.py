# Under the 100*delta-log convention, does the wage-level correlation of the
# residual vanish (confirming convexity was the driver)? READ-ONLY.
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(r"C:\Users\jayzh\projects\macro-research-department")
OUT = ROOT / "claude-ref" / "research" / "lfs_micro" / "audit_2026-06-09" / "forensics"

boc = pd.read_csv(ROOT / "data" / "raw" / "lfs_micro.csv", parse_dates=["date"]) \
        .rename(columns={"value": "boc"})
ours = pd.read_csv(ROOT / "data" / "processed" / "lfs_micro_replication.csv",
                   parse_dates=["date"])
m = pd.merge(ours, boc, on="date", how="inner")

m["lp100"] = np.log1p(m["underlying_pct"] / 100.0) * 100
for name, col in [("exp()-1", "underlying_pct"), ("100*dlog", "lp100")]:
    r = m[col] - m["boc"]
    rl, pl = stats.pearsonr(m["raw_mean_pct"], r)
    rc, pc = stats.pearsonr(m["composition_pct"], r)
    print(f"{name:9s} bias={r.mean():+.4f} RMSE={np.sqrt((r**2).mean()):.4f} "
          f"corr(resid, wage level)={rl:+.3f} (p={pl:.3f}) "
          f"corr(resid, comp)={rc:+.3f} (p={pc:.3f})")
    e = (r - r.mean()).values
    rho = np.sum(e[1:] * e[:-1]) / np.sum(e ** 2)
    print(f"          AR1={rho:.3f} max|miss|={r.abs().max():.4f} "
          f"at {m.loc[r.abs().idxmax(), 'date'].date()}")

# year means under lp convention
r = m["lp100"] - m["boc"]
m["resid_lp"] = r
print("\nResidual (lp convention) by year:")
print(m.groupby(m["date"].dt.year)["resid_lp"].agg(["mean", "std"]).round(4).to_string())

# plot comparison
fig, ax = plt.subplots(figsize=(11, 4))
ax.axhline(0, color="k", lw=0.6)
ax.axhspan(-0.05, 0.05, color="grey", alpha=0.25, label="BoC 0.1pp rounding band")
ax.plot(m["date"], m["underlying_pct"] - m["boc"], lw=1, color="#c0392b",
        label="resid, exp()-1 convention (current)")
ax.plot(m["date"], r, lw=1, color="#1f4e79",
        label="resid, 100*dlog convention")
ax.legend(fontsize=8)
ax.set_ylabel("pp")
ax.set_title("Residual vs BoC under both unit conventions")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "residual_lp_convention.png", dpi=140)
print("\nWrote", OUT / "residual_lp_convention.png")
