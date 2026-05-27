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
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import ElasticNetCV
from sklearn.metrics import r2_score


warnings.filterwarnings(
    "ignore",
    message="`sklearn.utils.parallel.delayed` should be used with `sklearn.utils.parallel.Parallel`.*",
    category=UserWarning,
)

RANDOM_SEED = 20260527
OUT_DIR = Path("chatgpt_replication")
VARIABLES_PATH = Path("data/processed/usdcad_variables.parquet")
TARGETS_PATH = Path("data/processed/usdcad_targets.parquet")
IMPLEMENTATION_ID = "chatgpt-codex-2026-05-27"

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
    columns: list


def feature_category(feature: str) -> str:
    return CATEGORY_PREFIX.get(feature[:1], "Other")


def robust_fit_transform(train_x: pd.DataFrame) -> tuple[pd.DataFrame, RobustScalerState]:
    fill_values = train_x.median(numeric_only=True)
    fill_values = fill_values.fillna(0.0)
    filled = train_x.fillna(fill_values)
    medians = filled.median(numeric_only=True)
    q75 = filled.quantile(0.75)
    q25 = filled.quantile(0.25)
    iqrs = (q75 - q25).replace(0.0, np.nan).fillna(filled.std(ddof=0)).replace(0.0, 1.0)
    z = (filled - medians) / iqrs
    state = RobustScalerState(medians=medians, iqrs=iqrs, fill_values=fill_values, columns=list(train_x.columns))
    return z.astype(float), state


def robust_transform(x: pd.DataFrame, state: RobustScalerState) -> pd.DataFrame:
    aligned = x.reindex(columns=state.columns)
    filled = aligned.fillna(state.fill_values)
    return ((filled - state.medians) / state.iqrs).astype(float)


