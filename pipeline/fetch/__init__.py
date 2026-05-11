"""API client modules. One submodule per upstream source.

Currently wired:
    statcan  - Statistics Canada Web Data Service (WDS)
    boc      - Bank of Canada Valet

To be added as editorial-director / researcher scope new series:
    fred     - FRED (US comparators)
    alberta  - Alberta Economic Dashboard (WCS oil price etc.)
    bis      - BIS bulk downloads (peer central bank policy rates)
    cmhc     - CMHC housing data
    osfi     - OSFI regulated entity data

Each submodule exposes:
    - one or more `fetch_*` functions returning a typed result
      (dataclass containing a pandas DataFrame and source metadata)
    - a URL helper (e.g. observations_url, table_url) so callers can record
      the exact upstream URL in the .meta.json sidecar

The shared HTTP client + retry policy live in pipeline.fetch._http.
"""

from pipeline.fetch import boc, statcan

__all__ = ["boc", "statcan"]
