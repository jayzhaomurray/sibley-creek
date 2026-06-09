# Residual forensics: Sibley Creek LFS-micro replication vs BoC INDINF_LFSMICRO_M.
# READ-ONLY on data/. All outputs to this folder.
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(r"C:\Users\jayzh\projects\macro-research-department")
OUT = ROOT / "claude-ref" / "research" / "lfs_micro" / "audit_2026-06-09" / "forensics"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- load
boc = pd.read_csv(ROOT / "data" / "raw" / "lfs_micro.csv", parse_dates=["date"])
boc = boc.rename(columns={"value": "boc"})
ours = pd.read_csv(ROOT / "data" / "processed" / "lfs_micro_replication.csv",
                   parse_dates=["date"])

print("BoC span:", boc["date"].min().date(), "->", boc["date"].max().date(),
      "n =", len(boc))
print("Ours span:", ours["date"].min().date(), "->", ours["date"].max().date(),
      "n =", len(ours))
# decimal precision of BoC feed
dec = boc["boc"].astype(str).str.split(".").str[-1].str.len().max()
print("BoC max decimals:", dec, "| unique mod-0.1 remainders:",
      sorted(set(np.round(np.mod(np.round(boc['boc']*10), 1), 6))))

m = pd.merge(ours[["date", "underlying_pct", "composition_pct", "raw_mean_pct",
                   "interaction_pct", "n_obs_curr", "n_obs_base",
                   "r2_curr", "r2_base"]],
             boc, on="date", how="inner")
print("\nOverlap:", m["date"].min().date(), "->", m["date"].max().date(),
      "n =", len(m))

# ---------------------------------------------------------------- 1. alignment
def fit_at_lag(k):
    """Shift ours by k months (ours[t+k] vs boc[t]); return rmse, corr, n."""
    s = ours.set_index("date")["underlying_pct"].copy()
    s.index = s.index - pd.DateOffset(months=k)
    j = pd.merge(s.rename("o").reset_index(), boc, on="date", how="inner").dropna()
    r = j["o"] - j["boc"]
    return np.sqrt((r ** 2).mean()), j["o"].corr(j["boc"]), len(j)

print("\n--- Alignment scan (ours shifted by k months vs BoC) ---")
for k in range(-3, 4):
    rm, co, n = fit_at_lag(k)
    print(f"  k={k:+d}: RMSE={rm:.4f} corr={co:.4f} n={n}")

resid = (m["underlying_pct"] - m["boc"]).rename("resid")
m["resid"] = resid
rmse = float(np.sqrt((resid ** 2).mean()))
mae = float(resid.abs().mean())
corr = float(m["underlying_pct"].corr(m["boc"]))
mx = m.loc[resid.abs().idxmax()]
print(f"\n--- Recomputed fit (lag 0) ---")
print(f"RMSE={rmse:.4f}pp MAE={mae:.4f}pp corr={corr:.4f} n={len(m)}")
print(f"max |miss| = {resid.abs().max():.4f}pp at {mx['date'].date()} "
      f"(ours {mx['underlying_pct']:.3f} vs BoC {mx['boc']:.1f})")

# ---------------------------------------------------------------- 2. residual character
mean = resid.mean()
sd = resid.std(ddof=1)
t = mean / (sd / np.sqrt(len(resid)))
print(f"\n--- Residual character ---")
print(f"mean = {mean:+.4f}pp, sd = {sd:.4f}, t = {t:.2f}, "
      f"p = {2 * (1 - stats.t.cdf(abs(t), len(resid) - 1)):.4f}")
print(f"RMSE^2 split: bias^2 = {mean**2:.5f}, var = {resid.var(ddof=0):.5f} "
      f"(bias share {100 * mean**2 / (rmse**2):.1f}%)")

# autocorrelation
def acf(x, k):
    x = np.asarray(x, float)
    xd = x - x.mean()
    return float(np.sum(xd[k:] * xd[:-k]) / np.sum(xd ** 2))

se_acf = 1 / np.sqrt(len(resid))
print(f"\nACF of residual (+/-2se band = {2*se_acf:.3f}):")
for k in [1, 2, 3, 6, 11, 12, 13, 24]:
    a = acf(resid, k)
    flag = " *" if abs(a) > 2 * se_acf else ""
    print(f"  lag {k:2d}: {a:+.3f}{flag}")

