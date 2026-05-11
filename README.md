# Macro Research Department

A small dashboard surfacing Canadian macroeconomic indicators. Static site
built with Astro, data pipeline written in Python.

> Scope and editorial intent: see `editorial/dashboard_purpose.md`
> Visual specification and design system: see `design/design-system.md`
>
> Both files are the authoritative briefs for this project. They are being
> drafted in parallel; read them before adding pages, charts, or styles.

## Repo layout

```
.
├── src/              Astro app (pages, layouts, components, styles)
├── public/           Static assets served as-is
├── charts/           Reusable chart components
├── design/           Design system (owned by art-director)
├── editorial/        Briefs, blurbs, scope (owned by editorial-director)
├── research/         Researcher's insight base
├── data/
│   ├── raw/          Cached upstream fetches (ignored by git)
│   └── processed/    Cleaned CSV + sibling .meta.json files
├── pipeline/         Python data pipeline
└── scripts/          Build and data utility scripts
```

## Prerequisites

- Node.js >= 22.12.0 (tested with 24.15.0)
- npm 11+ (ships with the Node above)
- Python >= 3.11 (tested with 3.14)
- Git

## Astro quickstart (PowerShell)

From the project root:

```powershell
npm install
npm run dev
```

Other scripts:

```powershell
npm run build      # production build into ./dist
npm run preview    # serve the built site locally
npm run check      # type-check Astro + TypeScript
```

## Python pipeline quickstart (PowerShell)

The pipeline lives at `pipeline/`. It fetches data from public APIs
(Statistics Canada WDS, Bank of Canada Valet, etc.), validates the response
shape, applies analytical transforms, and writes the result as CSV + sibling
`.meta.json` under `data/raw/` and `data/processed/`. The Astro site reads
the processed files at build time.

Prepare an isolated environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r pipeline\requirements.txt
```

Run the full pipeline (fetch + transform):

```powershell
python -m pipeline.build
```

Output:

```
data/raw/<name>.csv          one per upstream series
data/raw/<name>.meta.json    sidecar: source, fetched-at, release date, units
data/processed/<name>.csv    transformed views the site consumes
data/processed/<name>.meta.json
```

Run tests:

```powershell
python -m pytest
```

Tests mock the HTTP layer; they do not hit live APIs. The pipeline build
itself does hit live APIs; expect a few seconds of network time.

To leave the venv:

```powershell
deactivate
```

If PowerShell refuses to run `Activate.ps1` due to execution policy, run
this once per user (not per session):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Two-step build

This project intentionally separates data preparation from site rendering:

1. `python -m pipeline.build` populates `data/processed/`. Pure Python.
2. `npm run build` reads `data/processed/` and renders the Astro site.

The two halves share the on-disk contract documented in `data/SOURCES.md`
and `ARCHITECTURE.md` (ADR-0002, ADR-0004). They do not need to run on
the same machine in the same invocation; CI runs them in sequence in a
single workflow.

## Working with Claude Code

This project uses several specialist Claude Code agents (editorial-director,
researcher, art-director, frontend-designer, chart-builder, and this backend
agent). To launch Claude Code in this repo, open a fresh PowerShell terminal
in the project root and run `claude` manually.

## Status

Phase 0 (scaffolding) complete. Data sources and chart inventory will be
scoped by the editorial director before pipeline work begins.
