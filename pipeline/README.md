# pipeline

Python data pipeline for the Macro Research Department dashboard.

## Layout

- `fetch/` - one submodule per upstream source (StatCan WDS, BoC Valet, FRED, etc.)
- `transform/` - reusable analytical transforms (rolling means, YoY, indexing, smoothing)
- `io/` - disk I/O helpers, CSV + `.meta.json` contract
- `tests/` - unit tests for fetchers, transforms, and I/O

## Output contract

Every processed dataset written to `data/processed/` MUST ship with a sibling
`.meta.json` describing:

- source (e.g. "StatCan table 14-10-0287-01")
- fetch timestamp (UTC ISO 8601)
- units (e.g. "thousands of persons, seasonally adjusted")
- transforms applied (ordered list)
- vintage/release identifier where available

Downstream consumers (Astro pages, chart components) read both files.

## Source quirks

Source-specific quirks (release schedules, missing-data conventions, unit
oddities) belong in `data/SOURCES.md`. That file will be created when the
first source lands.
