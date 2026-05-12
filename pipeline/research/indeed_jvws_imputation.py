"""Impute the April-September 2020 gap in StatCan JVWS using Indeed Hiring Lab CA postings.

Background:
    StatCan's Job Vacancy and Wage Survey (JVWS, monthly vacancy rate, % of labour
    force) was suspended Apr 2020 - Sep 2020 inclusive during the pandemic. Six
    monthly observations are missing, which forces a Beveridge curve to skip the
    deepest part of the COVID excursion (unemployment spiked to ~13% in Apr 2020).

    Indeed Hiring Lab publishes a daily Canadian job-postings index (Feb 1 2020 = 100),
    which DOES cover the missing window. This script bridges the unit gap by fitting
    a linear regression of JVWS on Indeed over the overlap period (Oct 2020 onward)
    and back-casting the missing six observations.

Outputs:
    - data/derived/jvws_vacancy_rate_imputed.csv
    - editorial/research/indeed_jvws_imputation/01_overlay.png
    - editorial/research/indeed_jvws_imputation/02_scatter_fit.png
    - editorial/research/indeed_jvws_imputation/03_imputed_filled.png
    - editorial/research/indeed_jvws_imputation/04_residuals.png
    - editorial/research/indeed_jvws_imputation/05_alternative_method.png

This is exploratory research, not a production component. Plots use matplotlib
defaults intentionally; do not wire into site canon without explicit ask.

Run from project root:
    py -m pipeline.research.indeed_jvws_imputation
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Paths -- resolved relative to project root (this file lives at pipeline/research/).
ROOT = Path(__file__).resolve().parents[2]
JVWS_PATH = ROOT / "data" / "raw" / "job_vacancy_rate.csv"
INDEED_MONTHLY_PATH = ROOT / "data" / "raw" / "indeed_postings_ca_monthly.csv"
DERIVED_DIR = ROOT / "data" / "derived"
PLOTS_DIR = ROOT / "editorial" / "research" / "indeed_jvws_imputation"

GAP_START = pd.Timestamp("2020-04-01")
GAP_END = pd.Timestamp("2020-09-01")


def load_series() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load JVWS and Indeed monthly series. Both keyed on 'date' with 'value' column."""
    jvws = pd.read_csv(JVWS_PATH, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    indeed = (
        pd.read_csv(INDEED_MONTHLY_PATH, parse_dates=["date"])
        .sort_values("date")
        .reset_index(drop=True)
    )
    return jvws, indeed


def fit_ols(x: np.ndarray, y: np.ndarray) -> dict:
    """Plain OLS y = a + b*x with R-squared, MAE, RMSE, and residuals."""
    n = len(x)
    X = np.column_stack([np.ones(n), x])
    # Normal equations: beta = (X'X)^-1 X'y
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    a, b = float(beta[0]), float(beta[1])
    y_hat = a + b * x
    resid = y - y_hat
    ss_res = float((resid**2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    mae = float(np.abs(resid).mean())
    rmse = float(np.sqrt((resid**2).mean()))
    # Durbin-Watson for residual autocorrelation (rough rule: 1.5-2.5 = no concern).
    dw = float(((np.diff(resid)) ** 2).sum() / ss_res) if ss_res > 0 else float("nan")
    return {
        "a": a,
        "b": b,
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "dw": dw,
        "n": n,
        "y_hat": y_hat,
        "resid": resid,
    }


def main() -> None:
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    jvws, indeed = load_series()

    # Merge on monthly date.
    merged = jvws.rename(columns={"value": "jvws"}).merge(
        indeed.rename(columns={"value": "indeed"}), on="date", how="outer"
    ).sort_values("date").reset_index(drop=True)

    # Overlap = months where both are observed. Indeed starts Feb 2020; JVWS resumes Oct 2020.
    overlap = merged.dropna(subset=["jvws", "indeed"]).copy()
    print(f"Overlap rows: {len(overlap)}  ({overlap.date.min().date()} -> {overlap.date.max().date()})")

    x = overlap["indeed"].to_numpy()
    y = overlap["jvws"].to_numpy()
    fit = fit_ols(x, y)
    print(
        f"OLS: jvws = {fit['a']:.4f} + {fit['b']:.6f} * indeed   "
        f"R2={fit['r2']:.4f}  MAE={fit['mae']:.3f}  RMSE={fit['rmse']:.3f}  "
        f"DW={fit['dw']:.3f}  n={fit['n']}"
    )

    # Apply model to the gap months (Apr-Sep 2020).
    gap_mask = (merged["date"] >= GAP_START) & (merged["date"] <= GAP_END)
    gap = merged[gap_mask].copy()
    print("\nGap rows (before imputation):")
    print(gap.to_string(index=False))

    merged["jvws_imputed"] = merged["jvws"].copy()
    merged["imputation_source"] = np.where(merged["jvws"].notna(), "observed", "missing")

    # Primary imputation: OLS levels.
    imputed_levels = fit["a"] + fit["b"] * gap["indeed"].to_numpy()
    merged.loc[gap_mask, "jvws_imputed"] = imputed_levels
    merged.loc[gap_mask, "imputation_source"] = "imputed_ols_levels"

    # --- Alternative method: index-scaling robustness check ----------------------
    # Apply Indeed's % move from Mar 2020 (last pre-pause JVWS = 3.2) to JVWS.
    # JVWS_t = JVWS_{Mar2020} * (Indeed_t / Indeed_{Mar2020}).
    jvws_mar = float(merged.loc[merged["date"] == "2020-03-01", "jvws"].iloc[0])
    indeed_mar = float(merged.loc[merged["date"] == "2020-03-01", "indeed"].iloc[0])
    alt_scaled = jvws_mar * (gap["indeed"].to_numpy() / indeed_mar)
    print("\nAlternative (index-scaling from Mar 2020 anchor):")
    for d, lev, alt in zip(gap["date"], imputed_levels, alt_scaled):
        print(f"  {d.date()}  ols={lev:.3f}  alt={alt:.3f}")

    # --- Write derived CSV -------------------------------------------------------
    out = merged[["date", "jvws", "indeed", "jvws_imputed", "imputation_source"]].copy()
    out_path = DERIVED_DIR / "jvws_vacancy_rate_imputed.csv"
    out.to_csv(out_path, index=False)
    print(f"\nWrote {out_path}")

    # --- Plot 01: overlay with twin axes (overlap window) ------------------------
    overlap_plot_start = pd.Timestamp("2020-02-01")
    o = merged[(merged["date"] >= overlap_plot_start)].copy()
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(o["date"], o["jvws"], color="tab:blue", label="JVWS vacancy rate (%)", lw=1.8)
    ax1.set_ylabel("JVWS vacancy rate (%)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(o["date"], o["indeed"], color="tab:orange", label="Indeed postings (Feb-1-2020=100)", lw=1.2)
    ax2.set_ylabel("Indeed postings index (Feb-1-2020=100)", color="tab:orange")
    ax2.tick_params(axis="y", labelcolor="tab:orange")
    ax1.axvspan(GAP_START, GAP_END, color="lightgrey", alpha=0.4, label="JVWS pause")
    ax1.set_title("JVWS vacancy rate vs Indeed postings index (Feb 2020 - present)")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "01_overlay.png", dpi=120)
    plt.close(fig)

    # --- Plot 02: scatter + fit --------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(x, y, alpha=0.6, s=24)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, fit["a"] + fit["b"] * xs, color="red", lw=1.5, label="OLS fit")
    ax.set_xlabel("Indeed postings index (Feb-1-2020 = 100)")
    ax.set_ylabel("JVWS vacancy rate (%)")
    ax.set_title(f"JVWS vs Indeed (overlap, n={fit['n']})")
    ax.annotate(
        f"y = {fit['a']:.3f} + {fit['b']:.5f} x\n"
        f"R² = {fit['r2']:.3f}\nRMSE = {fit['rmse']:.3f}\nMAE = {fit['mae']:.3f}",
        xy=(0.04, 0.96),
        xycoords="axes fraction",
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.85},
    )
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "02_scatter_fit.png", dpi=120)
    plt.close(fig)

    # --- Plot 03: filled series, imputed flagged ---------------------------------
    fig, ax = plt.subplots(figsize=(11, 5))
    full = merged.copy()
    observed = full[full["imputation_source"] == "observed"]
    imputed = full[full["imputation_source"] == "imputed_ols_levels"]
    ax.plot(full["date"], full["jvws_imputed"], color="tab:blue", lw=1.2, alpha=0.7, label="JVWS (observed + imputed)")
    ax.scatter(observed["date"], observed["jvws_imputed"], color="tab:blue", s=10, label="Observed")
    ax.scatter(imputed["date"], imputed["jvws_imputed"], color="tab:red", marker="D", s=42, zorder=5, label="Imputed (Apr-Sep 2020)")
    ax.set_ylabel("JVWS vacancy rate (%)")
    ax.set_title("JVWS vacancy rate with imputed 2020 gap")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "03_imputed_filled.png", dpi=120)
    plt.close(fig)

    # --- Plot 04: residuals over fit period --------------------------------------
    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    axes[0].plot(overlap["date"], fit["resid"], marker="o", ms=3, lw=0.8)
    axes[0].axhline(0, color="grey", lw=0.6)
    axes[0].set_title(f"OLS residuals over fit period (DW = {fit['dw']:.2f})")
    axes[0].set_ylabel("Residual (% pts)")
    axes[1].hist(fit["resid"], bins=20, color="tab:blue", alpha=0.7)
    axes[1].set_xlabel("Residual (% pts)")
    axes[1].set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "04_residuals.png", dpi=120)
    plt.close(fig)

    # --- Plot 05: alternative method side-by-side --------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    window = merged[(merged["date"] >= "2019-06-01") & (merged["date"] <= "2021-12-01")].copy()
    ax.plot(window["date"], window["jvws"], color="tab:blue", marker="o", ms=4, label="JVWS observed")
    ax.scatter(gap["date"], imputed_levels, color="tab:red", marker="D", s=60, zorder=5, label="OLS levels imputation")
    ax.scatter(gap["date"], alt_scaled, color="tab:green", marker="s", s=60, zorder=5, label="Index-scaling alternative")
    ax.axvspan(GAP_START, GAP_END, color="lightgrey", alpha=0.4)
    ax.set_ylabel("JVWS vacancy rate (%)")
    ax.set_title("Imputation: OLS levels vs index-scaling robustness check")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "05_alternative_method.png", dpi=120)
    plt.close(fig)

    print("\nImputed values (Apr-Sep 2020):")
    for d, v in zip(gap["date"], imputed_levels):
        print(f"  {d.date()}  {v:.3f}")

    print(f"\nPlots written to {PLOTS_DIR}")


if __name__ == "__main__":
    main()