# trend
x = np.arange(len(m))
sl, ic, rv, pv, se = stats.linregress(x, resid)
print(f"\nTrend: slope = {sl*12:+.4f}pp/yr, p = {pv:.4f}")

# sub-periods
m["year"] = m["date"].dt.year
periods = {
    "2016-2019 (pre-COVID)": (m["date"] < "2020-03-01"),
    "2020-03..2021-12 (COVID)": (m["date"] >= "2020-03-01") & (m["date"] <= "2021-12-01"),
    "2022-2023": (m["date"] >= "2022-01-01") & (m["date"] <= "2023-12-01"),
    "2024+ ": (m["date"] >= "2024-01-01"),
}
print("\nSub-period residual stats:")
for name, mask in periods.items():
    r = resid[mask]
    print(f"  {name:28s} n={len(r):3d} mean={r.mean():+.4f} "
          f"sd={r.std(ddof=1):.4f} rmse={np.sqrt((r**2).mean()):.4f}")

print("\nResidual by year:")
print(m.groupby("year")["resid"].agg(["count", "mean", "std",
      lambda s: np.sqrt((s**2).mean())]).rename(columns={"<lambda_0>": "rmse"})
      .round(4).to_string())

# seasonality
m["mon"] = m["date"].dt.month
g = m.groupby("mon")["resid"].agg(["count", "mean", "std"])
F, pF = stats.f_oneway(*[m.loc[m["mon"] == mm, "resid"].values for mm in range(1, 13)])
print(f"\nResidual by calendar month (ANOVA F = {F:.2f}, p = {pF:.4f}):")
print(g.round(4).to_string())

# ---------------------------------------------------------------- 3. hypotheses
print("\n--- Hypothesis correlates ---")
m["abs_resid"] = resid.abs()
candidates = {
    "raw_mean_pct (wage growth level)": m["raw_mean_pct"],
    "|composition_pct|": m["composition_pct"].abs(),
    "composition_pct (signed)": m["composition_pct"],
    "|interaction_pct|": m["interaction_pct"].abs(),
    "min(n_obs_curr, n_obs_base)": m[["n_obs_curr", "n_obs_base"]].min(axis=1),
    "r2_curr": m["r2_curr"],
    "BoC level": m["boc"],
}
rows = []
for name, v in candidates.items():
    for target, tv in [("|resid|", m["abs_resid"]), ("resid", resid)]:
        r, p = stats.pearsonr(v, tv)
        rs, ps = stats.spearmanr(v, tv)
        rows.append((name, target, r, p, rs, ps))
ct = pd.DataFrame(rows, columns=["variable", "vs", "pearson", "p", "spearman", "p_s"])
print(ct.round(4).to_string(index=False))

# attenuation test: regress ours on BoC; slope > 1 => we amplify, < 1 => compress
sl2, ic2, rv2, pv2, se2 = stats.linregress(m["boc"], m["underlying_pct"])
print(f"\nAttenuation: ours = {ic2:.3f} + {sl2:.4f}*BoC  "
      f"(se {se2:.4f}; slope != 1 t = {(sl2-1)/se2:+.2f})")

# rounding floor: BoC published at 0.1pp grid
round_var = 0.1 ** 2 / 12
print(f"\nBoC 0.1pp publication rounding: implied RMSE floor contribution "
      f"= {np.sqrt(round_var):.4f}pp; share of residual variance "
      f"= {100 * round_var / (rmse**2):.1f}%")
print(f"RMSE net of rounding (quadrature) = {np.sqrt(rmse**2 - round_var):.4f}pp")

# residual distribution vs rounding-only null (uniform +/-0.05)
ks = stats.kstest(resid, stats.norm(loc=mean, scale=sd).cdf)
print(f"Normality KS p = {ks.pvalue:.3f}")

# lag-12 pair scatter data: bad-month contamination => resid[t] vs resid[t+12] negative
r12 = pd.DataFrame({"resid": resid.values}, index=m["date"])
r12["resid_p12"] = r12["resid"].shift(-12)
pair = r12.dropna()
rr, pp_ = stats.pearsonr(pair["resid"], pair["resid_p12"])
print(f"\nLag-12 contamination test: corr(resid[t], resid[t+12]) = {rr:+.3f} (p = {pp_:.4f})")
print("  (negative & significant would mean one bad PUMF month flips sign 12m later)")

