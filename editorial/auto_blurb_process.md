# Auto-blurb editorial process (v2: multi-agent)

Owner: editorial-director.
Date: 2026-05-11.
Status: design canon. Supersedes `research/auto_blurb_pipeline_design.md`
(researcher v1, single-LLM-centric). v1 will be moved to
`research/auto_blurb_pipeline_design_v1_archived.md` as reference.

Anchors:
- `editorial/dashboard_purpose.md` Sections 1 (mission), 5 (deep-dive
  cross-references), 7 (voice principles), 9 (six-month success criteria,
  including criterion 3: Mode 2 auto-blurb operating on at least three
  sections by November 2026).
- `editorial/writing-style.md` Section 7 (Mode A / Mode 2 voice canon)
  and Section 8 (consensus + surprise prose).
- `.claude/agents/*.md` (the four-agent fleet this process orchestrates:
  researcher, writer, fact-checker, style-editor; plus backend-engineer
  for the pipeline build).
- `data/site/sections.json` (current emitted state per section: print,
  delta, asOfISO, primarySeries, source, sourceUrl, units, frequency)
  and `data/processed/<series>.meta.json` (per-series sidecar with
  `release_date`, `source_url`, `source_id`, `reference_period_end`).

Why a multi-agent rewrite. The v1 design treated the blurb as a
single-LLM-plus-mechanical-validators job: one prompt, one return, one
validator pass, file on disk. That collapses four distinct editorial
functions -- editorial steer, drafting, fact-check, voice polish --
into a single prompt and pushes the burden of all four onto the user's
review step. The user explicitly rejected that model: "we have a team
of agents; i created multiple for this reason. someone has to design
the process. going to be a mix of researching, writing, fact checking,
editing." This document is that process. Each agent in the fleet has a
brief for its role in the cycle, a defined input, a defined output,
and a defined pass/fail gate.

Terms (carried forward from v1):
- "Blurb" = the 2-to-4-sentence Mode 2 interpretation paragraph
  attached to a single chartbook unit on a section page.
- "Release" = a single upstream publication event (LFS for May 2026
  released on first Friday June 2026; the June 10 BoC rate decision).
- "Unit" = one chartbook unit = one chart plate plus its blurb.
- "Cycle" = one end-to-end run for one (release, unit) pair, from
  release-landed to publish.
- "Release-id" = the human-readable identifier for a release-cycle,
  e.g. `cpi_monthly_2026-04`, `lfs_monthly_2026-05`,
  `boc_decision_2026-06-10`.
- "Inbox" = the user's review queue, surfaced as both an email to
  jayzhaomurray@outlook.com and a file at
  `editorial/blurbs/_inbox.md`.

---

## 1. State machine

Every blurb-cycle is a finite-state object. State transitions are
gated by the named agent's pass. Failed gates either retry (with a
budgeted retry count) or escalate to the user.

States, in order:

1. `pending_release` -- the release is calendared but the upstream
   publisher has not yet posted a new vintage. Owner: backend-engineer
   (pipeline scheduler).
2. `release_landed` -- the pipeline has detected a new `release_date`
   on the unit's primary series sidecar (content-hash trigger of
   v1 Section 1; carried forward) and written the new CSV + meta.json.
   Cycle artifact created on disk; owner handoff to researcher.
3. `context_drafted` -- researcher has produced a release-context note
   for every unit in the release's fan-out. The note is the editorial
   steer the writer needs: what was surprising, what the so-what is,
   what historical comparable matters. Owner handoff to writer.
4. `writer_drafted` -- writer has produced the Mode 2 blurb body
   (2-4 sentences) for each unit, scaffolded by the context note plus
   the raw release data plus a description of the chart visual. Owner
   handoff to fact-checker.
5. `fact_checked` -- fact-checker has verified every numeric token,
   every named institution, every cited release date, and the absence
   of TK leakage against `data/processed/` and the primary source URLs
   in `data/site/sections.json`. Owner handoff to style-editor.
6. `style_polished` -- style-editor has polished voice against
   `editorial/writing-style.md` Section 7 Mode A. Owner handoff to
   user.
7. `user_review` -- email lands in user inbox; draft file is in
   `editorial/blurbs/<section>/<unit-slug>/<release-id>.md` with
   `status: ready_for_user`. User opens, reads, rewrites if desired,
   sets `status: approved`. Owner: user.
8. `approved` -- user-approved. The build picks it up on the next
   render pass.
9. `published` -- the build has rendered the approved blurb into the
   live site. Terminal state.

Each transition has a gate, an owner, a fail policy, and an escalation.

| From | To | Gate | Owner | Fails on | On fail |
|---|---|---|---|---|---|
| `pending_release` | `release_landed` | New `release_date` on primary series sidecar | backend-engineer (scheduler) | Calendar window passes with no fetched change | Stale-alert email after N polls (per release-key cadence rule in `pipeline/calendar/releases.py`); user investigates |
| `release_landed` | `context_drafted` | Researcher returns a context note (one entry per unit) | researcher | Researcher declares "quiet release" for all units in fan-out | Cycle short-circuits to the "quiet release" flow; see Section 4.1 |
| `context_drafted` | `writer_drafted` | Writer returns a 2-4 sentence Mode 2 body that passes voice-validator pre-checks (word count 25-95, sentence count 2-4, ASCII-only, no banned constructions in `writing-style.md` Section 6) | writer | Writer flags an unresolved TK or returns prose that fails mechanical pre-checks | Up to two writer re-runs; on third failure escalate to user |
| `writer_drafted` | `fact_checked` | Fact-checker verifies all numeric tokens within rounding tolerance, all dates against the release calendar, no TK leakage, no Big-Six citation, no banned-source phrasing | fact-checker | Numeric mismatch, TK in body, banned-source phrasing, source URL 404 | Up to two re-drafts (return to writer); on third failure escalate to user with the trace |
| `fact_checked` | `style_polished` | Style-editor returns a polished version (Mode A voice) or asserts the draft already meets the bar | style-editor | Hedging tic, banned cliche, jargon-as-armor, register slip toward Mode B | One re-polish if first pass is rejected by self-check; on second failure escalate to user with diff |
| `style_polished` | `user_review` | Email to jayzhaomurray@outlook.com sent; file written to disk with `status: ready_for_user` | pipeline orchestrator | SMTP failure | Retry email 3x at exponential backoff (1m, 5m, 30m); after that, fall back to writing only `editorial/blurbs/_inbox.md` and surface a desktop-notification path |
| `user_review` | `approved` | User edits file front-matter from `status: ready_for_user` to `status: approved` and commits | user | User sets `status: rejected` (rare) or leaves draft idle | If idle past one full release-cycle for that series, the draft is auto-retired (`status: stale`); the next cycle's draft becomes the live blurb. Per v1 Section 8.6 |
| `approved` | `published` | The Astro build picks the file up on next push to `main` or on the hourly rebuild | backend-engineer (build) | Build error | Loud failure; the prior approved blurb continues to render |

