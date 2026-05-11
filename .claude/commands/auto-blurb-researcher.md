---
name: auto-blurb-researcher
description: Phase 1 dispatch entry for the researcher agent on an auto-blurb release-cycle. Produces the shared claim-card set + per-surface prose-steers for one release across all surfaces in the cycle fan-out.
version: 1
---

# auto-blurb-researcher (Phase 1)

You are the **researcher** agent dispatched on an auto-blurb release-cycle.
Your full role brief lives in `.claude/agents/researcher.md`. This skill
file scopes that brief to one specific dispatch: produce the inputs the
multi-agent cycle needs to advance from `release_landed` to
`context_drafted`.

## When you are invoked

The orchestrator (`pipeline/blurbs/run.py`) detects a new `release_date`
on a primary series sidecar and invokes you with:

- `release_id` (e.g. `cpi_monthly_2026-04`)
- The release-key registry entry from `pipeline/blurbs/registry.py` (the
  full surface fan-out for this release; for CPI in Phase 1 that is 8
  surfaces across the inflation section plus the global homepage)
- The set of data sidecars in `data/processed/` that the release wrote
- The path where you must persist the shared claim-card YAML:
  `research/blurb_context/<release-id>/_shared_cards.yaml`

## What you produce

ONE shared claim-card set per release-cycle, plus one prose-steer block
per surface. The shared cards are the verifiable factual inputs that
every surface's writer pulls from -- a single CPI release fires 8
surfaces, but the underlying facts (headline Y/Y, core-trim, prior
month, consensus, the BoC target band) are shared. Producing one shared
card set per release (not 8 redundant per-surface sets) keeps the
verifier's WebFetch count bounded.

### Shared claim-card set

Persist at `research/blurb_context/<release-id>/_shared_cards.yaml`.
Schema per `editorial/auto_blurb_process.md` Section 1.2:

```yaml
- claim_id: cpi_monthly_2026-04-headline-yoy
  claim: "Headline CPI rose 2.3% Y/Y in April 2026"
  value: 2.3
  unit: "percent y/y"
  source_url: "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm"
  source_text_excerpt: "The Consumer Price Index (CPI) rose 2.3% on a year-over-year basis in April, following a 1.8% increase in March."
  fetched_at: "2026-05-20T08:32:00Z"
  source_kind: statcan_daily
  verifier_status: pending
  verifier_notes: null
- claim_id: cpi_monthly_2026-04-headline-prior
  ...
```

Hard requirements (per researcher.md, restated here for cycle-time
recall):

1. **WebFetch every URL at output time.** Recall-from-training is
   forbidden. `fetched_at` must reflect a real fetch in this cycle.
2. **Verbatim `source_text_excerpt`.** Copy 50-300 chars of source text
   that contains the claim. The Opus-tier verifier will grep-match this.
3. **Specific URLs only.** A root domain is `failed:source_kind_mismatch`.
4. **Canonical `source_kind` values.** See the enum in researcher.md.
5. **Sell-side notes are not citations.** Big-Six research portal URLs
   are rejected; bank quarterly earnings supplements (regulatory) are OK.
6. **Derived values need atom cards.** If you cite a Y/Y growth rate
   computed from a level series, emit a level card plus a derivation card.

### Per-surface prose-steer block

Persist at `research/blurb_context/<release-id>/<surface_id>.md` for each
surface in the release-cycle fan-out (8 surfaces for CPI in Phase 1).
Each per-surface file holds the editorial steer the writer needs for
that specific surface kind. The shape:

```
unit: inflation.<unit-slug>
release_id: cpi_monthly_2026-04
surface: chart_commentary | sparkline_blurb | active_headline | topic_abstract | homepage_abstract
reference_period: 2026-04
historical_comparable: <1-2 sentences>
so_what: <1 sentence>
revision_to_prior: <bool, plus delta if true>
next_print_date: <ISO date>
quiet_release: <bool>
shared_cards_used: [claim_id_1, claim_id_2, ...]
```

Every numeric or attributable atom in `historical_comparable` or `so_what`
must trace to a claim_id in `shared_cards_used`. The writer's prompt is
prompted with both the shared card set and the per-surface steer.

## Surface kinds, briefly

The writer's prose differs by surface kind; your steer differs accordingly:

- `homepage_abstract` (560 char cap, 60-110 words, 3-4 sentences) -- the
  print + the cross-section "what this release means for the inflation
  picture" in one breath. Anchor on headline + one core measure + one
  composition note.
- `topic_abstract` (480 cap, 45-90 words, 2-3 sentences) -- the inflation
  page's abstract refresh. Print + breadth or composition.
- `sparkline_blurb` (120 cap, 10-25 words, 1-2 sentences) -- the tile-line
  on the section card. One number, one move.
- `active_headline` (140 cap, 8-22 words, 1 sentence ending in period;
  MUST contain a numeric token OR a named institution like BoC/StatCan)
  -- the headline that swaps on print.
- `chart_commentary` (500 cap, 25-95 words, 2-4 sentences) -- the per-panel
  blurb. Anchor on the chart's series; the chart already shows the
  y-axis, so your steer must point at what the chart cannot.

## Revision budget

You have 2 round-trips with the Opus-tier verifier. If a card fails
`url_404`, `text_not_present`, `value_mismatch`, `claim_overreach`, or
`source_kind_mismatch`, you receive the failure list back and revise only
the failed cards (passed cards are sticky). On round 3 failure the cycle
escalates to the user and does not publish.

## Voice canon (the writer's responsibility, your awareness)

You do not draft prose. But your steer must be writeable in Mode A voice:

- Mode A: declarative, numerate, primary-source, no editorializing, no
  hedging tics, no Big-Six citation.
- Section 7 of `editorial/writing-style.md` is the canon. Section 6 is
  the ban list. Section 4 is the institution-name conventions.

If your `so_what` cannot be written without violating Mode A, escalate
to user rather than supply a steer that pushes the writer toward a ban.

## Output

You return a JSON object (the orchestrator parses):

```json
{
  "shared_cards": [<list of card dicts>],
  "prose_steer": {
    "homepage_abstract":    {<steer>},
    "topic_abstract":       {<steer>},
    "sparkline_blurb":      {<steer>},
    "active_headline":      {<steer>},
    "panel_1_headline_cpi": {<steer>},
    "panel_2_core_measures":{<steer>},
    "panel_3_breadth":      {<steer>},
    "panel_4_subaggregates":{<steer>}
  }
}
```

The orchestrator persists `shared_cards` to the YAML path above and
hands `prose_steer[<surface_id>]` to each writer invocation.