# engine-cache spec audit + firmsize availability over time
cache_dir = ROOT / "data" / "raw" / "lfs_pumf" / "_engine_cache"
fs = []
for f in sorted(cache_dir.glob("*.json")):
    d = json.loads(f.read_text())
    fs.append((f.stem, d.get("firmsize_comp_lp"), d.get("spec", {}).get("smoothing")))
fsdf = pd.DataFrame(fs, columns=["month", "firmsize_comp_lp", "spec_smoothing"])
nz = fsdf["firmsize_comp_lp"].fillna(0).abs() > 1e-12
print(f"\nEngine cache: {len(fsdf)} months; firmsize contribution nonzero in "
      f"{int(nz.sum())} months; zero/absent in: "
      f"{fsdf.loc[~nz, 'month'].tolist()[:20]}")

# ---------------------------------------------------------------- plots
fig, axes = plt.subplots(4, 1, figsize=(11, 13), sharex=False)
ax = axes[0]
ax.plot(m["date"], m["boc"], lw=1.2, label="BoC INDINF_LFSMICRO_M", color="#1f4e79")
ax.plot(m["date"], m["underlying_pct"], lw=1.0, label="Sibley Creek replication",
        color="#c0392b", alpha=0.85)
ax.set_title("LFS-micro wage growth: BoC vs replication (overlap)")
ax.set_ylabel("% y/y"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax = axes[1]
ax.axhline(0, color="k", lw=0.6)
ax.axhspan(-0.05, 0.05, color="grey", alpha=0.25, label="BoC 0.1pp rounding band")
ax.bar(m["date"], m["resid"], width=20, color=np.where(m["resid"] >= 0,
       "#c0392b", "#1f4e79"))
ax.set_title(f"Residual (ours - BoC): mean {mean:+.3f}pp, RMSE {rmse:.3f}pp")
ax.set_ylabel("pp"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax = axes[2]
lags = range(1, 25)
av = [acf(resid, k) for k in lags]
ax.bar(lags, av, color="#555")
ax.axhline(2 * se_acf, color="r", ls="--", lw=0.7)
ax.axhline(-2 * se_acf, color="r", ls="--", lw=0.7)
ax.set_title("Residual autocorrelation (red = +/-2se)")
ax.set_xlabel("lag (months)"); ax.set_xticks([1, 6, 12, 18, 24]); ax.grid(alpha=0.3)

ax = axes[3]
bp = [m.loc[m["mon"] == mm, "resid"].values for mm in range(1, 13)]
ax.boxplot(bp, tick_labels=["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
ax.axhline(0, color="k", lw=0.6)
ax.set_title(f"Residual by calendar month (ANOVA p = {pF:.3f})")
ax.set_ylabel("pp"); ax.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(OUT / "residual_panels.png", dpi=140)
print("\nWrote", OUT / "residual_panels.png")

# scatters
fig2, ax2 = plt.subplots(1, 3, figsize=(13, 4))
ax2[0].scatter(m["composition_pct"].abs(), m["abs_resid"], s=14,
               facecolors="#1f4e7930", edgecolors="#1f4e79", linewidths=1)
ax2[0].set_xlabel("|composition effect| (pp)"); ax2[0].set_ylabel("|residual| (pp)")
ax2[0].set_title("Miss vs composition magnitude")
ax2[1].scatter(m["raw_mean_pct"], m["abs_resid"], s=14,
               facecolors="#c0392b30", edgecolors="#c0392b", linewidths=1)
ax2[1].set_xlabel("raw mean wage growth (% y/y)")
ax2[1].set_title("Miss vs wage-growth level")
ax2[2].scatter(pair["resid"], pair["resid_p12"], s=14,
               facecolors="#55555530", edgecolors="#555", linewidths=1)
ax2[2].axhline(0, lw=0.5, color="k"); ax2[2].axvline(0, lw=0.5, color="k")
ax2[2].set_xlabel("resid[t]"); ax2[2].set_ylabel("resid[t+12]")
ax2[2].set_title(f"Lag-12 contamination (r = {rr:+.2f})")
for a in ax2:
    a.grid(alpha=0.3)
fig2.tight_layout()
fig2.savefig(OUT / "residual_scatters.png", dpi=140)
print("Wrote", OUT / "residual_scatters.png")

m[["date", "underlying_pct", "boc", "resid", "composition_pct",
   "raw_mean_pct", "n_obs_curr", "n_obs_base"]].to_csv(
    OUT / "residual_table.csv", index=False)
print("Wrote", OUT / "residual_table.csv")
