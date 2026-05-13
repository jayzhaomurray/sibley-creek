# /source-audit

Generates the per-section source-coverage audit pages from
`editorial/source_cards/registry.yaml`, the plates' `citations[]` arrays,
and the section pages' prose.

When the user runs `/source-audit` (no arg) or `/source-audit <section>`:

1. Run `node scripts/source_audit.mjs [<section>]` from the repo root.
2. Read the output. The script writes `editorial/source_cards/audit/<section>.html` for each section + `audit/index.html`.
3. Report in ~80 tokens which sections were generated and the per-section claim count.
4. Tell the user the file paths to open in a browser. They click the URL or open the file:// path.

## What the audit page shows

- The section's headline question and abstract.
- Each plate's title, blurb, and source line.
- Each tagged claim is yellow-highlighted with a [N] reference.
- Sidebar lists all claims with verbatim excerpts, source-card titles, vintage dates, and clickable links to the source (including deep anchors).
- Each plate (and the section abstract) has a "✎ Propose edit" button. The user clicks it, edits the text + writes a reason, and clicks "Copy edit-spec to clipboard." The clipboard holds a structured EDIT REQUEST the user pastes into chat.

## When user pastes an EDIT REQUEST

If the user pastes text starting with `EDIT REQUEST`, parse the structured spec:

```
EDIT REQUEST
section: gdp
surface: plate-1   (or "section-abstract")

proposed_title:
<new title>

proposed_body:
<new body>

reason:
<one or more lines>
```

Apply the edit:
1. Locate the surface in `src/pages/<section>.astro` (plate by id) or `src/data/sections.ts` (blurb.body for section-abstract).
2. Replace the title and/or body with the proposed text.
3. If the proposed body introduces NEW numeric / dated / countable claims, dispatch fact-checker per the redraft re-gate rule (`editorial/review_protocol.md`).
4. After applying + gate pass, `npm run build` to verify clean.
5. Suggest regenerating the audit page so the user sees the change reflected.

## When NOT to dispatch

- If the audit page is already up to date (script hasn't been re-run since last edit), don't regenerate without need.
- API-backed series and pipeline-driven claims aren't in the registry; they don't appear as "source-card" entries on the audit page. The script labels them `pipeline:<key>`.

## Voice constraints

- Cap report at ~80 tokens.
- Don't paste the audit HTML; just confirm generation + paths.
