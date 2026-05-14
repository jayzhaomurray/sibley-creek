"""API client modules. One submodule per upstream source.

Currently wired:
    statcan    - Statistics Canada Web Data Service (WDS)
    cpi_basket - StatCan Table 18-10-0007 CPI basket weights (basket-cycle cadence)
    boc        - Bank of Canada Valet
    fred       - FRED (US comparators: DGS10, VIX, DTWEXBGS, IG/HY OAS, oil)
    yahoo      - Yahoo Finance daily closes (TSX ^GSPTSE, S&P 500 ^GSPC, gold GC=F)
    indeed_hiring_lab - Indeed Hiring Lab Canada postings (daily SA index)
    crea       - CREA MLS HPI XLSX bulk (CMA-level housing)
    dof_fiscal - Department of Finance Fiscal Monitor HTML scraper
    alberta    - Alberta Economic Dashboard (monthly natural gas / WCS-ready)
    imf_weo    - IMF World Economic Outlook DataMapper (annual macro indicators)

To be added later (deferred to Wave 3 / v1.5):
    bis      - BIS bulk downloads (peer central bank policy rates)
    cmhc     - CMHC housing data
    osfi     - OSFI regulated entity data

Each submodule exposes:
    - one or more `fetch_*` functions returning a typed result
      (dataclass containing a pandas DataFrame and source metadata)
    - a URL helper (e.g. observations_url, table_url, series_url) so callers
      can record the exact upstream URL in the .meta.json sidecar

The shared HTTP client + retry policy live in pipeline.fetch._http.
"""

from pipeline.fetch import (
    alberta,
    boc,
    cpi_basket,
    crea,
    dof_fiscal,
    fred,
    imf_weo,
    indeed_hiring_lab,
    statcan,
    yahoo,
)

__all__ = [
    "alberta",
    "boc",
    "cpi_basket",
    "crea",
    "dof_fiscal",
    "fred",
    "imf_weo",
    "indeed_hiring_lab",
    "statcan",
    "yahoo",
]