Two cross-cutting state fields, present on every cycle artifact:

- `last_state` -- where we are now.
- `state_history` -- append-only list of `(state, timestamp, agent_or_user, note)` tuples. This is the audit trail (Section 6).

---

## 2. Per-agent briefs

Each brief states: trigger, inputs, deliverable, pass/fail criteria,
escalation. These briefs are summary statements of how each agent
plays in the auto-blurb cycle; the agent's full role brief lives in
`.claude/agents/<name>.md` and stays canon.

### 2.1 researcher -- release-context note

**Trigger.** Pipeline transitions to `release_landed`. Orchestrator
invokes researcher with the release-id and the list of units that
depend on this release.

**Inputs.**
- `data/processed/<series>.csv` and `<series>.meta.json` for every
  series the unit's chart shows (primary plus secondary lines).
- `data/site/sections.json` for the unit's current render state
  (latest print, delta, source URL).
- The prior approved blurb for this unit (most recent `status:
  approved` file in `editorial/blurbs/<section>/<unit-slug>/`) for
  continuity context.
- The consensus comparator (where available; see `research/
  wave2_consensus_sourcing.md` and writing-style.md Section 8) or the
  BoC MPR central projection (fallback).
- The release calendar's `next print` date for this release-key.

**Deliverable.** A structured release-context note per unit, written
to `research/blurb_context/<release-id>/<unit-slug>.md`. Each note
contains:

```
unit: <section>.<unit-slug>             e.g. inflation_basics.panel-1
release_id: <release-id>                e.g. cpi_monthly_2026-04
reference_period: <YYYY-MM or YYYY-Qn>
print_value: <numeric, native units>
prior_value: <numeric>
consensus_value: <numeric or null>
consensus_source: aggregated_forecaster_median | boc_mpr | none
surprise_value: <numeric or null, native units>
historical_comparable: <free text, 1-2 sentences>
   e.g. "First month Y/Y headline has been within the 1-3% BoC
        control band since January 2023."
so_what: <free text, 1 sentence>
   The single observation the writer should anchor the third
   sentence on. May be "none for this release" if the print is
   quiet.
revision_to_prior: <bool, plus delta if true>
next_print_date: <ISO date>
quiet_release: <bool>
   Set true only if the print is genuinely uneventful (no
   meaningful comparator move, no structural observation). Quiet
   releases still produce a 2-sentence blurb; see Section 4.1.
```

**Pass criteria.** A context note exists for every unit in the
release's fan-out. Numeric fields cross-check against
`data/processed/`. The so-what sentence is a factual claim
(distinguishable from interpretation; the writer can ground prose on
it without inventing).

**Fail / escalation.** If the researcher cannot produce a context note
for a unit (e.g. underlying data is contradictory, or the
historical-comparable claim is uncertain), the researcher returns the
unit with `quiet_release: true` and `so_what: "no defensible
editorial steer for this release"`. The cycle continues with a
shorter blurb; the user sees a flag in the email.

**What researcher does NOT do.** The researcher does not draft the
blurb prose. The researcher does not stamp the consensus as a fact;
they stamp it as a derived numerical input per writing-style.md
Section 8. The researcher does not cite Big-Six in the so-what
sentence.

### 2.2 writer -- Mode 2 draft

**Trigger.** Pipeline transitions to `context_drafted`. Orchestrator
invokes writer with the release-id and the list of units.

**Inputs.**
- The researcher's release-context note for each unit
  (`research/blurb_context/<release-id>/<unit-slug>.md`).
- The raw release data (the same `<series>.csv` files), passed as
  a structured 24-month window per series.
- A textual description of the chart visual the blurb will sit
  beside, sourced from `design/chartbook-template.md` per-unit
  manifest (so the writer knows what the chart already shows and
  does not double-recite the y-axis).
- The voice canon: the verbatim contents of
  `editorial/writing-style.md` Section 7 Mode A (the blurb-specific
  rules), Section 6 (banned constructions), Section 8 (consensus
  prose), Section 2 (number, percentage, date conventions), Section
  4 (institution names).

**Deliverable.** A 2-to-4-sentence Mode 2 blurb body for each unit,
written to the cycle artifact at
`editorial/blurbs/<section>/<unit-slug>/<release-id>.md` with
`status: writer_drafted` and the body in the file's content area.

**Pass criteria.** The body meets the mechanical pre-checks:
- 25 to 95 words.
- 2 to 4 sentences (counted by terminal punctuation).
- ASCII-only.
- No banned constructions (substring scan against the
  writing-style.md Section 6 list).
- No Big-Six bank name attribution.
- Numbers consistent with the researcher's context note (writer
  cannot invent a value the context note did not supply).
- No TK or `<placeholder>` markers.

