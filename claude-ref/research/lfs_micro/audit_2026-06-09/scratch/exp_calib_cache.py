# Audit experiments E-F: recompute calibration metrics from production CSVs
# (read-only) and probe the engine-cache gates with _RAW_PUMF_DIR patched to a
# scratch sandbox (the same isolation pattern the tests use).
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\jayzh\projects\macro-research-department")
SCRATCH = ROOT / "claude-ref/research/lfs_micro/audit_2026-06-09/scratch"
sys.path.insert(0, str(ROOT))

print("================ E: calibration metrics recompute ================")
rep = pd.read_csv(ROOT / "data/processed/lfs_micro_replication.csv", parse_dates=["date"])
boc = pd.read_csv(ROOT / "data/raw/lfs_micro.csv", parse_dates=["date"])
r = rep.set_index("date")["underlying_pct"].dropna()
b = boc.set_index("date")["value"].astype(float)
print(f"ours: {r.index.min().date()}..{r.index.max().date()} n={len(r)}")
print(f"BoC : {b.index.min().date()}..{b.index.max().date()} n={len(b)}")
# check BoC has internal gaps in overlap window
boc_overlap = b[(b.index >= r.index.min()) & (b.index <= r.index.max())]
full_cal = pd.date_range(r.index.min(), b.index.max(), freq="MS")
missing_in_boc = sorted(set(full_cal) - set(boc_overlap.index))
print(f"BoC months missing within overlap window: {[d.strftime('%Y-%m') for d in missing_in_boc]}")

for lag in (-1, 0, 1):
    shifted = r.copy()
    shifted.index = shifted.index + pd.DateOffset(months=lag)
    common = shifted.index.intersection(b.index)
    d = shifted.loc[common] - b.loc[common]
    rmse = float(np.sqrt((d ** 2).mean()))
    mae = float(d.abs().mean())
    corr = float(shifted.loc[common].corr(b.loc[common]))
    print(f"lag {lag:+d}: n={len(common):3d}  RMSE={rmse:.4f}pp  MAE={mae:.4f}pp  corr={corr:.4f}")

# roughness claim: std of m/m changes
common = r.index.intersection(b.index)
print(f"std m/m changes: BoC={b.loc[common].diff().std():.3f}pp ours={r.loc[common].diff().std():.3f}pp")
# claimed: RMSE=0.1181, corr=0.9966, n=122

print()
print("================ F: engine cache gate probes ================")
import pipeline.lfs_micro.run as run_mod

sandbox = SCRATCH / "cache_sandbox"
if sandbox.exists():
    shutil.rmtree(sandbox)