def make_purged_walkforward_splits(n: int, horizon_days: int, fold_count: int = 10) -> list[tuple[np.ndarray, np.ndarray]]:
    val_size = max(20, n // (fold_count + 2))
    initial_train = n - val_size * fold_count
    if initial_train < max(200, horizon_days * 5):
        val_size = max(20, n // (fold_count + 3))
        initial_train = n - val_size * fold_count
    splits = []
    for i in range(fold_count):
        val_start = initial_train + i * val_size
        val_end = n if i == fold_count - 1 else min(n, val_start + val_size)
        purge_end = max(0, val_start - horizon_days)
        train_idx = np.arange(0, purge_end)
        val_idx = np.arange(val_start, val_end)
        if len(train_idx) > 50 and len(val_idx) > 0:
            splits.append((train_idx, val_idx))
    return splits


def spearman_filter(x_train_raw: pd.DataFrame, y_train: pd.Series) -> tuple[list[str], dict]:
    details = {}
    mi_candidates = []
    usable_cols = []
    for col in x_train_raw.columns:
        s = x_train_raw[col]
        coverage = float(s.notna().mean())
        if coverage < 0.20 or s.dropna().nunique() < 3:
            details[col] = {"rho": 0.0, "pvalue": 1.0, "coverage": coverage, "mi": 0.0, "keep": False}
            continue
        joined = pd.concat([s, y_train], axis=1).dropna()
        if len(joined) < 100:
            rho, pval = 0.0, 1.0
        else:
            rho, pval = stats.spearmanr(joined.iloc[:, 0], joined.iloc[:, 1])
            if not np.isfinite(rho):
                rho, pval = 0.0, 1.0
        usable_cols.append(col)
        details[col] = {"rho": float(rho), "pvalue": float(pval), "coverage": coverage, "mi": 0.0, "keep": False}

    if usable_cols:
        tmp = x_train_raw[usable_cols].copy()
        tmp = tmp.fillna(tmp.median(numeric_only=True).fillna(0.0))
        mi = mutual_info_regression(tmp, y_train.to_numpy(), random_state=RANDOM_SEED, n_neighbors=5)
        for col, val in zip(usable_cols, mi):
            details[col]["mi"] = float(max(val, 0.0))
            if val > 0:
                mi_candidates.append(float(val))
    mi_cut = float(np.median(mi_candidates)) if mi_candidates else math.inf
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


def select_elastic_net(x: pd.DataFrame, y: pd.Series, splits: list[tuple[np.ndarray, np.ndarray]]) -> tuple[set[str], dict]:
    if x.shape[1] == 0:
        return set(), {}
    l1_ratios = [0.15, 0.5, 0.85, 1.0]
    cv = [(tr, va) for tr, va in splits if len(tr) > 20 and len(va) > 0]
    model = ElasticNetCV(
        l1_ratio=l1_ratios,
        alphas=np.logspace(-4, 1, 60),
        cv=cv,
        max_iter=20000,
        random_state=RANDOM_SEED,
        fit_intercept=True,
        n_jobs=-1,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(x.to_numpy(), y.to_numpy())
    coefs = pd.Series(model.coef_, index=x.columns)
    selected = set(coefs[coefs.abs() > 1e-8].index)
    info = {"alpha": float(model.alpha_), "l1_ratio": float(model.l1_ratio_), "coefs": coefs.to_dict()}
    return selected, info


def select_boruta(x: pd.DataFrame, y: pd.Series) -> tuple[set[str], dict]:
    if x.shape[1] == 0:
        return set(), {}
    rng = np.random.default_rng(RANDOM_SEED)
    real_imps = []
    shadow_maxes = []
    arr = x.to_numpy()
    for iteration in range(20):
        shadow = arr.copy()
        for j in range(shadow.shape[1]):
            rng.shuffle(shadow[:, j])
        combo = np.hstack([arr, shadow])
        rf = RandomForestRegressor(
            n_estimators=250,
            max_depth=5,
            min_samples_leaf=25,
            max_features="sqrt",
            random_state=RANDOM_SEED + iteration,
            n_jobs=-1,
        )
        rf.fit(combo, y.to_numpy())
        imp = rf.feature_importances_
        real_imps.append(imp[: x.shape[1]])
        shadow_maxes.append(float(np.percentile(imp[x.shape[1] :], 95)))
    real_mean = pd.Series(np.mean(real_imps, axis=0), index=x.columns)
    shadow_threshold = float(np.median(shadow_maxes))
    selected = set(real_mean[real_mean > shadow_threshold].index)
    if not selected and len(real_mean) > 0:
        selected = set(real_mean.sort_values(ascending=False).head(min(5, len(real_mean))).index)
    return selected, {"importance": real_mean.to_dict(), "shadow_threshold": shadow_threshold}


def correlation_clusters(x: pd.DataFrame, threshold: float = 0.75) -> list[list[str]]:
    corr = x.corr().abs().fillna(0.0)
    remaining = set(x.columns)
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


def select_clustered_mda(x: pd.DataFrame, y: pd.Series, splits: list[tuple[np.ndarray, np.ndarray]], horizon_days: int) -> tuple[set[str], dict]:
    if x.shape[1] == 0:
        return set(), {}
    clusters = correlation_clusters(x)
    decreases = {tuple(c): [] for c in clusters}
    rng = np.random.default_rng(RANDOM_SEED + horizon_days)
    for fold_no, (tr, va) in enumerate(splits[-5:]):
        if len(tr) < 50 or len(va) < 20:
            continue
        rf = RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            min_samples_leaf=25,
            max_features="sqrt",
            random_state=RANDOM_SEED + 100 + fold_no + horizon_days,
            n_jobs=-1,
        )
        rf.fit(x.iloc[tr].to_numpy(), y.iloc[tr].to_numpy())
        pred = rf.predict(x.iloc[va].to_numpy())
        baseline = r2_score(y.iloc[va].to_numpy(), pred)
        for cluster in clusters:
            xp = x.iloc[va].copy()
            for col in cluster:
                xp[col] = rng.permutation(xp[col].to_numpy())
            perm_pred = rf.predict(xp.to_numpy())
            decreases[tuple(cluster)].append(float(baseline - r2_score(y.iloc[va].to_numpy(), perm_pred)))
    cluster_scores = {cluster: float(np.mean(vals)) if vals else 0.0 for cluster, vals in decreases.items()}
    positives = [v for v in cluster_scores.values() if v > 0]
    cutoff = float(np.median(positives) * 0.25) if positives else math.inf
    selected = set()
    for cluster, score in cluster_scores.items():
        if score > cutoff:
            selected.update(cluster)
    if not selected:
        ranked = sorted(cluster_scores.items(), key=lambda kv: kv[1], reverse=True)
        for cluster, _ in ranked[: min(3, len(ranked))]:
            selected.update(cluster)
    feature_scores = {}
    for cluster, score in cluster_scores.items():
        for col in cluster:
            feature_scores[col] = score / max(1, len(cluster))
    return selected, {"clusters": [list(c) for c in clusters], "cluster_scores": {",".join(k): v for k, v in cluster_scores.items()}, "feature_scores": feature_scores}


def fit_final_model(x: pd.DataFrame, y: pd.Series, splits: list[tuple[np.ndarray, np.ndarray]]) -> tuple[ElasticNetCV, pd.Series]:
    model = ElasticNetCV(
        l1_ratio=[0.15, 0.5, 0.85, 1.0],
        alphas=np.logspace(-4, 1, 80),
        cv=[(tr, va) for tr, va in splits if len(tr) > 20 and len(va) > 0],
        max_iter=25000,
        random_state=RANDOM_SEED,
        fit_intercept=True,
        n_jobs=-1,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(x.to_numpy(), y.to_numpy())
    coefs = pd.Series(model.coef_, index=x.columns)
    return model, coefs


def coefficient_score(x: pd.DataFrame, coefs: pd.Series) -> np.ndarray:
    weights = coefs.reindex(x.columns).fillna(0.0)
    if np.all(np.abs(weights.to_numpy()) < 1e-10):
        weights = pd.Series(1.0 / max(1, x.shape[1]), index=x.columns)
    return x.to_numpy().dot(weights.to_numpy())


def predictive_score(model: ElasticNetCV, x: pd.DataFrame, coefs: pd.Series) -> np.ndarray:
    pred = model.predict(x.to_numpy())
    if np.nanstd(pred) < 1e-10:
        return coefficient_score(x, coefs)
    return pred


def annualized_sharpe(signal: np.ndarray, returns: np.ndarray, horizon_days: int) -> float:
    pnl = np.sign(signal) * returns
    pnl = pnl[np.isfinite(pnl)]
    if len(pnl) < 3 or np.std(pnl, ddof=1) == 0:
        return 0.0
    return float(np.mean(pnl) / np.std(pnl, ddof=1) * math.sqrt(252 / horizon_days))


def hit_rate(signal: np.ndarray, direction: np.ndarray) -> float:
    pred = np.where(signal >= 0, 1.0, -1.0)
    mask = np.isfinite(pred) & np.isfinite(direction)
    if mask.sum() == 0:
        return 0.0
    return float(np.mean(pred[mask] == direction[mask]))


def approximate_dsr(sharpe: float, n_obs: int, n_trials: int) -> tuple[float, float]:
    if n_obs <= 3:
        return 0.0, 1.0
    independent_trials = max(1, int(n_trials))
    expected_max_noise = stats.norm.ppf(1.0 - 1.0 / math.e / independent_trials) if independent_trials > 1 else 0.0
    sr_std = math.sqrt(max(1e-12, 1.0 / (n_obs - 1)))
    dsr = (sharpe - expected_max_noise) / sr_std
    pvalue = float(1.0 - stats.norm.cdf(dsr))
    return float(dsr), pvalue


def binomial_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return float(max(0.0, center - half)), float(min(1.0, center + half))


def plot_score_png(dates, scores, holdout_start, title) -> str:
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=140)
    ax.plot(dates, scores, color="#1f5f8b", linewidth=1.1)
    ax.axvspan(pd.to_datetime(holdout_start), pd.to_datetime(dates.iloc[-1]), color="#f0b44c", alpha=0.22, label="Hold-out")
    ax.axhline(0, color="#333333", linewidth=0.7)
    ax.set_title(title)
    ax.set_ylabel("Composite score")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    bio = BytesIO()
    fig.savefig(bio, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(bio.getvalue()).decode("ascii")


def verdict(metrics: dict) -> tuple[str, str]:
    ext = metrics["holdout_hit_rate_extreme"]
    mid = metrics["holdout_hit_rate_middle"]
    n_ext = metrics["holdout_n_extreme_obs"]
    dsr = metrics["dsr"]
    hold_sharpe = metrics["holdout_sharpe_annualized"]
    if n_ext >= 80 and ext >= 0.56 and ext - mid >= 0.04 and hold_sharpe > 0 and dsr > 0:
        return "ship_with_trade_ideas", "Extreme readings beat the middle bucket with enough observations and positive hold-out trading Sharpe; use as trade-idea context, not a standalone signal."
    if n_ext >= 50 and ext >= 0.52 and hold_sharpe >= -0.10:
        return "scorecard_only", "Signal is directionally usable as a dashboard component, but effect size and multiple-testing correction are not strong enough for standalone trade recommendations."
    return "do_not_ship", "Hold-out edge is too weak, unstable, or commercially unattractive given the cost of false conviction signals."


def run_horizon(name: str, cfg: dict, merged: pd.DataFrame, feature_cols: list[str]) -> tuple[dict, dict, pd.DataFrame]:
    horizon_days = cfg["days"]
    df = merged[["date", cfg["ret"], cfg["dir"]] + feature_cols].copy()
    df = df.dropna(subset=[cfg["ret"], cfg["dir"]]).sort_values("date").reset_index(drop=True)
    n_total = len(df)
    n_holdout = int(math.ceil(n_total * 0.20))
    n_train = n_total - n_holdout
    train = df.iloc[:n_train].reset_index(drop=True)
    holdout = df.iloc[n_train:].reset_index(drop=True)

    x_train_raw = train[feature_cols]
    y_train = train[cfg["ret"]].astype(float)
    filter_features, filter_details = spearman_filter(x_train_raw, y_train)
    x_filter_raw = x_train_raw[filter_features]
    x_train_z, scaler = robust_fit_transform(x_filter_raw)
    splits = make_purged_walkforward_splits(len(train), horizon_days, fold_count=10)

    en_selected, en_info = select_elastic_net(x_train_z, y_train, splits)
    boruta_selected, boruta_info = select_boruta(x_train_z, y_train)
    mda_selected, mda_info = select_clustered_mda(x_train_z, y_train, splits, horizon_days)

    votes = {}
    for col in filter_features:
        votes[col] = int(col in en_selected) + int(col in boruta_selected) + int(col in mda_selected)
    final_features = sorted([c for c, v in votes.items() if v >= 2])
    if len(final_features) < 3:
        rank_score = {}
        for col in filter_features:
            rank_score[col] = (
                votes.get(col, 0),
                abs(filter_details[col]["rho"]),
                boruta_info.get("importance", {}).get(col, 0.0),
                mda_info.get("feature_scores", {}).get(col, 0.0),
            )
        final_features = sorted(filter_features, key=lambda c: rank_score[c], reverse=True)[: min(5, len(filter_features))]

    final_scaler_raw = train[final_features]
    x_final_train, final_scaler = robust_fit_transform(final_scaler_raw)
    final_model, final_coefs = fit_final_model(x_final_train, y_train, splits)
    if np.all(np.abs(final_coefs.to_numpy()) < 1e-10):
        rho_signs = pd.Series({c: np.sign(filter_details[c]["rho"]) or 1.0 for c in final_features})
        final_coefs = rho_signs / max(1, len(rho_signs))

    # Out-of-sample CV predictions from the final selected variable set.
    cv_pred = np.full(len(train), np.nan)
    for tr, va in splits:
        fold_scaler_x, fold_scaler = robust_fit_transform(train.iloc[tr][final_features])
        model, coefs = fit_final_model(fold_scaler_x, train.iloc[tr][cfg["ret"]].astype(float), make_purged_walkforward_splits(len(tr), horizon_days, fold_count=5))
        x_va = robust_transform(train.iloc[va][final_features], fold_scaler)
        cv_pred[va] = predictive_score(model, x_va, coefs)
    cv_mask = np.isfinite(cv_pred)
    cv_hit = hit_rate(cv_pred[cv_mask], train.loc[cv_mask, cfg["dir"]].to_numpy())
    cv_r2 = float(r2_score(train.loc[cv_mask, cfg["ret"]].to_numpy(), cv_pred[cv_mask])) if cv_mask.sum() > 2 else 0.0
    cv_sharpe = annualized_sharpe(cv_pred[cv_mask], train.loc[cv_mask, cfg["ret"]].to_numpy(), horizon_days)
    n_trials = int(1 + len(filter_features) + 4 * 60 + 20 + len(mda_info.get("clusters", [])))
    dsr, dsr_p = approximate_dsr(cv_sharpe, int(cv_mask.sum()), n_trials)

    x_hold = robust_transform(holdout[final_features], final_scaler)
    hold_pred = predictive_score(final_model, x_hold, final_coefs)
    hold_hit = hit_rate(hold_pred, holdout[cfg["dir"]].to_numpy())
    hold_r2 = float(r2_score(holdout[cfg["ret"]].to_numpy(), hold_pred)) if len(holdout) > 2 else 0.0
    hold_sharpe = annualized_sharpe(hold_pred, holdout[cfg["ret"]].to_numpy(), horizon_days)

    q_low, q_high = np.quantile(hold_pred, [0.10, 0.90])
    extreme_mask = (hold_pred <= q_low) | (hold_pred >= q_high)
    middle_mask = ~extreme_mask
    hold_pred_dir = np.where(hold_pred >= 0, 1.0, -1.0)
    extreme_hits = int(np.sum(hold_pred_dir[extreme_mask] == holdout.loc[extreme_mask, cfg["dir"]].to_numpy()))
    middle_hits = int(np.sum(hold_pred_dir[middle_mask] == holdout.loc[middle_mask, cfg["dir"]].to_numpy()))
    extreme_n = int(extreme_mask.sum())
    middle_n = int(middle_mask.sum())
    extreme_hit_rate = float(extreme_hits / extreme_n) if extreme_n else 0.0
    middle_hit_rate = float(middle_hits / middle_n) if middle_n else 0.0
    ci_low, ci_high = binomial_ci(extreme_hits, extreme_n)

    all_x = robust_transform(df[final_features], final_scaler)
    full_score = predictive_score(final_model, all_x, final_coefs)

    importance = {}
    for col in final_features:
        importance[col] = float(
            abs(final_coefs.reindex(final_features).fillna(0.0).get(col, 0.0))
            + boruta_info.get("importance", {}).get(col, 0.0)
            + max(0.0, mda_info.get("feature_scores", {}).get(col, 0.0))
            + abs(filter_details[col]["rho"])
        )
    max_imp = max(importance.values()) if importance else 1.0
    importance = {k: v / max_imp for k, v in importance.items()}
    feature_signs = {col: int(1 if final_coefs.get(col, 0.0) >= 0 else -1) for col in final_features}

    metrics = {
        "horizon_days": horizon_days,
        "n_obs_total": int(n_total),
        "n_obs_train": int(n_train),
        "n_obs_holdout": int(n_holdout),
        "train_start_date": train["date"].iloc[0].strftime("%Y-%m-%d"),
        "train_end_date": train["date"].iloc[-1].strftime("%Y-%m-%d"),
        "holdout_start_date": holdout["date"].iloc[0].strftime("%Y-%m-%d"),
        "holdout_end_date": holdout["date"].iloc[-1].strftime("%Y-%m-%d"),
        "n_features_input": int(len(feature_cols)),
        "n_features_after_filter": int(len(filter_features)),
        "n_features_selected_final": int(len(final_features)),
        "selected_features": final_features,
        "feature_signs": feature_signs,
        "cv_hit_rate": cv_hit,
        "cv_r2": cv_r2,
        "cv_sharpe_annualized": cv_sharpe,
        "dsr": dsr,
        "dsr_pvalue": dsr_p,
        "holdout_hit_rate_aggregate": hold_hit,
        "holdout_r2": hold_r2,
        "holdout_sharpe_annualized": hold_sharpe,
        "holdout_hit_rate_extreme": extreme_hit_rate,
        "holdout_hit_rate_middle": middle_hit_rate,
        "holdout_n_extreme_obs": extreme_n,
        "holdout_n_middle_obs": middle_n,
    }
    v, just = verdict(metrics)
    metrics["verdict"] = v
    metrics["verdict_justification"] = just

    diagnostics = {
        "filter_details": filter_details,
        "elastic_net": en_info,
        "boruta": boruta_info,
        "mda": mda_info,
        "votes": votes,
        "importance": importance,
        "holdout_extreme_ci": [ci_low, ci_high],
        "holdout_score_thresholds": [float(q_low), float(q_high)],
        "full_dates": df["date"],
        "full_scores": pd.Series(full_score),
        "holdout_start": holdout["date"].iloc[0],
    }
    score_df = pd.DataFrame({"date": df["date"], "score": full_score})
    return metrics, diagnostics, score_df


def write_html(name: str, metrics: dict, diag: dict) -> None:
    label = name.capitalize()
    imp_rows = ""
    for feat, val in sorted(diag["importance"].items(), key=lambda kv: kv[1], reverse=True):
        imp_rows += f"<tr><td>{feat}</td><td>{feature_category(feat)}</td><td>{val:.3f}</td><td>{metrics['feature_signs'][feat]:+d}</td></tr>\n"
    img = plot_score_png(diag["full_dates"], diag["full_scores"], diag["holdout_start"], f"{label} USDCAD composite score")
    ci_low, ci_high = diag["holdout_extreme_ci"]
    q_low, q_high = diag["holdout_score_thresholds"]
    caveat = "This is not claiming a stable standalone alpha; it is a hold-out-tested scorecard component."
    confidence = "low" if metrics["verdict"] == "do_not_ship" else ("moderate" if metrics["verdict"] == "scorecard_only" else "moderate-high")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{label} USDCAD Diagnostic</title>
<style>
body {{ font-family: Arial, Helvetica, sans-serif; margin: 0; color: #17202a; background: #fbfbf8; }}
section {{ padding: 28px 42px; border-bottom: 1px solid #ddd8cc; }}
.hero {{ min-height: 100vh; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; background: #0f2b3a; color: #fff; }}
.hero h1 {{ font-size: 42px; margin: 0 0 16px; letter-spacing: 0; }}
.hero p {{ max-width: 940px; font-size: 18px; line-height: 1.45; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
.metric {{ background: #fff; border: 1px solid #d9d4c8; border-radius: 6px; padding: 14px; }}
.metric b {{ display: block; font-size: 24px; margin-top: 6px; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; }}
th, td {{ text-align: left; padding: 9px 10px; border-bottom: 1px solid #e5e0d6; }}
th {{ background: #efe9dc; }}
img {{ width: 100%; max-width: 1200px; height: auto; display: block; }}
.caption {{ color: #4c5963; font-size: 14px; line-height: 1.45; }}
</style>
</head>
<body>
<section class="hero">
<h1>{label} USDCAD direction score: {metrics['verdict'].replace('_', ' ')}</h1>
<p><b>Headline finding:</b> hold-out aggregate hit rate was {metrics['holdout_hit_rate_aggregate']:.1%}; extreme-score hit rate was {metrics['holdout_hit_rate_extreme']:.1%} versus {metrics['holdout_hit_rate_middle']:.1%} in the middle bucket.</p>
<p><b>Confidence:</b> {confidence}. We are claiming a reproducible, strictly out-of-sample evaluation of this framework on the provided dataset. We are not claiming the result is capacity-adjusted, transaction-cost-adjusted, or immune to regime change. {caveat}</p>
<p><b>Key caveats:</b> overlapping forward returns reduce independent observations; the DSR is an approximation to Bailey-Lopez de Prado using an explicit independent-trial count; Boruta and MDA are random-forest based and fixed-seed but still sample-dependent.</p>
</section>
<section>
<h2>Composite score chart over time</h2>
<img alt="Composite score chart" src="data:image/png;base64,{img}">
<p class="caption">The shaded region is the untouched most recent 20% hold-out. Positive scores predict USD/CAD up, which is CAD weakening; negative scores predict USD/CAD down, which is CAD strengthening.</p>
</section>
<section>
<h2>Hold-out performance summary</h2>
<div class="grid">
<div class="metric">Hit rate<b>{metrics['holdout_hit_rate_aggregate']:.1%}</b></div>
<div class="metric">R²<b>{metrics['holdout_r2']:.3f}</b></div>
<div class="metric">Annualized Sharpe<b>{metrics['holdout_sharpe_annualized']:.2f}</b></div>
<div class="metric">Hold-out observations<b>{metrics['n_obs_holdout']}</b></div>
<div class="metric">Date range<b>{metrics['holdout_start_date']} to {metrics['holdout_end_date']}</b></div>
</div>
<p class="caption">Hit rate is the fraction of dates where the score's sign matched the realized forward direction. R² is regression fit to forward log return. Sharpe signs the forward return by the predicted direction and annualizes by the forecast horizon.</p>
</section>
<section>
<h2>Extreme-reading analysis</h2>
<div class="grid">
<div class="metric">Extreme hit rate<b>{metrics['holdout_hit_rate_extreme']:.1%}</b></div>
<div class="metric">95% CI<b>{ci_low:.1%} to {ci_high:.1%}</b></div>
<div class="metric">Middle hit rate<b>{metrics['holdout_hit_rate_middle']:.1%}</b></div>
<div class="metric">Extreme sample<b>{metrics['holdout_n_extreme_obs']}</b></div>
<div class="metric">Middle sample<b>{metrics['holdout_n_middle_obs']}</b></div>
</div>
<p class="caption">Extreme means the bottom decile plus top decile of hold-out scores: score <= {q_low:.4f} or score >= {q_high:.4f}. The confidence interval is a Wilson binomial interval for the extreme bucket.</p>
</section>
<section>
<h2>Variable importance ranking</h2>
<table><thead><tr><th>Variable</th><th>Category</th><th>Importance</th><th>Sign</th></tr></thead><tbody>
{imp_rows}
</tbody></table>
</section>
<section>
<h2>Methodology summary</h2>
<p>The pipeline reserved the most recent 20% as hold-out before any fitting. The training sample used a Spearman plus mutual-information univariate filter, then three embedded selectors: purged-CV elastic net, random-forest Boruta with shadow variables, and correlation-clustered permutation MDA. Features passing at least two selectors formed the score; if fewer than three survived, the deterministic fallback used the highest-ranked filtered variables to keep the composite estimable.</p>
<p>Cross-validation used 10 expanding walk-forward folds. Each validation block was preceded by a purge equal to the forecast horizon, with no added embargo after the validation block because training is strictly historical relative to validation.</p>
</section>
<section>
<h2>Limitations and failure modes</h2>
<p>The model can fail when macro regimes shift, when oil/risk/rates relationships invert, or when the signal is mainly a crisis-period artifact. The evaluation does not include transaction costs, execution timing, position limits, or corporate hedging constraints. Because forecast returns overlap, apparent sample sizes overstate the number of independent bets, so the DSR and the extreme-reading comparison matter more than aggregate hit rate alone.</p>
</section>
</body></html>"""
    (OUT_DIR / f"diagnostic_{name}.html").write_text(html, encoding="utf-8")


def write_methodology(results: dict) -> None:
    text = f"""# USDCAD Replication Methodology

Implementation id: `{IMPLEMENTATION_ID}`

## Data and Hold-out

I used only `data/processed/usdcad_variables.parquet` and `data/processed/usdcad_targets.parquet`. For each horizon I sorted by date, dropped rows with missing target return or direction for that horizon, and reserved the most recent 20% as a clean hold-out before any filtering, scaling, selection, sign determination, or fitting.

## Sub-choices

- Filter method: Spearman rank correlation against forward log return plus mutual information regression on the training set only.
- Filter threshold: keep a variable if `abs(Spearman rho) >= 0.03` and `p <= 0.10`, or if mutual information is positive and at or above the median positive MI among usable variables. Variables with less than 20% training coverage or fewer than three unique observed values are removed. If fewer than five variables survive, a deterministic top-five rank by univariate evidence is used so the downstream composite remains estimable.
- Imputation: training median imputation. Features with all-missing training values receive zero after the coverage filter removes them.
- Standardization: robust z-score, `(x - training median) / training IQR`, fit on training data only.
- Embedded selection: Elastic Net CV, Boruta-style shadow-variable random forest, and clustered MDA.
- Voting rule: selected features must pass the filter and receive votes from at least two of the three embedded methods. If fewer than three survive, the highest-ranked filtered variables by votes, Spearman strength, Boruta importance, and MDA importance are used as a deterministic fallback.
- Cross-validation: 10 expanding walk-forward folds on the training sample.
- Purge rule: observations in the forecast horizon immediately before each validation block are removed from that fold's training set, so a training label cannot overlap the validation period.
- Embargo: zero extra days after validation because every fold trains only on history before the validation block; the historical-only split already prevents training on post-validation information.
- Sign determination: the final elastic-net coefficient sign defines the feature sign. If all coefficients shrink to zero, Spearman sign is used as a documented fallback.
- Score construction: final selected robust-z features feed a final Elastic Net regression for forward log return. The predicted return is the composite score. Positive means USD/CAD up, i.e. CAD weakening; negative means CAD strengthening.
- Extreme threshold: bottom decile plus top decile of hold-out scores for each horizon, evaluated once.
- Multiple testing correction: approximate Bailey-Lopez de Prado Deflated Sharpe Ratio using the purged-CV annualized Sharpe, the number of CV-predicted observations, and an explicit independent-trial count equal to one final model plus filtered variables plus elastic-net alpha/l1 trials plus Boruta iterations plus MDA clusters.

## Deviations and Practical Approximations

Boruta is implemented directly with shadow variables and random forests rather than through an external Boruta package. Clustered MDA uses absolute-correlation clusters and validation-block permutation decreases in R². The DSR uses the standard normal approximation to the expected maximum Sharpe under multiple independent trials; it is conservative for weak signals but still an approximation because exact independent trial dependence is not observable from this one run.

## Horizon Summary

"""
    for name, m in results["horizons"].items():
        text += f"""### {name.capitalize()}

- Training window: {m['train_start_date']} to {m['train_end_date']}
- Hold-out window: {m['holdout_start_date']} to {m['holdout_end_date']}
- Features after filter: {m['n_features_after_filter']}
- Final selected features: {', '.join(m['selected_features'])}
- Verdict: `{m['verdict']}`

"""
    (OUT_DIR / "methodology.md").write_text(text, encoding="utf-8")


def write_honest_assessment(results: dict) -> None:
    lines = ["# Honest Assessment\n"]
    for name, m in results["horizons"].items():
        found = "yes" if m["holdout_hit_rate_extreme"] > m["holdout_hit_rate_middle"] and m["holdout_sharpe_annualized"] > 0 else "no"
        confidence = "low"
        if m["verdict"] == "scorecard_only":
            confidence = "moderate-low"
        elif m["verdict"] == "ship_with_trade_ideas":
            confidence = "moderate"
        lines.append(f"## {name.capitalize()}\n")
        lines.append(f"- Did the methodology find a signal? {found}. Aggregate hold-out hit rate was {m['holdout_hit_rate_aggregate']:.1%}; extreme hit rate was {m['holdout_hit_rate_extreme']:.1%} versus {m['holdout_hit_rate_middle']:.1%} in the middle bucket.\n")
        lines.append(f"- Confidence: {confidence}. CV Sharpe was {m['cv_sharpe_annualized']:.2f}, DSR was {m['dsr']:.2f}, and hold-out Sharpe was {m['holdout_sharpe_annualized']:.2f}.\n")
        lines.append("- What would convince me it is fake? A rolling-origin rerun where selected variables churn heavily, extreme readings stop beating middle readings, or performance concentrates in one crisis/regime would make me treat it as data-mined.\n")
        lines.append(f"- Product action: {m['verdict'].replace('_', ' ')}. {m['verdict_justification']}\n\n")
    results_verdicts = [m["verdict"] for m in results["horizons"].values()]
    if all(v == "do_not_ship" for v in results_verdicts):
        overall = "Overall, I would not sell this as a conviction product from this run. It may still be useful as research input."
    elif "ship_with_trade_ideas" in results_verdicts:
        overall = "Overall, I would restrict trade-idea use to the horizons that passed the extreme-reading and Sharpe checks."
    else:
        overall = "Overall, I would use this as a scorecard component, not as a standalone trade signal."
    lines.append(f"## Overall\n\n{overall}\n")
    (OUT_DIR / "honest_assessment.md").write_text("".join(lines), encoding="utf-8")


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
        metrics, diag, _score_df = run_horizon(name, cfg, merged, feature_cols)
        horizons[name] = metrics
        diagnostics[name] = diag
        write_html(name, metrics, diag)

    dsr_trials = max(int(m["n_features_after_filter"] + 1 + 4 * 60 + 20) for m in horizons.values())
    results = {
        "implementation_id": IMPLEMENTATION_ID,
        "methodology_summary": {
            "filter_method": "training-only Spearman rank correlation plus mutual information regression, with minimum coverage and uniqueness screens",
            "filter_threshold": "coverage >= 20%, unique observed values >= 3, and (abs(rho) >= 0.03 with p <= 0.10 or MI >= median positive MI); deterministic top-five fallback if fewer than five survive",
            "embedded_methods": ["elastic_net", "boruta", "clustered_mda"],
            "embedded_voting_rule": "feature must pass the filter and receive at least two of three embedded-selection votes; deterministic top-ranked fallback if fewer than three survive",
            "cv_method": "purged_walkforward",
            "cv_fold_count": 10,
            "cv_embargo_days": 0,
            "cv_purge_rule": "for each expanding walk-forward validation block, remove the forecast-horizon number of observations immediately preceding validation from that fold's training set",
            "holdout_fraction": 0.20,
            "sign_determination_method": "final elastic-net coefficient sign; Spearman sign fallback only if all final coefficients shrink to zero",
            "imputation_method": "training median imputation fit separately within each fold and final training set",
            "standardization_method": "training-only robust z-score using median and IQR",
            "score_construction": "Elastic Net prediction of forward log return from selected robust-z variables; positive predicts USD/CAD up/CAD weakening, negative predicts CAD strengthening",
            "extreme_threshold_definition": "bottom decile plus top decile of hold-out composite scores for each horizon",
            "dsr_n_trials": int(dsr_trials),
        },
        "horizons": horizons,
        "confidence_rating": {
            "score_1_to_5": 2,
            "justification": "The process is leakage-controlled and reproducible, but overlapping labels, weak DSR evidence, and a single historical hold-out limit confidence.",
        },
        "honest_assessment": "False conviction signals are worse than missed signals. I would only ship horizons whose hold-out extreme readings clearly beat the middle bucket with positive hold-out Sharpe; otherwise the output belongs in a scorecard or research workflow.",
    }

    (OUT_DIR / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_methodology(results)
    write_honest_assessment(results)


if __name__ == "__main__":
    main()
