import base64
import json
import math
import warnings
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import erfinv
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import ElasticNetCV
from sklearn.metrics import r2_score


warnings.filterwarnings("ignore", category=UserWarning)

RANDOM_SEED = 20260527
OUT_DIR = Path("chatgpt_replication")
VARIABLES_PATH = Path("data/processed/usdcad_variables.parquet")
TARGETS_PATH = Path("data/processed/usdcad_targets.parquet")
IMPLEMENTATION_ID = "chatgpt-codex-v2-2026-05-27"

HORIZONS = {
    "weekly": {"days": 5, "ret": "ret_5d", "dir": "dir_5d"},
    "monthly": {"days": 21, "ret": "ret_21d", "dir": "dir_21d"},
    "quarterly": {"days": 63, "ret": "ret_63d", "dir": "dir_63d"},
}

CATEGORY_PREFIX = {
    "A": "Rates and yield curves",
    "B": "Commodities",
    "C": "Risk appetite",
    "F": "Macroeconomic releases",
    "G": "USD and FX",
    "H": "Policy and trade uncertainty",
    "I": "Technical and USDCAD-derived",
    "J": "Other",
    "L": "Other",
}


@dataclass
class RobustScalerState:
    medians: pd.Series
    iqrs: pd.Series
    fill_values: pd.Series
    columns: list[str]


def category(feature: str) -> str:
    return CATEGORY_PREFIX.get(feature[:1], "Other")


def robust_fit_transform(x: pd.DataFrame) -> tuple[pd.DataFrame, RobustScalerState]:
    fill_values = x.median(numeric_only=True).fillna(0.0)
    filled = x.fillna(fill_values)
    medians = filled.median(numeric_only=True)
    iqrs = (filled.quantile(0.75) - filled.quantile(0.25)).replace(0.0, np.nan)
    iqrs = iqrs.fillna(filled.std(ddof=0)).replace(0.0, 1.0)
    state = RobustScalerState(medians=medians, iqrs=iqrs, fill_values=fill_values, columns=list(x.columns))
    return ((filled - medians) / iqrs).astype(float), state


def robust_transform(x: pd.DataFrame, state: RobustScalerState) -> pd.DataFrame:
    aligned = x.reindex(columns=state.columns)
    filled = aligned.fillna(state.fill_values)
    return ((filled - state.medians) / state.iqrs).astype(float)