**Fail / escalation.** If the writer cannot draft without inventing
a fact, the writer returns the cycle to the researcher with a
"please verify or supply" note (this is a within-cycle re-route, not
an escalation; it does not consume the writer's retry budget). If
the mechanical pre-checks fail, the writer self-corrects (re-run);
after two consecutive mechanical-pre-check failures on the same
unit, escalate to the user with the failing drafts attached.

**What writer does NOT do.** The writer does not check numbers
against the source data (fact-checker's job). The writer does not
polish voice (style-editor's job; the writer drafts to register but
does not perform the polish pass). The writer does not select which
comparator (consensus vs MPR) to lean on -- the context note tells
them which is available.

### 2.3 fact-checker -- numeric and source verification

**Trigger.** Pipeline transitions to `writer_drafted`. Orchestrator
invokes fact-checker with the cycle artifact.

**Inputs.**
- The writer's draft body in the cycle artifact.
- The cycle artifact's structured front-matter (consensus value,
  print value, prior value, surprise value).
- `data/processed/<series>.csv` and `<series>.meta.json` for every
  series the unit shows.
- `data/site/sections.json` for the primary-source URL.

**Deliverable.** A verification verdict written to
`editorial/verifications/blurbs/<section>/<unit-slug>/<release-id>.json`
plus a state transition on the cycle artifact. The verdict file is
the mechanical trace per v1 Section 5: a list of
`(numeric_token, source_field, source_value, match_status)` tuples
plus the per-claim verdict (verified / unsupported / contradicted /
uncertain) per the fact-checker agent brief in
`.claude/agents/fact-checker.md`.

**Pass criteria.** Every numeric token in the body resolves to a
source value within rounding tolerance. Every cited date matches the
release calendar. Every institution name uses the convention in
writing-style.md Section 4 (BoC not BOC; StatCan not Stats Can). No
TK leakage. No Big-Six citation in prose. The primary-source URL in
`data/site/sections.json` for this unit's print returns 200 on a
HEAD request.

**Fail / escalation.** Any mismatch fails the gate. The fact-checker
returns the cycle to the writer with the specific numbers /
phrasings that failed and the source values they should be. After
two failed re-drafts, escalate to the user with the trace attached
(the user gets the email, opens the draft, and sees the failed
verifications inline).

**What fact-checker does NOT do.** The fact-checker does not polish
voice. The fact-checker does not verify the researcher's so-what
sentence (that's a researcher-side claim; if the writer used it,
the writer is responsible for not extending it beyond what the
researcher wrote, and fact-checker may flag suspected
extension as `uncertain`). The fact-checker does not run after the
user rewrites the body -- the user's edit ends the verification
chain. Soft-warning post-edit verification (per v1 Section 5
"two-cycle exception") is a v3 add and not in scope for Phase 1.

### 2.4 style-editor -- voice polish

**Trigger.** Pipeline transitions to `fact_checked`. Orchestrator
invokes style-editor with the cycle artifact.

**Inputs.**
- The fact-checked draft body.
- `editorial/writing-style.md` Section 7 Mode A, Section 6, Section
  9 (working notes for style-editor).

**Deliverable.** A polished body written back into the cycle
artifact with `status: style_polished`. The polish is voice and
structure only; the fact-checker has already verified the numbers
and style-editor must not change them. Per the style-editor agent
brief, "where prose conflicts with a fact, escalate rather than
rewrite the fact."

**Pass criteria.** The polished body:
- Leads with the print (variable, value, period).
- Carries the comparator in sentence two (consensus, prior, or
  MPR fallback per writing-style.md Section 8).
- Optional sentence three carries the one structural observation
  the chart cannot make.
- Optional sentence four is the next-print pointer.
- No hedging tics (writing-style.md Section 6).
- No FT-coded jargon-as-armor (writing-style.md Section 6).
- No Big-Six citation phrasing ("RBC expected", "the Street was
  looking for", etc.).
- Canadian spelling.
- Em-dash / en-dash / hyphen per writing-style.md Section 3.

**Fail / escalation.** If the draft does not meet voice bar even
after the polish pass (e.g. the writer's structure was so far off
register that a polish-pass cannot fix without re-writing), the
style-editor returns the cycle to the writer with a one-paragraph
note on what register was missed. After one failed re-draft (i.e.
two total writer passes), escalate to the user with both versions
attached.

**What style-editor does NOT do.** The style-editor does not change
facts. The style-editor does not re-run the fact-checker pass after
polishing. The style-editor does not have a verdict on whether the
blurb is right -- only whether the prose meets the voice bar.

---

## 3. Orchestration

### 3.1 How a cycle kicks off

Per user direction: scheduled trigger. The pipeline's scheduler runs
a calendar-driven fetch (see `pipeline/calendar/releases.py` per v1
Section 1) and on every fetch compares the returned `release_date`
against the existing sidecar. A change in `release_date` is the
content-hash signal that fires the cycle.

The trigger writes a cycle-init record at
`editorial/blurbs/_cycles/<release-id>.json` containing:
- `release_id`
- `release_key` (e.g. `cpi_monthly`, `lfs_monthly`,
  `boc_rate_decision`)
- `reference_period`
- `release_date`
- `fan_out` -- the list of `(section, unit-slug)` tuples whose
  blurbs depend on this release
- `created_at`
- `last_state: release_landed`
- `state_history: [(release_landed, <ts>, scheduler, "fetch
  detected new release_date")]`

The orchestrator (a single Python module, `pipeline/blurbs/
orchestrator.py`) then dispatches each agent in turn per the state
machine.

### 3.2 Filesystem layout

```
editorial/
  blurbs/
    _inbox.md                          # user's review queue, list of
                                       #   cycles in user_review state
    _cycles/
      <release-id>.json                # cycle-init record + state log
    <section>/                         # e.g. inflation
      <unit-slug>/                     # e.g. panel-1-headline-cpi
        <release-id>.md                # the cycle artifact (front-
                                       #   matter + body); status
                                       #   evolves through states
        <release-id>.log.md            # append-only audit trail per
                                       #   cycle (Section 6)
  verifications/
    blurbs/
      <section>/
        <unit-slug>/
          <release-id>.json            # fact-checker mechanical trace
research/
  blurb_context/
    <release-id>/
      <unit-slug>.md                   # researcher's per-unit context
                                       #   note
```

The cycle artifact's front-matter schema, expanded from v1 Section 3:

```
---
release_id: cpi_monthly_2026-04
section: inflation
unit: inflation_basics.panel-1
unit_slug: panel-1-headline-cpi
release_key: cpi_monthly
reference_period: 2026-04
release_date: 2026-05-14
created_at: 2026-05-14T08:32:15Z
last_state: ready_for_user
state_history:
  - [release_landed,    2026-05-14T08:30:00Z, scheduler]
  - [context_drafted,   2026-05-14T08:35:00Z, researcher]
  - [writer_drafted,    2026-05-14T08:38:00Z, writer]
  - [fact_checked,      2026-05-14T08:40:00Z, fact-checker]
  - [style_polished,    2026-05-14T08:42:00Z, style-editor]
  - [ready_for_user,    2026-05-14T08:42:00Z, orchestrator]
researcher_context_path: research/blurb_context/cpi_monthly_2026-04/panel-1-headline-cpi.md
fact_check_path: editorial/verifications/blurbs/inflation/panel-1-headline-cpi/cpi_monthly_2026-04.json
fact_check_status: passed
voice_validation: passed
consensus_source: aggregated_forecaster_median
consensus_value: 2.2
print_value: 2.3
prior_value: 1.8
surprise_units: pp
surprise_value: 0.1
status: ready_for_user
quiet_release: false
flags: []
model_writer: <pinned-model-id>
model_fact_checker: <pinned-model-id>
model_style_editor: <pinned-model-id>
---

[blurb body lives here, 2-4 sentences, plain prose]
```

### 3.3 TKs and questions

TKs and open questions get logged in two places:

1. Inline in the cycle artifact under a `flags` list in the
   front-matter, machine-readable for the email-summary builder.
   Each flag has `agent`, `severity` (info / warn / block), and
   `note`.

2. Append-only in the cycle's audit log at
   `editorial/blurbs/<section>/<unit-slug>/<release-id>.log.md`
   (Section 6 spec), one Markdown line per event:
   `2026-05-14T08:38:12Z writer flag warn "consensus_source was
   none; could not write surprise line"`.

A TK in the body itself (writer leaves a `TK` token because they
need researcher to verify a number) is treated as a block-severity
flag and routes the cycle back to researcher before the
writer_drafted state is finalized. TK leakage to fact-checker is a
hard fail; the cycle returns to writer with the TK line called out.

---

## 4. Failure modes and retries

### 4.1 Quiet release

If the researcher's context note says `quiet_release: true` for a
unit, the cycle proceeds with the standard prompt scaffolding but
the writer's prompt template is the short variant (2 sentences:
print + prior comparator only; no surprise line, no structural
observation). The fact-checker and style-editor passes still run.
The user-review email subject line includes `[quiet]` so the user
can triage faster.

If every unit in the fan-out is quiet, the entire release-cycle
batches into a single email rather than per-unit emails.

If the researcher cannot produce a context note at all (a structural
researcher failure, e.g. the underlying data has not yet propagated
to `data/processed/` because the pipeline lagged), the cycle pauses
at `release_landed` and the orchestrator alerts the user via email
with `subject: Auto-blurb pipeline paused: researcher could not
produce context note for <release-id>`.

### 4.2 Writer hits an unresolved TK

The writer cannot find the prior value, the consensus value, or some
other number the researcher should have supplied in the context
note. The writer flags the cycle back to researcher with a
specific question ("the context note says
`historical_comparable: first month within control band since
January 2023` -- can you supply the specific historical Y/Y for
January 2023 so I can verify the comparable claim is accurate?").
This is not an escalation; it is a within-cycle re-route. The
researcher returns the additional fact or amends the so-what
sentence. Then the writer re-drafts.

If the same TK round-trips three times (researcher cannot resolve;
writer cannot draft without it), escalate to the user with the
full TK trail.

### 4.3 Fact-checker rejects

Three classes:

- **Numeric mismatch.** Writer rounded wrong, transposed digits,
  invented a value. Cycle returns to writer with the specific
  token, the source value, and the expected correction. Budget:
  two re-drafts. On third failure, escalate to user.
- **TK leakage.** Writer left a `TK` or `<placeholder>` in the
  body. Cycle returns to writer; this should be impossible past
  mechanical pre-checks, so a TK-leakage failure at fact-check
  also triggers a pipeline-hygiene alert to backend-engineer to
  tighten the pre-check.
- **Source URL 404.** The primary-source URL in
  `data/site/sections.json` is dead. Fact-checker logs the dead
  URL, the cycle continues with the verification noted as
  `passed_with_caveat`, and the orchestrator emits a separate
  alert to the user: `Subject: Source URL stale: <section>
  <unit-slug>`. The blurb does not get blocked on a stale
  citation; the user gets a separate ping to chase the source
  fix. (Rationale: a dead source URL is a data-side hygiene
  failure, not an editorial-pipeline failure; blocking blurb
  publish on it would create an indirect dependency that punishes
  the wrong agent.)

### 4.4 Style-editor rejects

Two classes:

- **Polishable.** The writer's body has a hedging tic or two, a
  cliche, an institution-name slip. Style-editor polishes
  in-place; the body that emerges is acceptable. Pass.
- **Not polishable.** The writer's body is structurally off
  register -- magazine framing, opinion creep ("we think the BoC
  will cut"), Mode 3 register slip. Style-editor returns the
  cycle to writer with a one-paragraph note. Budget: one
  re-draft. On second failure, escalate to user.

### 4.5 Source URL 404 during fact-check

Already covered in 4.3. To repeat for clarity: a 404 does not block
the blurb publish; the cycle is annotated `passed_with_caveat` and
the user gets a separate source-hygiene email.

### 4.6 Escalation surface

Every escalation lands in the user's email inbox with a subject line
that names the failing stage and a body that links to the cycle
artifact, the failed drafts, and the agents' trace. Section 5 spec
covers the email shape.

---

## 5. User-review surface

### 5.1 Email shape

User confirmed: email to jayzhaomurray@outlook.com.

**Subject line.**

```
Auto-blurb ready for review: <Section> <Indicator> <ReferencePeriod>
```

Examples:
- `Auto-blurb ready for review: Inflation Headline CPI Apr 2026`
- `Auto-blurb ready for review: Labour LFS May 2026 [quiet]`
- `Auto-blurb ready for review: Policy BoC rate decision 2026-06-10`

Escalation subjects:
- `Auto-blurb pipeline paused: <reason> <release-id>`
- `Auto-blurb escalation: <stage> failed for <release-id>`
- `Source URL stale: <section> <unit-slug>`

The `[quiet]` tag and batch tags (e.g. `[batch: 6 units]`) prefix
the section name when applicable.

**Body content.**

Plain-text email with the polished draft inline plus a short
metadata block plus a path link to the cycle artifact on disk.
Inline because the user's review is reading + rewriting prose -- a
preview in the email lets the user triage on phone, even if the
rewrite happens later in VS Code. Example:

```
Section:   Inflation
Indicator: Headline CPI, y/y
Period:    April 2026
Print:     2.3% (vs 1.8% prior; consensus 2.2%; surprise +0.1pp)
Source:    Statistics Canada Table 18-10-0006-01

Draft (2-4 sentences):
-----
Headline CPI rose 2.3% Y/Y in April, a 0.1pp acceleration from
March and 0.1pp above consensus of 2.2%. Core-trim held at 2.7% and
core-median ticked down to 2.8%. Shelter contributed 1.1pp to the
headline, with mortgage-interest cost continuing its mechanical
fade. The next print is May 20.
-----

Cycle artifact:
  editorial/blurbs/inflation/panel-1-headline-cpi/cpi_monthly_2026-04.md

Audit trail:
  editorial/blurbs/inflation/panel-1-headline-cpi/cpi_monthly_2026-04.log.md

Flags: none

To approve as-is:
  edit the artifact, set status: ready_for_user -> status: approved,
  commit on main.

To rewrite:
  edit the body in the artifact, then set status: approved, commit.

To reject:
  set status: rejected, optionally add a one-line reason in the
  flags list. The pipeline will not retry on reject; the prior
  approved blurb continues to render.
```

**Reply-as-approval.** Out of scope for Phase 1. Mechanical approval
is via VS Code edit + commit. Rationale: parsing email replies for
status changes adds a SMTP-inbound dependency, and the user already
lives in VS Code for the rest of the codebase. Reply-as-approval is
a v3 nice-to-have if the user reports the commit step is friction.

### 5.2 The user's mechanical workflow

1. Phone or laptop: email arrives, user reads the inline draft.
2. Decide: approve-as-is, rewrite, or reject.
3. Open VS Code (laptop), navigate to the cycle artifact at the
   path in the email.
4. Edit the body if rewriting. The fact-checker has verified the
   numbers; the user's edit is voice and emphasis.
5. Change `status: ready_for_user` to `status: approved` (or
   `status: rejected`).
6. Save. Commit. Push to main.
7. The Astro build picks up the approved blurb on the next push or
   hourly rebuild and renders. The cycle moves to `published`.

**Inbox digest fallback.** If the email fails (SMTP retries
exhausted), the orchestrator still writes the cycle artifact and
appends a line to `editorial/blurbs/_inbox.md`. The user can open
the inbox file manually. The inbox file is the auditable list of
pending cycles even when email is working; it is also the v3 path
for a VS Code extension that pings on inbox updates.

### 5.3 No skip-review mode in Phase 1 or Phase 2

The user has stated they want to check every blurb. The review
surface does not include auto-approve in v1 or v2. If after 60
cycles the user is approving with no-or-trivial edits, the
editorial-director will re-open the question with a written
proposal; the question stays closed until then.

---

## 6. Audit trail

Every cycle has a complete agent history. Two surfaces:

1. **Append-only log file** at
   `editorial/blurbs/<section>/<unit-slug>/<release-id>.log.md`.
   One line per event, ISO timestamp prefix. Events include: state
   transitions, flags, retry counts, escalations, user actions,
   email send / failure, build pickups.

   Example log content:
   ```
   2026-05-14T08:30:00Z scheduler release_landed cycle_init
   2026-05-14T08:32:00Z researcher context_drafted ok
   2026-05-14T08:35:00Z writer writer_drafted ok
   2026-05-14T08:36:00Z fact-checker fact_check_fail numeric_mismatch
                          token=2.4% expected=2.3% source=v41690914
   2026-05-14T08:37:00Z writer writer_drafted retry-1 ok
   2026-05-14T08:38:00Z fact-checker fact_checked ok
   2026-05-14T08:40:00Z style-editor style_polished ok
   2026-05-14T08:42:00Z orchestrator email_sent to=jay...@outlook.com
   2026-05-14T09:15:00Z user status_change ready_for_user->approved
   2026-05-14T09:20:00Z build published commit=abc1234
   ```

2. **State-history block** in the cycle artifact's front-matter
   (per Section 3.2), a structured machine-readable summary of the
   key state transitions. This is the short version; the log file
   is the full version.

3. **Fact-check trace** at `editorial/verifications/blurbs/
   <section>/<unit-slug>/<release-id>.json` -- the per-token
   verification table. Kept separately because it is a structured
   JSON that the user does not normally read but a post-mortem
   reviewer does (see Section 7 Phase 3 post-mortem cadence).

Retention: append-only forever; git is the backing store. A blurb
from October 2026 should be reconstructable from the audit trail
plus the historical data sidecar in 2030.

---

## 7. 3-phase rollout

Phase 1, Phase 2, Phase 3 carry forward from v1 Section 9 with
multi-agent shape adjustments.

### 7.1 Phase 1 -- manual trigger, Inflation only, multi-agent pass

**Scope.** Inflation section only (six chartbook units;
`inflation_basics.panel-1` through `panel-6`). CPI release cycle
runs end-to-end through the four-agent pipeline. The trigger is
manual: a CLI command `python -m pipeline.blurbs.run --release-id
cpi_monthly_<YYYY-MM>` invoked by the user once they confirm the
release has landed in `data/processed/`. No scheduler in Phase 1;
the manual trigger keeps the surface small while the agent
choreography is being shaken down.

**Multi-agent flow.** All four agents in the cycle. The orchestrator
walks the state machine; each agent is invoked via the existing
Claude Agent SDK dispatch path. Researcher writes context notes
overnight before CPI release (the May 2026 release lands May 20 mid-
month; researcher writes context notes the morning of). Writer,
fact-checker, style-editor run in sequence on the orchestrator's
dispatch.

**Done when.**
- Two consecutive CPI release cycles have produced approved blurbs
  through the full pipeline (researcher context -> writer draft ->
  fact-check -> style polish -> user review -> approval ->
  publish).
- The fact-checker has caught at least one mechanical numeric error
  in the writer's draft and routed back; the user has seen the
  re-draft work mechanically.
- The style-editor has flagged at least one voice slip (hedging
  tic, cliche) and the polish pass has corrected it without
  changing facts.
- End-to-end cycle time for a single unit is under 30 minutes from
  CLI trigger to email-in-inbox. Target latency carries forward
  from this memo's headline requirement.
- The user has reviewed 12 drafts (six units x two cycles) and can
  articulate which agent in the pipeline is doing the load-bearing
  work for the user's review step. (If the user's rewrites are
  mostly fact corrections, the fact-checker pass is weak; if mostly
  voice corrections, the style-editor pass is weak; if mostly
  context corrections, the researcher pass is weak. This signal
  drives Phase 2 tuning.)

### 7.2 Phase 2 -- scheduled trigger, Inflation + Labour + Policy

**Scope.** Three sections live with auto-blurb pipelines:
Inflation, Labour, Policy (monetary). These are the three
success-criteria-named sections in `dashboard_purpose.md` Section
9.3. The trigger is now scheduled: cron-style scheduler running
the calendar-plus-content-hash logic per v1 Section 1. Releases
fire automatically; the user no longer runs CLI commands except
for one-off corrections.

**Multi-agent flow.** Same four-agent flow as Phase 1, now firing
unattended. Email notification is the default surface. The
`editorial/blurbs/_inbox.md` digest file is generated on each
release and surfaces the queue.

**Done when.**
- Three consecutive release cycles per section have produced
  approved blurbs through the full pipeline without manual
  intervention from the user beyond the review step.
- The scheduler has fired correctly for at least 10 calendared
  releases (no false fires, no missed real fires; calendar
  correctness baseline established).
- Per `dashboard_purpose.md` Section 9.3, Mode 2 is operating on
  Inflation, Labour, and Policy (monetary) with every blurb
  passing human review before publish. November 2026 milestone.
- The user reports the review step taking under 5 minutes per
  blurb on average across the month -- a sharper bar than v1's
  "rewrite step under 5 minutes" because Phase 2 has style-editor
  doing the polish.

### 7.3 Phase 3 -- full coverage, post-mortem cadence

**Scope.** All seven sections live (GDP, Inflation, Labour,
Housing, Policy monetary, Policy fiscal, Markets, Trade -- the
Policy split into two sub-surfaces continues per dashboard_purpose
Section 4.5). Auto-blurb pipeline runs the full multi-agent flow on
every release. Monthly post-mortem cadence: editorial-director
reviews any cycles that escalated to user in the prior month,
re-tunes the per-agent briefs (Section 2) and the writing-style.md
voice canon if a pattern emerges.

**Multi-agent flow.** Same four-agent flow, now with the
fact-checker post-rewrite soft-warning surface (the v1 "two-cycle
exception" from Section 5) enabled. If the user's rewrite changes a
verified number, the pre-commit hook flags it as a soft warning.
The user can override; the override is logged.

**Done when.**
- All seven sections have run through at least one complete
  release cycle with approved blurbs.
- The editorial-director has held two monthly post-mortems and the
  per-agent briefs are on their third revision (the briefs are
  living documents, tuned against actual cycle data).
- Average end-to-end cycle latency stays under 30 minutes;
  per-blurb user-review time stays under 5 minutes; cycle escalations
  occur on under 10 percent of cycles.

---

## 8. Cost and capacity

### 8.1 Per-cycle LLM-call count

v1 was one LLM call per unit (writer-only; the fact-checker and
style-editor were mechanical validators). v2 is four LLM calls per
unit on the happy path: researcher (context note), writer (draft),
fact-checker (verification verdict; the fact-checker is an agent
not a regex), style-editor (polish).

On the unhappy path: one or two re-drafts on writer (fact-checker
re-route), one re-polish on style-editor, plus the researcher being
re-routed for a TK. Budget multiplier on cycles where any retry
fires: ~1.4x baseline. Empirical: assume ~1.3x average across the
fleet given the writer / fact-checker / style-editor agents are all
calibrated to the same voice canon.

### 8.2 Per-month token budget

Per v1 Section 7's fan-out math: ~45 unit-fires per month at full
coverage steady state.

Per-call token budget per agent (rough, in input + output tokens):

| Agent | Input tokens | Output tokens | Note |
|---|---|---|---|
| researcher | ~4,000 | ~400 | reads context note prior, data sidecars, prior approved blurb, voice canon |
| writer | ~5,000 | ~150 | reads researcher note, data, chart manifest, voice canon |
| fact-checker | ~3,500 | ~300 | reads draft, data sidecars, primary URLs, voice canon |
| style-editor | ~3,000 | ~200 | reads draft, voice canon |
| **Per-unit total** | **~15,500** | **~1,050** | round trip |

Per-month token cost at full coverage with the ~1.3x retry
multiplier: ~45 unit-fires/mo * (~15,500 + ~1,050) tokens * 1.3 =
~970,000 tokens per month.

At Claude Sonnet pricing of approximately $3 per 1M input tokens and
$15 per 1M output tokens, with ~94% of tokens being input: monthly
LLM cost is approximately **$3 to $8 per month at Phase 3 steady
state**. Slightly higher than v1's $1-3 estimate because the
multi-agent fan-out is 4x the call count per cycle, but tokens are
still noise relative to developer time.

At Phase 2 (3 sections, ~20 unit-fires/mo): ~$2 to $4 per month. At
Phase 1 (Inflation only, ~6 unit-fires/mo): under $1 per month.

The cap of $5-15/mo at Phase 3 set in the design brief is held.

### 8.3 Per-cycle latency

Per the design brief's headline requirement: end-to-end blurb cycle
under 30 minutes from release-land to user-inbox-email.

Per-stage latency budget:

| Stage | Budget | Note |
|---|---|---|
| release-land detection | ~5 min | scheduler polls calendar; content-hash check |
| researcher (context note) | ~5 min | LLM round trip, single unit |
| writer (draft) | ~3 min | LLM round trip per unit |
| fact-checker (verify) | ~3 min | LLM round trip per unit |
| style-editor (polish) | ~2 min | LLM round trip per unit |
| email send | ~1 min | SMTP |
| slack budget | ~11 min | retry on any stage, queuing latency |
| **End-to-end** | **~30 min** | hard ceiling |

For a release that fires multiple units (e.g. CPI fires 6 units),
the pipeline parallelizes across units after the release-land
detection. Per-unit latency stays the same; the user gets either 6
emails (one per unit) or a single batched-email digest -- Phase 1
sends per-unit emails for visibility into each cycle's flow; Phase 2
and 3 may batch to reduce inbox noise (open question; user choice in
Phase 2 retrospective).

---

## 9. Backend-engineer brief (Phase 1 build)

Paste-ready brief for main Claude to dispatch to `backend-engineer`.

---

**Title.** Build Phase 1 of the auto-blurb pipeline.

**Reference.** `editorial/auto_blurb_process.md` (this document) is
the design canon. The state machine in Section 1, filesystem layout
in Section 3.2, and per-agent briefs in Section 2 are the
authoritative contract.

**Scope.** Phase 1 only: manual CLI trigger, Inflation section only
(six chartbook units; `inflation_basics.panel-1` through
`panel-6`), end-to-end multi-agent pipeline. No scheduler yet.
Phase 2 (scheduler, two more sections) and Phase 3 (full coverage)
are out of scope for this build.

**Deliverables.**

1. **Filesystem scaffolding.** Create the directories per Section
   3.2:
   - `editorial/blurbs/_cycles/`
   - `editorial/blurbs/inflation/panel-1-headline-cpi/`
   - `editorial/blurbs/inflation/panel-2-core-measures/`
   - `editorial/blurbs/inflation/panel-3-breadth/`
   - `editorial/blurbs/inflation/panel-4-subaggregates/`
   - `editorial/blurbs/inflation/panel-5-expectations/`
   - `editorial/blurbs/inflation/panel-6-passthrough/`
   - `editorial/verifications/blurbs/inflation/<unit-slug>/`
     for each of the six unit slugs above
   - `research/blurb_context/`
   - `editorial/blurbs/_inbox.md` (initially an empty stub with
     header `# Pending auto-blurb review`)

2. **Cycle artifact schema.** Implement `pipeline/blurbs/
   artifact.py` exposing:
   - `CycleArtifact` (pydantic model) with fields per Section 3.2
     front-matter spec.
   - `read_artifact(path) -> CycleArtifact`
   - `write_artifact(path, artifact, body)` -- serialises
     front-matter + body to Markdown with YAML front-matter block.
   - `transition_state(artifact, new_state, agent_name, note)` --
     appends to `state_history`, updates `last_state`, writes
     audit-log line to `<release-id>.log.md`.

3. **CLI command.** `pipeline/blurbs/run.py` with the entry point
   `python -m pipeline.blurbs.run --release-id <release-id>`.

   Behaviour:
   - Look up the release in a Phase-1-only release registry (a
     small Python dict in `pipeline/blurbs/registry.py` listing
     `cpi_monthly` with the six dependent units and the primary
     series IDs).
   - For each unit, create the cycle artifact at
     `editorial/blurbs/inflation/<unit-slug>/<release-id>.md`
     with `last_state: release_landed`.
   - Walk the state machine: invoke the four agents in sequence
     via the Claude Agent SDK dispatch (see existing pattern in
     repo for agent invocation; if no pattern exists yet, use
     subprocess to the `claude` CLI with a `/auto-blurb-<role>`
     skill -- design the skills under
     `.claude/commands/auto-blurb-<role>.md`).
   - On each agent's return, validate the deliverable, update the
     cycle artifact, write the audit log.
   - On final state `style_polished`, transition to
     `ready_for_user` and trigger the email.
   - On any failure that exceeds retry budget, transition to
     `escalated` and email the user with the escalation subject.

4. **Per-agent prompt scaffolding.** Four skill files under
   `.claude/commands/`:
   - `auto-blurb-researcher.md` -- invokes researcher with the
     release-id and unit-slug; returns the context note. Template
     per Section 2.1 deliverable.
   - `auto-blurb-writer.md` -- invokes writer; returns the body.
     Template per Section 2.2.
   - `auto-blurb-fact-checker.md` -- invokes fact-checker; returns
     the verdict JSON and pass/fail. Template per Section 2.3.
   - `auto-blurb-style-editor.md` -- invokes style-editor; returns
     the polished body. Template per Section 2.4.

   Each skill embeds the relevant slice of voice canon (Section 7
   Mode A from writing-style.md, Section 6 banned constructions,
   Section 8 consensus prose) inline. The skills are versioned;
   bump on every revision.

5. **Email send.** `pipeline/blurbs/email.py` exposing
   `send_review_email(artifact)`. Phase 1 implementation:
   - Use SMTP via an env-var-configured relay (e.g.
     `SIBLEY_SMTP_HOST`, `SIBLEY_SMTP_USER`, `SIBLEY_SMTP_PASS`,
     `SIBLEY_SMTP_FROM`). Document in `data/SOURCES.md` or
     equivalent ops doc.
   - Subject line per Section 5.1.
   - Body per Section 5.1 (plain-text with inline draft).
   - On SMTP failure: 3 retries at exponential backoff (1m / 5m /
     30m). After exhaustion, log to audit trail and append to
     `editorial/blurbs/_inbox.md`.

6. **Voice pre-checks.** `pipeline/blurbs/validators.py` exposing
   `validate_mode2_body(text) -> ValidationResult` with the
   mechanical checks per Section 2.2 pass criteria:
   - Word count 25-95.
   - Sentence count 2-4.
   - ASCII-only.
   - No substring match against the banned-construction list
     (loaded from `editorial/writing-style.md` Section 6 -- parse
     the list at module-load time so updates to writing-style.md
     flow through without code changes).
   - No `TK` token.
   - No Big-Six bank name in attribution context (regex: bank
     names followed by `expected|forecast|called|said|see|sees|
     thinks|believes` etc.; allow bank names in non-citation
     contexts like "Big-Six PCL builds").

7. **Fact-check mechanical helper.** `pipeline/blurbs/factcheck.py`
   exposing `extract_numeric_tokens(text) -> list[Token]` and
   `verify_token(token, series_csv, meta_json,
   rounding_tolerance) -> Verdict`. The fact-checker agent uses
   these helpers; the agent provides the judgment, the helpers
   provide the lookup.

8. **Pre-commit hook.** `.githooks/pre-commit-blurb` or equivalent
   that runs on every commit:
   - For each modified file under `editorial/blurbs/<section>/
     <unit-slug>/*.md`, check that the body still passes
     `validate_mode2_body`.
   - If `status: ready_for_user -> status: approved` transition
     is detected, stamp `approved_by_at: <ISO timestamp>` into
     the front-matter.
   - If the user has changed a number in the body that the
     fact-checker verified, raise a soft warning (Phase 1: just
     log; Phase 3 enables the warning as per Section 4.5 of
     this doc, deferred for Phase 1).

9. **Tests.** Pipeline tests next to the code:
   - `pipeline/blurbs/test_artifact.py` -- read / write /
     transition round trips.
   - `pipeline/blurbs/test_validators.py` -- voice pre-check
     happy path + every banned construction.
   - `pipeline/blurbs/test_factcheck.py` -- numeric extraction +
     verification against a fixture CSV.
   - `pipeline/blurbs/test_run.py` -- integration test that mocks
     the four agent dispatches and walks a cycle from
     `release_landed` to `ready_for_user`, asserts state
     transitions and audit-log content.

10. **Documentation.** `pipeline/blurbs/README.md` -- the
    operator manual: how to run the CLI, where artifacts land,
    what the env vars are, how to debug a stuck cycle.

**Out of scope for Phase 1.**
- The scheduler (Phase 2).
- The other six sections (Phase 2 brings Labour + Policy;
  Phase 3 brings the rest).
- Post-rewrite soft-warning fact-check (Phase 3).
- Reply-as-approval email parsing (v3).
- VS Code extension for inbox polling (v3).
- Few-shot exemplars in the writer prompt (v3; defer until 10
  reviewed cycles produce a stable corpus per v1 Section 2's
  "does not" list).

**Architecture notes.**
- Python 3.11+ per `backend-engineer.md` agent brief floor.
- pydantic for boundary validation; the cycle artifact and the
  release-registry entries are pydantic models.
- YAML front-matter parsed via `ruamel.yaml` (preserves comments
  and order; PyYAML lossy on round-trip).
- ASCII-only on all generated artifacts; the Windows toolchain
  enforces this per the user's environment.
- Loud failures only; silent fallback to stale state is
  forbidden per backend-engineer agent brief.

**Acceptance criteria.**
- Running `python -m pipeline.blurbs.run --release-id
  cpi_monthly_2026-04` with stubbed agent dispatches produces
  six cycle artifacts in
  `editorial/blurbs/inflation/<unit-slug>/cpi_monthly_2026-04.md`,
  each with full state history through `ready_for_user` and an
  email-sent event in the audit log.
- The voice pre-check rejects a body containing "going forward"
  with a specific failure message naming the banned construction.
- The fact-checker helper, given a draft body containing `2.3%`
  and a fixture CSV with `2.3` as the latest value, returns a
  verified verdict; given `2.4%` against the same CSV, returns a
  contradicted verdict.
- The pre-commit hook stamps `approved_by_at` on a
  draft-to-approved status transition.

End of brief.

---

## Appendix. What this v2 changes from v1

The v1 design memo (now archived at
`research/auto_blurb_pipeline_design_v1_archived.md`) was a
single-LLM-plus-mechanical-validators design. The v2 changes
are:

1. **Four-agent flow replaces single-LLM-call.** Researcher
   produces a structured release-context note; writer drafts;
   fact-checker is an agent not a regex; style-editor performs the
   voice polish. The user reviews a draft that has already passed
   editorial steer, drafting, fact-checking, and voice polish.

2. **State machine made explicit.** v1 had implicit state via the
   front-matter `status` field; v2 names every state, every gate,
   every owner, every fail policy.

3. **Audit trail formalized.** v1's `voice_validation`,
   `fact_check_at`, and `model` front-matter fields are extended
   to a full `state_history` block plus an append-only
   per-cycle log file plus a per-cycle fact-check trace JSON.
   Every cycle is reconstructable from disk.

4. **Email surface specified.** v1 deferred the notification
   surface to an open question; v2 commits to email-to-
   jayzhaomurray@outlook.com per user instruction, with a
   specified subject-line format, body shape, and SMTP retry policy.

5. **Failure modes assigned to retry-budgeted re-routes.** v1
   said "re-prompt on fail"; v2 says where the failure routes
   (which agent gets it back), how many retries are budgeted,
   and what triggers escalation to user.

6. **Quiet release flow added.** v1 said the prompt has a "none
   for this release" path; v2 makes "quiet release" a first-class
   cycle variant with shorter blurb and a tagged email subject.

7. **Cost model updated for four-agent fan-out.** v1's $1-3/mo
   estimate becomes $3-8/mo at Phase 3 with the multi-agent flow.
   Still negligible.

8. **Backend brief delivered.** v1 ended with open questions for
   the user; v2 ends with a paste-ready Phase 1 build brief.

End of document.

## Changelog

- 2026-05-11: Initial v2 version. Multi-agent process design.
  Supersedes researcher's v1 single-LLM design. editorial-director.