sandbox.mkdir(parents=True)
orig = run_mod._RAW_PUMF_DIR
run_mod._RAW_PUMF_DIR = sandbox
try:
    # fake parquets for fingerprinting
    (sandbox / "2025-01.parquet").write_bytes(b"fake parquet content v1")
    (sandbox / "2024-01.parquet").write_bytes(b"fake base parquet v1")

    good_row = {
        "date": "2025-01-01", "underlying_lp": 0.03, "composition_lp": 0.005,
        "raw_mean_lp": 0.035, "total_fitted_lp": 0.035,
        "n_obs_curr": 50000, "n_obs_base": 51000, "r2_curr": 0.61, "r2_base": 0.62,
    }
    run_mod._save_cache("2025-01", good_row)
    hit = run_mod._load_cache("2025-01")
    print("F1 valid entry loads:", "PASS" if hit is not None else "FAIL")

    # F2: tamper the parquet content (same size) -> sha256 must miss
    (sandbox / "2025-01.parquet").write_bytes(b"fake parquet content v2")
    miss = run_mod._load_cache("2025-01")
    print("F2 content tamper (same size) -> miss:", "PASS" if miss is None else "FAIL")
    (sandbox / "2025-01.parquet").write_bytes(b"fake parquet content v1")  # restore

    # F3: tamper the BASE month parquet -> must also miss
    (sandbox / "2024-01.parquet").write_bytes(b"fake base parquet v2")
    miss = run_mod._load_cache("2025-01")
    print("F3 base-month tamper -> miss:", "PASS" if miss is None else "FAIL")
    (sandbox / "2024-01.parquet").write_bytes(b"fake base parquet v1")

    # F4: delete a parquet -> miss (fingerprint '' never matches)
    (sandbox / "2024-01.parquet").unlink()
    miss = run_mod._load_cache("2025-01")
    print("F4 missing parquet -> miss:", "PASS" if miss is None else "FAIL")
    (sandbox / "2024-01.parquet").write_bytes(b"fake base parquet v1")

    # F5: implausible row refused at save time
    bad = dict(good_row, n_obs_curr=325, r2_curr=0.09)
    try:
        run_mod._save_cache("2025-02", bad)
        print("F5 implausible save refused: FAIL (no exception)")
    except RuntimeError:
        print("F5 implausible save refused: PASS")

    # F6: hand-plant an implausible entry (attacker/corruption path) -> load must miss
    p = sandbox / "_engine_cache" / "2025-03.json"
    planted = dict(good_row, date="2025-03-01", n_obs_curr=325, r2_curr=0.09)
    planted["spec"] = json.loads((sandbox / "_engine_cache" / "2025-01.json").read_text())["spec"]
    # give it CORRECT fingerprints so only the plausibility gate can catch it
    fp = {}
    for k in ("2025-03", "2024-03"):
        (sandbox / f"{k}.parquet").write_bytes(b"x" + k.encode())
    planted["parquet_fingerprints"] = run_mod._parquet_fingerprints("2025-03")
    p.write_text(json.dumps(planted))
    miss = run_mod._load_cache("2025-03")
    print("F6 planted implausible entry -> miss:", "PASS" if miss is None else "FAIL")

    # F7: spec field change -> miss (edit cached spec)
    p = sandbox / "_engine_cache" / "2025-01.json"
    data = json.loads(p.read_text())
    data["spec"]["min_cell_count"] = 25
    p.write_text(json.dumps(data))
    miss = run_mod._load_cache("2025-01")
    print("F7 spec change -> miss:", "PASS" if miss is None else "FAIL")
    data["spec"]["min_cell_count"] = 30
    p.write_text(json.dumps(data))

    # F8: regressor-set change -> miss
    data["spec"]["regressor_set"] = [c for c in data["spec"]["regressor_set"] if c != "firmsize"]
    p.write_text(json.dumps(data))
    miss = run_mod._load_cache("2025-01")
    print("F8 regressor-set change -> miss:", "PASS" if miss is None else "FAIL")

    # F9: entry with NO fingerprints (legacy) -> miss
    data = json.loads(p.read_text())
    data["spec"]["regressor_set"] = sorted(
        c for c, _ in __import__("pipeline.lfs_micro.regression", fromlist=["REGRESSOR_GROUPS"]).REGRESSOR_GROUPS)
    del data["parquet_fingerprints"]
    p.write_text(json.dumps(data))
    miss = run_mod._load_cache("2025-01")
    print("F9 legacy entry without fingerprints -> miss:", "PASS" if miss is None else "FAIL")

    # F10: missing n_obs/r2 keys entirely -> miss (defaults 0 fail the gate)
    data["parquet_fingerprints"] = run_mod._parquet_fingerprints("2025-01")
    for k in ("n_obs_curr", "n_obs_base", "r2_curr", "r2_base"):
        data.pop(k, None)
    p.write_text(json.dumps(data))
    miss = run_mod._load_cache("2025-01")
    print("F10 entry missing n/r2 keys -> miss:", "PASS" if miss is None else "FAIL")
finally:
    run_mod._RAW_PUMF_DIR = orig
    shutil.rmtree(sandbox, ignore_errors=True)

print()
print("Sanity: production _RAW_PUMF_DIR restored:", run_mod._RAW_PUMF_DIR)
