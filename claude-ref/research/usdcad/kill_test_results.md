# Kill-test results: petrocurrency channel

Run: 2026-06-05T06:08Z  |  Break date: 2014-07-01  |  Dead zone: 1%  |  Weekly freq: Friday

## Data sources
- USDCAD: FRED DEXCAUS (CAD per USD), daily, converted to CAD-strength return: cad_ret = -pct_change(DEXCAUS)
- WTI oil: FRED DCOILWTICO, daily
- S&P 500: Yahoo Finance ^GSPC v8 chart API (Stooq now requires paid key), daily
- All resampled to weekly Friday close

## Sign check
Sign check 2007 cumulative cad_ret = 17.09% [PASS] (expected >3% for CAD appreciation episode)

## Week counts by bucket
```
  demand_decline           : 252
  demand_rally             : 366
  supply_decline           : 256
  supply_rally             : 242
  unclassified             : 261
```

### Main 2x2: break at 2014-07-01, dead zone 1%, Friday weeks

| regime               | period       | avg_cad_ret/wk | n_weeks | beta_cad_on_oil | r2     |
|----------------------|--------------|----------------|---------|-----------------|--------|
| demand_rally         | pre_break    | +0.6836% |    199 | +0.0673 | 0.0318 |
| demand_rally         | post_break   | +0.4159% |    167 | +0.0479 | 0.0390 |
| supply_rally         | pre_break    | -0.0308% |    148 | +0.0180 | 0.0031 |
| supply_rally         | post_break   | +0.0049% |     94 | +0.0013 | 0.0002 |


### Robustness: dead zone 2%, break 2014-07-01, Friday weeks

| regime               | period       | avg_cad_ret/wk | n_weeks | beta_cad_on_oil | r2     |
|----------------------|--------------|----------------|---------|-----------------|--------|
| demand_rally         | pre_break    | +0.7142% |    169 | +0.0713 | 0.0304 |
| demand_rally         | post_break   | +0.4596% |    133 | +0.0450 | 0.0323 |
| supply_rally         | pre_break    | +0.0054% |    113 | +0.0122 | 0.0015 |
| supply_rally         | post_break   | +0.0231% |     75 | +0.0004 | 0.0000 |


### Robustness: Wednesday weeks, dead zone 1%, break 2014-07-01

| regime               | period       | avg_cad_ret/wk | n_weeks | beta_cad_on_oil | r2     |
|----------------------|--------------|----------------|---------|-----------------|--------|
| demand_rally         | pre_break    | +0.6745% |    198 | +0.0266 | 0.0066 |
| demand_rally         | post_break   | +0.4984% |    171 | +0.0672 | 0.1076 |
| supply_rally         | pre_break    | -0.0861% |    139 | -0.0364 | 0.0125 |
| supply_rally         | post_break   | +0.0276% |     78 | -0.0141 | 0.0155 |


### Robustness: Friday weeks, dead zone 1%, break 2015-01-01

| regime               | period       | avg_cad_ret/wk | n_weeks | beta_cad_on_oil | r2     |
|----------------------|--------------|----------------|---------|-----------------|--------|
| demand_rally         | pre_break    | +0.6733% |    202 | +0.0703 | 0.0347 |
| demand_rally         | post_break   | +0.4238% |    164 | +0.0456 | 0.0357 |
| supply_rally         | pre_break    | -0.0424% |    149 | +0.0188 | 0.0033 |
| supply_rally         | post_break   | +0.0240% |     93 | +0.0007 | 0.0001 |


### Robustness: Friday weeks, dead zone 1%, break 2016-01-01

| regime               | period       | avg_cad_ret/wk | n_weeks | beta_cad_on_oil | r2     |
|----------------------|--------------|----------------|---------|-----------------|--------|
| demand_rally         | pre_break    | +0.6697% |    212 | +0.0617 | 0.0274 |
| demand_rally         | post_break   | +0.4126% |    154 | +0.0518 | 0.0476 |
| supply_rally         | pre_break    | -0.0565% |    156 | +0.0266 | 0.0061 |
| supply_rally         | post_break   | +0.0550% |     86 | -0.0014 | 0.0003 |


## Verdict
**MURKY**

Post-break demand-rally avg cad_ret = +0.4159% per week (beta = +0.0479); pre-break avg = +0.6836% (beta = +0.0673). Attenuation visible but not a clean break; inspect rolling-beta chart.


## Charts
- `work/research/usdcad/killtest_petrocurrency_trade.png` -- cumulative CAD return by regime
- `work/research/usdcad/killtest_rolling_demand_beta.png` -- 3-yr rolling beta, demand weeks