def purged_expanding_splits(n: int, horizon_days: int, fold_count: int = 10) -> list[tuple[np.ndarray, np.ndarray]]:
    val_size = max(30, n // (fold_count + 2))
    initial_train = n - val_size * fold_count
    splits = []
    for fold in range(fold_count):
        val_start = initial_train + fold * val_size
        val_end = n if fold == fold_count - 1 else min(n, val_start + val_size)
        train_end = max(0, val_start - horizon_days)
        train_idx = np.arange(0, train_end)
        val_idx = np.arange(val_start, val_end)
        if len(train_idx) >= max(252, horizon_days * 5) and len(val_idx) >= 10:
            splits.append((train_idx, val_idx))
    return splits


def spearman_filter(x_train_raw: pd.DataFrame, y_train: pd.Series) -> tuple[list[str], dict]:
    details = {}
    usable_cols = []
    for col in x_train_raw.columns:
        s = x_train_raw[col]
        coverage = float(s.notna().mean())
        unique = int(s.dropna().nunique())
        if coverage < 0.20 or unique < 3:
            details[col] = {"rho": 0.0, "pvalue": 1.0, "coverage": coverage, "mi": 0.0, "keep": False}
            continue
        joined = pd.concat([s, y_train], axis=1).dropna()
        if len(joined) < 100:
            rho, pval = 0.0, 1.0
        else:
            rho, pval = stats.spearmanr(joined.iloc[:, 0], joined.iloc[:, 1])
            if not np.isfinite(rho):
                rho, pval = 0.0, 1.0
        details[col] = {"rho": float(rho), "pvalue": float(pval), "coverage": coverage, "mi": 0.0, "keep": False}
        usable_cols.append(col)

    if usable_cols:
        tmp = x_train_raw[usable_cols].copy()
        tmp = tmp.fillna(tmp.median(numeric_only=True).fillna(0.0))
        mi = mutual_info_regression(tmp, y_train.to_numpy(), random_state=RANDOM_SEED, n_neighbors=5)
        for col, val in zip(usable_cols, mi):
            details[col]["mi"] = float(max(val, 0.0))

    positives = [d["mi"] for d in details.values() if d["mi"] > 0]
    mi_cut = float(np.median(positives)) if positives else math.inf
    kept = []
    for col, d in details.items():
        keep = (abs(d["rho"]) >= 0.03 and d["pvalue"] <= 0.10) or (d["mi"] > 0 and d["mi"] >= mi_cut)
        d["keep"] = bool(keep)
        if keep:
            kept.append(col)
    if len(kept) < 5:
        ranked = sorted(
            [c for c in x_train_raw.columns if details[c]["coverage"] >= 0.20],
            key=lambda c: (abs(details[c]["rho"]), details[c]["mi"]),
            reverse=True,
        )
        kept = ranked[: min(5, len(ranked))]
        for col in kept:
            details[col]["keep"] = True
    return kept, details


def elastic_net_selection(xz: pd.DataFrame, y: pd.Series, splits: list[tuple[np.ndarray, np.ndarray]]) -> tuple[set[str], dict]:
    model = ElasticNetCV(
        l1_ratio=[0.15, 0.5, 0.85, 1.0],
        alphas=np.logspace(-4, 1, 60),
        cv=[(tr, va) for tr, va in splits],
        max_iter=20000,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(xz.to_numpy(), y.to_numpy())
    coefs = pd.Series(model.coef_, index=xz.columns)
    return set(coefs[coefs.abs() > 1e-8].index), {
        "alpha": float(model.alpha_),
        "l1_ratio": float(model.l1_ratio_),
        "coefs": coefs.to_dict(),
    }


def boruta_shadow_selection(xz: pd.DataFrame, y: pd.Series) -> tuple[set[str], dict]:
    rng = np.random.default_rng(RANDOM_SEED)
    arr = xz.to_numpy()
    hit_counts = pd.Series(0, index=xz.columns, dtype=float)
    importance_sum = pd.Series(0.0, index=xz.columns)
    n_iter = 25
    for i in range(n_iter):
        shadow = arr.copy()
        for j in range(shadow.shape[1]):
            rng.shuffle(shadow[:, j])
        combo = np.hstack([arr, shadow])
        rf = RandomForestRegressor(
            n_estimators=250,
            max_depth=5,
            min_samples_leaf=25,
            max_features="sqrt",
            random_state=RANDOM_SEED + 31 + i,
            n_jobs=-1,
        )
        rf.fit(combo, y.to_numpy())
        real_imp = pd.Series(rf.feature_importances_[: xz.shape[1]], index=xz.columns)
        shadow_max = float(np.max(rf.feature_importances_[xz.shape[1] :]))
        hit_counts += (real_imp > shadow_max).astype(float)
        importance_sum += real_imp
    hit_rate = hit_counts / n_iter
    mean_imp = importance_sum / n_iter
    selected = set(hit_rate[hit_rate >= 0.20].index)
    if not selected:
        selected = set(mean_imp.sort_values(ascending=False).head(min(5, len(mean_imp))).index)
    return selected, {"hit_rate": hit_rate.to_dict(), "importance": mean_imp.to_dict(), "iterations": n_iter}


def correlation_clusters(xz: pd.DataFrame, threshold: float = 0.75) -> list[list[str]]:
    corr = xz.corr().abs().fillna(0.0)
    remaining = set(xz.columns)
    clusters = []
    while remaining:
        seed = sorted(remaining)[0]
        cluster = {seed}
        changed = True
        while changed:
            changed = False
            for col in list(remaining - cluster):
                if corr.loc[col, list(cluster)].max() >= threshold:
                    cluster.add(col)
                    changed = True
        clusters.append(sorted(cluster))
        remaining -= cluster
    return clusters


def clustered_mda_selection(
    xz: pd.DataFrame,
    y: pd.Series,
    y_dir: pd.Series,
    splits: list[tuple[np.ndarray, np.ndarray]],
    horizon_days: int,
) -> tuple[set[str], dict]:
    clusters = correlation_clusters(xz)
    cluster_scores = {tuple(c): [] for c in clusters}
    rng = np.random.default_rng(RANDOM_SEED + horizon_days)
    for fold_no, (tr, va) in enumerate(splits[-5:]):
        rf = RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            min_samples_leaf=25,
            max_features="sqrt",
            random_state=RANDOM_SEED + 500 + fold_no + horizon_days,
            n_jobs=-1,
        )
        rf.fit(xz.iloc[tr].to_numpy(), y.iloc[tr].to_numpy())
        pred = rf.predict(xz.iloc[va].to_numpy())
        baseline = float(np.mean(np.where(pred >= 0, 1.0, -1.0) == y_dir.iloc[va].to_numpy()))
        for cluster in clusters:
            xp = xz.iloc[va].copy()
            for col in cluster:
                xp[col] = rng.permutation(xp[col].to_numpy())
            perm_pred = rf.predict(xp.to_numpy())
            perm_hit = float(np.mean(np.where(perm_pred >= 0, 1.0, -1.0) == y_dir.iloc[va].to_numpy()))
            cluster_scores[tuple(cluster)].append(baseline - perm_hit)
    cluster_mean = {k: float(np.mean(v)) if v else 0.0 for k, v in cluster_scores.items()}
    positives = [v for v in cluster_mean.values() if v > 0]
    cutoff = float(np.median(positives) * 0.25) if positives else math.inf
    selected = set()
    for cluster, score in cluster_mean.items():
        if score > cutoff:
            selected.update(cluster)
    if not selected:
        for cluster, _ in sorted(cluster_mean.items(), key=lambda kv: kv[1], reverse=True)[: min(3, len(cluster_mean))]:
            selected.update(cluster)
    feature_scores = {}
    for cluster, score in cluster_mean.items():
        for col in cluster:
            feature_scores[col] = score / max(1, len(cluster))
    return selected, {
        "clusters": [list(c) for c in clusters],
        "cluster_scores": {",".join(k): v for k, v in cluster_mean.items()},
        "feature_scores": feature_scores,
    }


def determine_signs(x_raw: pd.DataFrame, y: pd.Series, features: list[str], fallback_coefs: dict | None = None) -> dict[str, int]:
    signs = {}
    for col in features:
        joined = pd.concat([x_raw[col], y], axis=1).dropna()
        rho = 0.0
        if len(joined) >= 100 and joined.iloc[:, 0].nunique() >= 3:
            rho, _ = stats.spearmanr(joined.iloc[:, 0], joined.iloc[:, 1])
            if not np.isfinite(rho):
                rho = 0.0
        if rho == 0.0 and fallback_coefs:
            rho = float(fallback_coefs.get(col, 0.0))
        signs[col] = 1 if rho >= 0 else -1
    return signs


def signed_composite(xz: pd.DataFrame, signs: dict[str, int]) -> np.ndarray:
    cols = [c for c in xz.columns if c in signs]
    if not cols:
        return np.zeros(len(xz))
    signed = xz[cols].copy()
    for col in cols:
        signed[col] = signed[col] * signs[col]
    return signed.mean(axis=1).to_numpy()


def sharpe_values(signal: np.ndarray, returns: np.ndarray, horizon_days: int) -> tuple[float, float]:
    pnl = np.where(signal >= 0, 1.0, -1.0) * returns
    pnl = pnl[np.isfinite(pnl)]
    if len(pnl) < 3 or np.std(pnl, ddof=1) == 0:
        return 0.0, 0.0
    per_period = float(np.mean(pnl) / np.std(pnl, ddof=1))
    annualized = float(per_period * math.sqrt(252 / horizon_days))
    return per_period, annualized


def hit_rate(signal: np.ndarray, direction: np.ndarray) -> float:
    pred = np.where(signal >= 0, 1.0, -1.0)
    mask = np.isfinite(pred) & np.isfinite(direction)
    return float(np.mean(pred[mask] == direction[mask])) if mask.sum() else 0.0


def deflated_sharpe_probability(sr_per_period: float, n_obs: int, n_trials: int, returns: np.ndarray) -> tuple[float, float]:
    if n_obs < 10 or sr_per_period == 0:
        return 0.0, 1.0
    vals = returns[np.isfinite(returns)]
    skew = float(stats.skew(vals)) if len(vals) > 3 else 0.0
    kurt = float(stats.kurtosis(vals) + 3) if len(vals) > 3 else 3.0
    if n_trials <= 1:
        sr_star = 0.0
    else:
        gamma = 0.5772156649015329
        z1 = 2 * (1 - 1.0 / n_trials) - 1
        z2 = 2 * (1 - 1.0 / (n_trials * math.e)) - 1
        z1 = np.clip(z1, -0.9999, 0.9999)
        z2 = np.clip(z2, -0.9999, 0.9999)
        sr_star = ((1 - gamma) * math.sqrt(2) * erfinv(z1) + gamma * math.sqrt(2) * erfinv(z2)) / math.sqrt(n_obs)
    var_sr = (1 - skew * sr_per_period + ((kurt - 1) / 4.0) * sr_per_period**2) / n_obs
    var_sr = max(var_sr, 1e-8)
    z_dsr = (sr_per_period - sr_star) / math.sqrt(var_sr)
    dsr = float(stats.norm.cdf(z_dsr))
    return dsr, float(1.0 - dsr)


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return float(max(0, center - half)), float(min(1, center + half))


def fit_select_score(train: pd.DataFrame, feature_cols: list[str], cfg: dict) -> dict:
    x_train_raw = train[feature_cols]
    y_train = train[cfg["ret"]].astype(float)
    y_dir_train = train[cfg["dir"]].astype(float)
    filter_features, filter_details = spearman_filter(x_train_raw, y_train)
    xz_filter, scaler_filter = robust_fit_transform(x_train_raw[filter_features])
    splits = purged_expanding_splits(len(train), cfg["days"], 10)

    en_selected, en_info = elastic_net_selection(xz_filter, y_train, splits)
    boruta_selected, boruta_info = boruta_shadow_selection(xz_filter, y_train)
    mda_selected, mda_info = clustered_mda_selection(xz_filter, y_train, y_dir_train, splits, cfg["days"])
    votes = {c: int(c in en_selected) + int(c in boruta_selected) + int(c in mda_selected) for c in filter_features}
    selected = sorted([c for c, v in votes.items() if v >= 2])
    if len(selected) < 3:
        selected = sorted(
            filter_features,
            key=lambda c: (
                votes.get(c, 0),
                abs(filter_details[c]["rho"]),
                boruta_info["importance"].get(c, 0.0),
                mda_info["feature_scores"].get(c, 0.0),
            ),
            reverse=True,
        )[: min(5, len(filter_features))]

    final_xz, final_scaler = robust_fit_transform(x_train_raw[selected])
    final_signs = determine_signs(x_train_raw, y_train, selected, en_info.get("coefs", {}))
    train_score = signed_composite(final_xz, final_signs)
    q_low, q_high = np.quantile(train_score, [0.10, 0.90])

    cv_pred = np.full(len(train), np.nan)
    for tr, va in splits:
        fold_raw = train.iloc[tr][selected]
        fold_y = train.iloc[tr][cfg["ret"]].astype(float)
        _, fold_scaler = robust_fit_transform(fold_raw)
        fold_signs = determine_signs(fold_raw, fold_y, selected, en_info.get("coefs", {}))
        x_va = robust_transform(train.iloc[va][selected], fold_scaler)
        cv_pred[va] = signed_composite(x_va, fold_signs)

    importance = {}
    for col in selected:
        importance[col] = float(
            votes.get(col, 0)
            + abs(filter_details[col]["rho"])
            + boruta_info["importance"].get(col, 0.0)
            + max(0.0, mda_info["feature_scores"].get(col, 0.0))
        )
    max_imp = max(importance.values()) if importance else 1.0
    importance = {k: v / max_imp for k, v in importance.items()}
    return {
        "filter_features": filter_features,
        "filter_details": filter_details,
        "selected": selected,
        "signs": final_signs,
        "scaler": final_scaler,
        "train_score": train_score,
        "train_thresholds": (float(q_low), float(q_high)),
        "cv_pred": cv_pred,
        "splits": splits,
        "votes": votes,
        "importance": importance,
        "en": en_info,
        "boruta": boruta_info,
        "mda": mda_info,
    }


def run_horizon(name: str, cfg: dict, merged: pd.DataFrame, feature_cols: list[str]) -> tuple[dict, dict]:
    df = merged[["date", cfg["ret"], cfg["dir"]] + feature_cols].copy()
    df = df.dropna(subset=[cfg["ret"], cfg["dir"]]).sort_values("date").reset_index(drop=True)
    n_total = len(df)
    n_holdout = int(math.ceil(n_total * 0.20))
    n_train = n_total - n_holdout
    train = df.iloc[:n_train].reset_index(drop=True)
    holdout = df.iloc[n_train:].reset_index(drop=True)

    fit = fit_select_score(train, feature_cols, cfg)
    selected = fit["selected"]
    signs = fit["signs"]

    cv_mask = np.isfinite(fit["cv_pred"])
    cv_hit = hit_rate(fit["cv_pred"][cv_mask], train.loc[cv_mask, cfg["dir"]].to_numpy())
    cv_r2 = float(r2_score(train.loc[cv_mask, cfg["ret"]].to_numpy(), fit["cv_pred"][cv_mask])) if cv_mask.sum() > 2 else 0.0
    cv_sr_period, cv_sharpe = sharpe_values(fit["cv_pred"][cv_mask], train.loc[cv_mask, cfg["ret"]].to_numpy(), cfg["days"])
    n_trials = int(len(feature_cols) + 3)
    dsr, dsr_p = deflated_sharpe_probability(cv_sr_period, int(cv_mask.sum()), n_trials, train.loc[cv_mask, cfg["ret"]].to_numpy())

    x_hold = robust_transform(holdout[selected], fit["scaler"])
    hold_score = signed_composite(x_hold, signs)
    hold_hit = hit_rate(hold_score, holdout[cfg["dir"]].to_numpy())
    hold_r2 = float(r2_score(holdout[cfg["ret"]].to_numpy(), hold_score)) if len(holdout) > 2 else 0.0
    _, hold_sharpe = sharpe_values(hold_score, holdout[cfg["ret"]].to_numpy(), cfg["days"])

    q_low, q_high = fit["train_thresholds"]
    extreme_mask = (hold_score <= q_low) | (hold_score >= q_high)
    middle_mask = ~extreme_mask
    pred_dir = np.where(hold_score >= 0, 1.0, -1.0)
    extreme_hits = int(np.sum(pred_dir[extreme_mask] == holdout.loc[extreme_mask, cfg["dir"]].to_numpy()))
    middle_hits = int(np.sum(pred_dir[middle_mask] == holdout.loc[middle_mask, cfg["dir"]].to_numpy()))
    extreme_n = int(extreme_mask.sum())
    middle_n = int(middle_mask.sum())
    extreme_hit = float(extreme_hits / extreme_n) if extreme_n else 0.0
    middle_hit = float(middle_hits / middle_n) if middle_n else 0.0
    ci_low, ci_high = wilson_ci(extreme_hits, extreme_n)

    x_full = robust_transform(df[selected], fit["scaler"])
    full_score = signed_composite(x_full, signs)
    v, just = verdict(hold_hit, extreme_hit, middle_hit, extreme_n, hold_sharpe, dsr)
    metrics = {
        "horizon_days": int(cfg["days"]),
        "n_obs_total": int(n_total),
        "n_obs_train": int(n_train),
        "n_obs_holdout": int(n_holdout),
        "train_start_date": train["date"].iloc[0].strftime("%Y-%m-%d"),
        "train_end_date": train["date"].iloc[-1].strftime("%Y-%m-%d"),
        "holdout_start_date": holdout["date"].iloc[0].strftime("%Y-%m-%d"),
        "holdout_end_date": holdout["date"].iloc[-1].strftime("%Y-%m-%d"),
        "n_features_input": int(len(feature_cols)),
        "n_features_after_filter": int(len(fit["filter_features"])),
        "n_features_selected_final": int(len(selected)),
        "selected_features": selected,
        "feature_signs": signs,
        "cv_hit_rate": cv_hit,
        "cv_r2": cv_r2,
        "cv_sharpe_annualized": cv_sharpe,
        "dsr": dsr,
        "dsr_pvalue": dsr_p,
        "holdout_hit_rate_aggregate": hold_hit,
        "holdout_r2": hold_r2,
        "holdout_sharpe_annualized": hold_sharpe,
        "holdout_hit_rate_extreme": extreme_hit,
        "holdout_hit_rate_middle": middle_hit,
        "holdout_n_extreme_obs": extreme_n,
        "holdout_n_middle_obs": middle_n,
        "verdict": v,
        "verdict_justification": just,
    }
    diag = {
        "dates": df["date"],
        "full_score": pd.Series(full_score),
        "holdout_start": holdout["date"].iloc[0],
        "thresholds": [q_low, q_high],
        "ci": [ci_low, ci_high],
        "importance": fit["importance"],
        "train_extreme_share": float(np.mean((fit["train_score"] <= q_low) | (fit["train_score"] >= q_high))),
        "holdout_extreme_share": float(extreme_n / len(holdout)) if len(holdout) else 0.0,
    }
    return metrics, diag


def verdict(agg: float, ext: float, mid: float, n_ext: int, sharpe: float, dsr: float) -> tuple[str, str]:
    if n_ext >= 60 and agg >= 0.53 and ext >= 0.56 and ext - mid >= 0.04 and sharpe > 0 and dsr >= 0.50:
        return "ship_with_trade_ideas", "Aggregate and extreme hold-out performance are positive using train-derived thresholds and corrected DSR; still disclose overlapping-label limitations."
    if n_ext >= 40 and (ext >= 0.55 or agg >= 0.52) and sharpe > -0.10:
        return "scorecard_only", "There is some directional structure, but it is not strong enough for standalone trade calls after corrected thresholding and multiple-testing treatment."
    return "do_not_ship", "Corrected hold-out evidence is too weak or unstable for a predictive product."


def plot_png(dates, scores, holdout_start, title, q_low, q_high) -> str:
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=140)
    ax.plot(dates, scores, color="#194f78", linewidth=1.0)
    ax.axvspan(pd.to_datetime(holdout_start), pd.to_datetime(dates.iloc[-1]), color="#d99a2b", alpha=0.22)
    ax.axhline(0, color="#333333", linewidth=0.7)
    ax.axhline(q_low, color="#7b2d26", linewidth=0.8, linestyle="--")
    ax.axhline(q_high, color="#2d6a4f", linewidth=0.8, linestyle="--")
    ax.set_title(title)
    ax.set_ylabel("Signed robust-z composite")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    bio = BytesIO()
    fig.savefig(bio, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(bio.getvalue()).decode("ascii")


def write_html(name: str, metrics: dict, diag: dict) -> None:
    q_low, q_high = diag["thresholds"]
    ci_low, ci_high = diag["ci"]
    img = plot_png(diag["dates"], diag["full_score"], diag["holdout_start"], f"{name.capitalize()} USDCAD v2 composite", q_low, q_high)
    rows = ""
    for feat, val in sorted(diag["importance"].items(), key=lambda kv: kv[1], reverse=True):
        rows += f"<tr><td>{feat}</td><td>{category(feat)}</td><td>{val:.3f}</td><td>{metrics['feature_signs'][feat]:+d}</td></tr>\n"
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>USDCAD v2 {name}</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;margin:0;background:#fbfbf8;color:#17202a}}section{{padding:28px 42px;border-bottom:1px solid #ddd8cc}}.hero{{min-height:100vh;display:flex;flex-direction:column;justify-content:center;background:#12303f;color:#fff;box-sizing:border-box}}.hero h1{{font-size:40px;margin:0 0 14px}}.hero p{{max-width:940px;font-size:18px;line-height:1.45}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}.metric{{background:#fff;border:1px solid #d9d4c8;border-radius:6px;padding:14px}}.metric b{{display:block;font-size:24px;margin-top:6px}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid #e5e0d6}}th{{background:#efe9dc}}img{{width:100%;max-width:1200px;height:auto}}.caption{{color:#4c5963;font-size:14px;line-height:1.45}}
</style></head><body>
<section class="hero"><h1>{name.capitalize()} v2 verdict: {metrics['verdict'].replace('_',' ')}</h1>
<p><b>Headline:</b> aggregate hold-out hit rate {metrics['holdout_hit_rate_aggregate']:.1%}; train-threshold extreme hit rate {metrics['holdout_hit_rate_extreme']:.1%} versus {metrics['holdout_hit_rate_middle']:.1%} in the middle bucket.</p>
<p><b>What changed from v1:</b> extreme thresholds are fit on training scores, DSR is probability-style and period-consistent, Sharpe uses horizon scaling, and the same signed composite score definition is used for CV and hold-out.</p></section>
<section><h2>Composite score chart over time</h2><img alt="Composite score chart" src="data:image/png;base64,{img}"><p class="caption">Dashed lines are training-derived 10th/90th percentile thresholds. Shading marks the untouched hold-out period.</p></section>
<section><h2>Hold-out performance summary</h2><div class="grid">
<div class="metric">Hit rate<b>{metrics['holdout_hit_rate_aggregate']:.1%}</b></div>
<div class="metric">R2<b>{metrics['holdout_r2']:.3f}</b></div>
<div class="metric">Sharpe<b>{metrics['holdout_sharpe_annualized']:.2f}</b></div>
<div class="metric">Hold-out observations<b>{metrics['n_obs_holdout']}</b></div>
<div class="metric">Date range<b>{metrics['holdout_start_date']} to {metrics['holdout_end_date']}</b></div></div></section>
<section><h2>Extreme-reading analysis</h2><div class="grid">
<div class="metric">Extreme hit rate<b>{metrics['holdout_hit_rate_extreme']:.1%}</b></div>
<div class="metric">95% CI<b>{ci_low:.1%} to {ci_high:.1%}</b></div>
<div class="metric">Middle hit rate<b>{metrics['holdout_hit_rate_middle']:.1%}</b></div>
<div class="metric">Extreme sample<b>{metrics['holdout_n_extreme_obs']}</b></div>
<div class="metric">Middle sample<b>{metrics['holdout_n_middle_obs']}</b></div></div>
<p class="caption">Extreme means score <= {q_low:.4f} or score >= {q_high:.4f}, thresholds fit only on training. Hold-out extreme share was {diag['holdout_extreme_share']:.1%}; it is not forced to 20%.</p></section>
<section><h2>Variable importance ranking</h2><table><thead><tr><th>Variable</th><th>Category</th><th>Importance</th><th>Sign</th></tr></thead><tbody>{rows}</tbody></table></section>
<section><h2>Methodology summary</h2><p>The pipeline uses a chronological 80/20 split. Filtering, imputation, robust scaling, sign determination, selection, and thresholds are fit on training only. Embedded selection combines Elastic Net, shadow-variable Boruta, and clustered MDA using directional hit-rate decrease. The product score is an equal-weight signed robust-z composite.</p></section>
<section><h2>Limitations and failure modes</h2><p>Forward returns overlap, reducing independent observations. Feature release lags are inherited from the provided processed dataset. The CV remains post-selection for final selected variables, so the hold-out remains the key evidence. Extreme readings can fail under regime shifts or if the training score distribution no longer calibrates live score magnitudes.</p></section>
</body></html>"""
    (OUT_DIR / f"diagnostic_v2_{name}.html").write_text(html, encoding="utf-8")


def write_methodology(results: dict) -> None:
    text = f"""# USDCAD Replication Methodology v2

Implementation id: `{IMPLEMENTATION_ID}`

This rerun corrects the known v1 and Sibley audit issues without overwriting prior outputs.

## Corrections

- Extreme thresholds are now fit on training composite scores and applied unchanged to hold-out.
- Hold-out imputation, scaling, sign determination, selection, and thresholding use no hold-out information.
- Score construction is a single coherent signed robust-z composite for both CV and hold-out.
- DSR is now a probability-style Bailey-Lopez de Prado approximation using per-period Sharpe, skew/kurtosis adjustment, and `n_trials = input features + embedded selection families`.
- Sharpe annualization uses `sqrt(252 / horizon_days)`.
- Clustered MDA uses direction-hit decrease rather than R2 decrease.

## Sub-choices

- Filter: training-only Spearman plus mutual information; `abs(rho) >= 0.03 and p <= 0.10`, or MI above median positive MI; coverage must be at least 20%.
- Embedded selection: Elastic Net CV, shadow-variable Boruta approximation with hit-rate threshold, and correlation-clustered MDA.
- Voting: at least two of three embedded votes; deterministic top-ranked fallback if fewer than three survive.
- CV: 10 expanding purged walk-forward folds on training data. CV uses final selected variables but fold-local scaling and signs, so it is a post-selection diagnostic. Hold-out is the binding test.
- Sign determination: Spearman sign on training data for final model; fold-local Spearman signs for CV.
- Score: mean of selected robust-z variables after multiplying by training-derived signs. Positive predicts USD/CAD up/CAD weakening.

## Horizon Summary

"""
    for name, m in results["horizons"].items():
        text += f"""### {name.capitalize()}

- Hold-out: {m['holdout_start_date']} to {m['holdout_end_date']}
- Selected features: {', '.join(m['selected_features'])}
- Aggregate hit: {m['holdout_hit_rate_aggregate']:.1%}
- Extreme hit: {m['holdout_hit_rate_extreme']:.1%} vs middle {m['holdout_hit_rate_middle']:.1%}
- Verdict: `{m['verdict']}`

"""
    (OUT_DIR / "methodology_v2.md").write_text(text, encoding="utf-8")


def write_assessment(results: dict) -> None:
    lines = ["# Honest Assessment v2\n\n"]
    for name, m in results["horizons"].items():
        lines.append(f"## {name.capitalize()}\n\n")
        lines.append(f"Corrected hold-out aggregate hit rate was {m['holdout_hit_rate_aggregate']:.1%}. ")
        lines.append(f"Training-threshold extreme hit rate was {m['holdout_hit_rate_extreme']:.1%} versus {m['holdout_hit_rate_middle']:.1%} in the middle bucket, with {m['holdout_n_extreme_obs']} extreme observations. ")
        lines.append(f"Product action: {m['verdict'].replace('_', ' ')}. {m['verdict_justification']}\n\n")
    (OUT_DIR / "honest_assessment_v2.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    np.random.seed(RANDOM_SEED)
    OUT_DIR.mkdir(exist_ok=True)
    variables = pd.read_parquet(VARIABLES_PATH)
    targets = pd.read_parquet(TARGETS_PATH)
    variables["date"] = pd.to_datetime(variables["date"])
    targets["date"] = pd.to_datetime(targets["date"])
    merged = variables.merge(targets, on="date", how="inner").sort_values("date").reset_index(drop=True)
    feature_cols = [c for c in variables.columns if c != "date"]

    horizons = {}
    diagnostics = {}
    for name, cfg in HORIZONS.items():
        metrics, diag = run_horizon(name, cfg, merged, feature_cols)
        horizons[name] = metrics
        diagnostics[name] = diag
        write_html(name, metrics, diag)

    results = {
        "implementation_id": IMPLEMENTATION_ID,
        "methodology_summary": {
            "filter_method": "training-only Spearman plus mutual information with coverage and uniqueness screens",
            "filter_threshold": "coverage >= 20%, unique observed values >= 3, and (abs(rho) >= 0.03 with p <= 0.10 or MI >= median positive MI)",
            "embedded_methods": ["elastic_net", "boruta_shadow_hit_rate", "clustered_directional_mda"],
            "embedded_voting_rule": "feature must pass the filter and receive at least two of three embedded-selection votes; deterministic top-ranked fallback if fewer than three survive",
            "cv_method": "purged_walkforward_post_selection_score_validation",
            "cv_fold_count": 10,
            "cv_embargo_days": 0,
            "cv_purge_rule": "for each expanding walk-forward validation block, remove the forecast-horizon number of observations immediately preceding validation from that fold's training set",
            "holdout_fraction": 0.20,
            "sign_determination_method": "training-only Spearman signs for final hold-out score; fold-local Spearman signs for CV",
            "imputation_method": "training median imputation fit separately within each fold and final training set",
            "standardization_method": "training-only robust z-score using median and IQR",
            "score_construction": "equal-weight signed robust-z composite; positive predicts USD/CAD up/CAD weakening",
            "extreme_threshold_definition": "training-score bottom decile plus top decile thresholds applied unchanged to hold-out",
            "dsr_n_trials": int(len(feature_cols) + 3),
        },
        "horizons": horizons,
        "confidence_rating": {
            "score_1_to_5": 3,
            "justification": "Known leakage/calibration bugs are corrected and hold-out remains clean, but overlapping labels and post-selection CV keep confidence moderate at best.",
        },
        "honest_assessment": "v2 is more defensible than v1 for product-style extreme readings because thresholds and preprocessing are train-derived. Hold-out evidence still controls the verdict.",
    }
    (OUT_DIR / "results_v2.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_methodology(results)
    write_assessment(results)


if __name__ == "__main__":
    main()
