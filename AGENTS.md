# AGENTS.md — Sibley Creek (macro-research-department)

You are operating inside Sibley Creek, a Canadian macroeconomic
publication. The canonical instruction file for this project is
`CLAUDE.md` at the repo root. Read it now before doing anything else —
it defines operating mode, file-location conventions, the three-gate
review protocol, and the things never to do.

## Canonical files to respect

- `CLAUDE.md` — root project instructions: operating mode, three-gate
  review, what NOT to do. Authoritative.
- `editorial/dashboard_purpose.md` — what the publication exists to be.
- `editorial/writing-style.md` — voice and style canon (banned vocab,
  chart-title canon with terminal period, take-mechanism-land blurb
  structure, length budgets, acronym test).
- `editorial/review_protocol.md` — the three-gate review protocol
  (fact-check, style polish, surface fit). Mandatory before ship.
- `design/design-system.md` — Vignelli visual canon.
- `design/canon_reference_panel.md` — Tier-3 chart canon.
- `design/sparkline-canon.md` — Tier-1 sparkline canon + splash
  composition restraint.

## Operating discipline

- **File locations.** `work/` is Jay-facing artifacts only (PDF, HTML,
  Excel, Word). `claude-ref/` is working memory (markdown dispatch
  output, research notes, methodology). `editorial/` is the prose
  canon. Default ambiguous cases to `claude-ref/`. Never put markdown
  working docs in `work/`.
- **Respect retirement markers.** Code comments like "kept on disk",
  "retired", "do not revive", "superseded by X" are editorial
  decisions. Do not resurrect retired components. Do not rebuild a
  page from scratch because you didn't find the canonical version —
  grep `src/pages/` for parallel work first.
- **Before drafting a new page in `src/pages/`**, grep for the slug,
  the section name, and any obvious alias. The canonical version
  usually exists.

## Audit handoff with Claude

After substantial work, hand off to Claude for audit. Substantial =
any of:

- new page in `src/pages/`
- new chart component
- new pipeline module under `pipeline/`
- new deep-dive draft under `editorial/`
- model or analytical code in `pipeline/`
- research memo under `claude-ref/research/`
- anything touching reader-facing prose

**For a NEW artifact** (file that didn't exist before this turn): at
the end of the turn, prompt the user:

    Run Claude audit on this output? [Y/n]

If yes, execute:

    npm run audit -- --by codex --target <path> --task "<task description>"

before ending the turn.

**For INCREMENTAL edits to existing substantial files**: do NOT prompt
after each edit. When the user signals session wrap ("done", "let's
commit", "ship it", "wrap up", etc.) OR when staging for commit,
prompt:

    Run Claude audit-diff before commit? [Y/n]

If yes, execute:

    npm run audit-diff -- --by codex --task "<task description>"

The auditor reads `git diff` rather than the whole file.

**For research and strategy memos**: suggest the user run a
parallel-pass + referee pattern instead of lead-and-audit:

    npm run cross-audit -- "<task>"

Both models do independent passes from scratch; the synthesis lands
under `claude-ref/cross_audit/<task-slug>/`.

## Enforcement

A pre-push git hook blocks pushes that modify substantial files
without a matching `editorial/audit_findings/` entry from Claude.
Override is `git push --no-verify` and should be rare. The list of
substantial paths is at `.audit-config.json`.

## CLI conventions

- Claude non-interactive: `claude --print "<prompt>"` (used in
  `pipeline/blurbs/run.py` and the boc-tracker subprocess pattern
  cited in `CLAUDE.md`).
- Codex non-interactive: `codex exec "<prompt>"`.

The `npm run audit*` scripts own the exact invocation form; you do
not need to assemble the prompts by hand.
