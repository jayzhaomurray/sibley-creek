# Auto-blurb pipeline

Multi-agent orchestration for the auto-blurb cycle. Covers the full
Sibley Creek section set: `inflation`, `labour`, `gdp`, `housing`,
`markets`, `policy`, `trade`. See `editorial/auto_blurb_process.md`
for the full design and `pipeline/blurbs/section_context.py` for the
per-section plate inventories and canonical sources the researcher
seeds against.

## CLI

```
python -m pipeline.blurbs.run --release-id cpi_monthly_2026-04
python -m pipeline.blurbs.run --release-id lfs_monthly_2026-04 --section labour
python -m pipeline.blurbs.run --release-id gdp_monthly_2026-02 --section gdp --dry-run
python -m pipeline.blurbs.run --release-id cpi_monthly_2026-04 --surface panel_1_headline_cpi
```

`--release-id` is free-form of the form `<release_key>_<YYYY-MM>` (or
`<release_key>_<YYYY-MM-DD>` for daily-cadence releases). Convention
`<section>_<release-type>_<YYYY-MM>` also works -- the parser splits
on the trailing date suffix. Canonical release-keys per section:

| section   | release-key       | example release-id                |
|-----------|-------------------|-----------------------------------|
| inflation | `cpi_monthly`     | `cpi_monthly_2026-04`             |
| labour    | `lfs_monthly`     | `lfs_monthly_2026-04`             |
| gdp       | `gdp_monthly`     | `gdp_monthly_2026-02`             |
| housing   | `crea_monthly`    | `crea_monthly_2026-04`            |
| markets   | `markets_daily`   | `markets_daily_2026-05-12`        |
| policy    | `boc_decision`    | `boc_decision_2026-06-10`         |
| trade     | `trade_monthly`   | `trade_monthly_2026-03`           |

`--section <slug>` is an optional guard: when set, the orchestrator
asserts the release-id resolves to that section's canonical release-
key. Useful to catch typos in the release-id at submit time.

`--dry-run` writes the wrapper cycle JSON and per-surface artifact stubs
in `release_landed` state without dispatching any agents. Useful for
inspecting the fan-out before running an LLM cycle.

`--surface <id>` re-runs only that surface against the existing cycle
file (e.g. after a user rejection).

After the cycle completes, bulk-approve every surface with:

```
python -m pipeline.blurbs.approve_cycle --release-id <release-id> --all
```

## Surfaces per section

Every section emits the same canonical surface set:

- one `homepage_abstract` (the splash hero rewrites on every section's
  release because the hero synthesises from section blurbs per
  writing-style 8b)
