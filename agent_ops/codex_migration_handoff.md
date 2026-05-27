# Codex Migration Handoff

Last updated: 2026-05-27.

## Current Goal

Replace the old Claude-led operating workflow with a Codex-led workflow that is easier for Jay to invoke and remember.

The new interface should be one personal Codex skill:

```text
$task
```

Jay should not need to remember separate Claude agents, slash commands, risk levels, or dispatch prompts.

## What Has Been Done

- Reconstructed the personal Codex skill at `C:\Users\jayzh\.codex\skills\task` after restart showed it was missing.
- Validated the skill with `py -3 C:\Users\jayzh\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\jayzh\.codex\skills\task`; validation passed.
- Added skill files:
  - `C:\Users\jayzh\.codex\skills\task\SKILL.md`
  - `C:\Users\jayzh\.codex\skills\task\references\auto_blurb_protocol.md`
  - `C:\Users\jayzh\.codex\skills\task\references\chart_ops.md`
  - `C:\Users\jayzh\.codex\skills\task\references\command_map.md`
  - `C:\Users\jayzh\.codex\skills\task\references\parallel_work.md`
  - `C:\Users\jayzh\.codex\skills\task\references\repo_conventions.md`
  - `C:\Users\jayzh\.codex\skills\task\references\risk_rubric.md`
  - `C:\Users\jayzh\.codex\skills\task\references\source_audit_and_pending.md`
  - `C:\Users\jayzh\.codex\skills\task\references\workflows.md`
- Audited the old Claude surface area and folded the missing detailed mechanics into `$task` references:
  - auto-blurb claim cards, verifier failure taxonomy, and three-round re-gate loop;
  - chart fix/move/promote/demote/pin mechanics;
  - source-audit generation and pasted `EDIT REQUEST` handling;
  - pending-action scan and wrap-up checklist;
  - fleet-style parallel work via Codex subagents only when Jay explicitly asks for delegation.
- Previous session reported that `claude.exe` is installed and supports non-interactive use with `claude -p --agent <agent>`; reconfirm before invoking Claude from Codex.
- Confirmed old Claude workflow assets exist under:
  - `.claude/agents/`
  - `.claude/commands/`

## Strategic Decision

Do not port Claude workflow 1-for-1.

The old Claude system had too many agents and slash commands. Jay was not consistently remembering to use them. The new system should consolidate workflows under `$task`.

## New Operating Model

Codex is the default coordinator, implementer, reviewer, and referee.

Claude is optional, because Jay is reducing Claude to the cheapest plan. Claude should be used only when a bounded specialist review is worth the cost.

Default fallback order:

1. Codex handles the task directly.
2. Codex uses Codex-native review/subagents if available and useful.
3. Claude is called only as an optional specialist.
4. If Claude is skipped for high-risk work, the final report should say what review replaced it.

## Consolidated Function Map

Collapse the old Claude agent roster into five functions:

| New Function | Old Claude Agents Folded In | Default Owner |
| --- | --- | --- |
| Research | `researcher`, part of `editorial-director` | Codex first, Claude optional |
| Editorial review | `fact-checker`, `style-editor`, `editorial-director` | Codex workflow, Claude optional |
| Writing | `writer`, `style-editor` | Codex first, Claude optional |
| Visual / chart | `art-director`, `chart-builder`, part of `frontend-designer` | Codex first, Claude optional |
| Engineering | `backend-engineer`, `frontend-designer` | Codex |

## Consolidated Command Map

Do not create separate skills for each old slash command. `$task` should recognize natural language modes:

| `$task` Mode | Old Claude Commands Covered |
| --- | --- |
| `$task sources ...` | `check-sources`, `source-audit`, source-card follow-up |
| `$task chart ...` | `fix-chart`, `move-chart`, `promote-chart`, `demote-chart`, `pin-chart` |
| `$task blurbs ...` | `refresh-blurbs`, all `auto-blurb-*` phase commands |
| `$task review ...` | fact-check, style, and surface-fit gates |
| `$task wrap up` / `$task pending ...` | `pending`, `wrap-up` |
| `$task research ...` | R2 research-cell workflow or R3 methodology workflow |
| `$task fix/build/code ...` | Codex engineering workflow |

## Durable Rules To Preserve

- Reader-facing prose must pass the editorial gate:
  1. fact-check;
  2. style;
  3. surface fit.
- Any new claim introduced during redraft re-enters fact-check.
- Big-Six bank desks are context or Mode 3 analysis citations, not fact authority.
- Primary sources are preferred.
- Source-card and citation discipline matter.
- Chart work follows the Vignelli design canon.
- Frontend/chart work should run `npm run build` and visual checks where practical.
- Quant, causal, predictive, and subscriber-signal work is R3 and requires explicit spec plus independent review.
- Do not overwrite prior versions of research results; create second versions when correcting analysis.
- Jay should receive one synthesis, not raw model sprawl.

## Next Step After Restart

Use `$task` as the single front door. Avoid building more repo-level operating docs unless needed.

Recommended first post-restart prompt:

```text
$task continue the Codex migration from agent_ops/codex_migration_handoff.md
```

If `$task` is not recognized after restart, ask Codex to read:

```text
C:\Users\jayzh\.codex\skills\task\SKILL.md
agent_ops/codex_migration_handoff.md
```

Then continue by updating the personal skill.
