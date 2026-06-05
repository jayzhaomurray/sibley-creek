"""BoC Shadow Policy Rate — internal Sibley Creek research tool.

Reconstructs the Bank of Canada's *unpublished* rule-implied policy rate path
from the Bank's own published outputs: ToTEM III's estimated policy rule
(Technical Report 119, Table 2.3) applied to the latest Monetary Policy Report
projections (core CPI, GDP growth, output gap, potential growth, neutral range).

Self-contained package, manual quarterly trigger, NOT registered in
pipeline.build. Mirrors the pipeline/usdcad/ precedent.

Sub-modules:
    inputs  -- openpyxl parse of the punch-in workbook + pydantic validation
    model   -- forecast merge/interpolation, gap evolution, t+4 lookup, rule
               iteration
    chart   -- matplotlib -> SVG + minimal HTML wrapper
    run     -- `python -m pipeline.shadow_rate.run` CLI entry point
"""