- one `topic_abstract` (the section page abstract)
- one `sparkline_blurb` (the splash tile-line for the section)
- one `active_headline` (the section page's hero line)
- one `chart_commentary` per plate on the section page

Per-section plate inventories live in
`pipeline/blurbs/section_context.py` `SECTION_CONTEXTS`. The current
surface counts (homepage + topic + sparkline + headline + plates) are:

| section   | plates | total surfaces |
|-----------|--------|----------------|
| inflation |   4    |       8        |
| labour    |  10    |      14        |
| gdp       |   6    |      10        |
| housing   |   7    |      11        |
| markets   |   6    |      10        |
| policy    |   7    |      11        |
| trade     |   6    |      10        |

### Length budgets

| kind              | cap | words   | sentences |
|-------------------|-----|---------|-----------|
| homepage_abstract | 560 | 60-110  | 3-4       |
| topic_abstract    | 480 | 45-90   | 2-3       |
| sparkline_blurb   | 120 | 10-25   | 1-2       |
| active_headline   | 140 |  8-22   | 1         |
| chart_commentary  | 500 | 25-95   | 2-4       |

### Inflation-specific gates

Inflation keeps hand-curated panel gates: panel 5 (expectations, CSCE /
BOS -- separate release) and panel 6 (passthrough -- chart currently
broken) are marked `False` in `RELEASE_KEYS["cpi_monthly"].panels`. The
inflation surface IDs (`panel_1_headline_cpi`, `panel_2_core_measures`,
etc) are preserved as-is for backwards compatibility with the existing
researcher prompt template and any landed cycle artifacts.

Other sections use generated surface IDs of the form
`<section>_<surface_slug>` (e.g. `labour_panel_1_headline_jobs`,
`gdp_panel_3_industry_split`). If a section page gains or loses a
plate, update `section_context.SECTION_CONTEXTS[<slug>].plate_inventory`
and the registry follows on the next import.

## Researcher section-context

The `.claude/commands/auto-blurb-researcher.md` prompt template is
section-agnostic. At fan-out time the orchestrator's researcher
dispatch should prepend the section-context block rendered by
`pipeline.blurbs.section_context.render_researcher_context_block(<slug>)`
so the researcher knows the section's canonical sources, primary
series, release quirks, and plate inventory. This is the seam where
section-specific seeding happens without forking the template.

## State machine

```
release_landed -> context_drafted -> claims_verified -> writer_drafted
              -> fact_checked    -> style_polished  -> ready_for_user
              -> approved        -> published
```

Retry budgets (per spec):

- Researcher: 2 round-trips on claims-verification failure
- Writer + fact-checker: 3 round-trips
- Style-editor: 1 re-draft

Exhaustion transitions the surface to `escalated`; the cycle still emits
the batched email with an `[ESCALATED]` marker on the affected surface.

## LLM dispatch mechanism

Phase 1 ships the orchestration + dispatch hooks; the agent dispatch
implementations are pluggable callables registered at
`run.run_release_cycle(researcher_dispatch=..., writer_dispatch=...,
style_dispatch=...)`. Tests pass fixture callables. Production wiring is:

### Verifier (Mode A, claims-verification)

The verifier is implemented as a hybrid:

1. **Mechanical checks (no LLM)** run in `pipeline/blurbs/verify_claims.py`:
   `url_404`, `text_not_present` (string match), `value_mismatch` (string
   match near the excerpt), `source_kind_mismatch` (domain check). These
   are deterministic httpx fetches and require no API.
2. **LLM judgment for `claim_overreach`**: dispatched via the Anthropic
   API direct (`anthropic.Anthropic().messages.create`) with model pin
   `claude-opus-4-7` per the user-confirmed spec. Each card is one
   fresh-context API call (no batching) -- this is the structural defense
   against LLM consistency bias per `auto_blurb_process.md` Section 1.1.

**Env var required:** `ANTHROPIC_API_KEY`. If the env var is unset or
the `anthropic` package is not installed, `verify_claim_file` runs the
mechanical checks only and the `claim_overreach` axis falls through to
human review (flagged in `verifier_notes` for affected cards).

### Writer / fact-checker / style-editor (Sonnet)

Per the user confirmation:

- Writer: `claude-sonnet-4-7`, dispatched per-surface in serial (Phase 1
  picks serial for simplicity; parallel deferred to Phase 2 once the
  agent-orchestration choreography is shaken down).
- Fact-checker (Mode B, draft-verification): does NOT need the LLM in
  Phase 1. Mode B is mechanical: numeric token extraction + per-token
  card lookup. The LLM-judgment piece (`claim_overreach` on the writer's
  prose) is deferred to Phase 2 -- per spec Section 2.3b, this mirrors
  the upstream failure mode and can be added later.
- Style-editor: `claude-sonnet-4-7`, one re-draft on validator failure.

The Sonnet calls go through the same Anthropic API direct mechanism (or,
equivalently, via the Claude Agent SDK once the SDK adopts a Python entry
point; switching is a one-file change in `run.py`).

### Why API-direct over `claude` CLI subprocess

- Anthropic API direct avoids the CLI's interactive-shell assumptions
  (the CLI is built for human-in-the-loop, not for orchestrators).
- Model pinning is explicit at the call site (`model="claude-opus-4-7"`).
- Streaming / token counts are observable, which makes the cost model in
  `auto_blurb_process.md` Section 8 enforceable.
- The Anthropic SDK is a single `pip install anthropic` (not yet in
  `pipeline/requirements.txt`; added in the dispatch wiring task).

## SMTP env vars

The batched-cycle email send requires:

- `SMTP_HOST` (required; otherwise the orchestrator falls back to
  `editorial/blurbs/_inbox.md`)
- `SMTP_PORT` (default 587; use 465 for SMTPS)
- `SMTP_USER` (optional, depending on relay)
- `SMTP_PASS` (optional)
- `SMTP_FROM` (defaults to `SMTP_USER`)
- `BLURB_REVIEW_TO` (defaults to `jayzhaomurray@outlook.com` per
  EDR doc Section 5.1)

3-retry exponential backoff at 1m / 5m / 30m. After exhaustion, append
to `editorial/blurbs/_inbox.md`.

## File map

```
pipeline/blurbs/
  __init__.py
  artifact.py         CycleArtifact: front-matter YAML + body
  release_cycle.py    ReleaseCycle / SurfaceSlot / state machine
  registry.py         RELEASE_KEYS (Phase 1: cpi_monthly)
  validators.py       per-surface body rules + Mode A bans loaded from style.md
  factcheck.py        Mode B helpers (extract_numeric_tokens, verify_token)
  verify_claims.py    Mode A: fresh-context re-fetch + 5-reason taxonomy
  email.py            batched-cycle email; 3-retry SMTP; inbox fallback
  run.py              orchestrator CLI
  approve_cycle.py    bulk-approve helper (ready_for_user -> approved)
  README.md           this file
  test_*.py           pytest tests
```

```
editorial/blurbs/
  _inbox.md
  _cycles/<release-id>.json
  _global/homepage-abstract/<release-id>.md
  <section>/<unit-slug>/<release-id>.md
  <section>/<unit-slug>/<release-id>.log.md
editorial/verifications/blurbs/
  _shared/<release-id>.claims.json
  <section>/<unit-slug>/<release-id>.draft.json
research/blurb_context/<release-id>/_shared_cards.yaml
```

## Open questions blocking Phase 2

Documented in the dispatch report; chief one: how does the Astro side
consume the approved blurb? Phase 1's contract is that the approved
artifact lives on disk; the build picks it up via the existing
sections.json pipeline. The shape of the lookup (path-by-release-id vs
latest-approved-per-surface) is open.
