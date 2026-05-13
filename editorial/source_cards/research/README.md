# Research deep-dive citations (sidecar pattern)

Each `editorial/published/<slug>.md` deep dive gets paired with a
sidecar YAML in this directory at `<slug>.yaml`. The sidecar carries
the citation tags for every numeric / dated / countable claim in the
deep dive's body.

Why a sidecar (not inline markdown markers): keeps the prose clean for
human reading, makes the citation set scannable as data, and matches
the per-page convention the rest of the site uses (`citations[]` on
section plates, `abstractCitations[]` on section blurbs).

## Schema

```yaml
slug: <slug>             # matches editorial/published/<slug>.md
title: <human title>     # optional; mirrors the article's H1
citations:
  - phrase: "<verbatim substring from the deep-dive body>"
    source: "card:<id>" | "pipeline:<provider>:<key>" | "derived" | "other:<note>"
    note: "<optional context>"
  - ...
```

## Coverage gate

`scripts/check_citation_coverage.mjs` reads each deep dive + its sidecar.
For each citable token in the body (percentages, dollar amounts, bps,
pp, dates, year markers, "Nth straight / first since X" enumerations),
the gate checks whether at least one citation's `phrase` covers it.

A deep dive enters STRICT mode the moment any sidecar exists. A dive
with no sidecar stays in warn-only "needs-tagging" mode.

## Audit page

`scripts/source_audit.mjs` writes one HTML audit per deep dive at
`editorial/source_cards/audit/research/<slug>.html`. Same UI shape as
the section-page audits: tagged claims highlighted in the body,
sidebar listing each claim with source + URL + excerpt.
