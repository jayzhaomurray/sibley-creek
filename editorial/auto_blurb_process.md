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

The three named review gates (fact-check, style-polish, surface-fit)
are the canonical pre-publish gates per `editorial/review_protocol.md`.
The state machine names them as `fact_checked`, `style_polished`,
and `surface_fit_passed` respectively. Surface-fit (Gate 3) is owned
by editorial-director and runs after style-polish so the polished
prose is what gets judged for surface appropriateness.

States, in order:

1. `pending_release` -- the release is calendared but the upstream
   publisher has not yet posted a new vintage. Owner: backend-engineer
   (pipeline scheduler).
2. `release_landed` -- the pipeline has detected a new `release_date`
   on the unit's primary series sidecar (content-hash trigger of
   v1 Section 1; carried forward) and written the new CSV + meta.json.
   Cycle artifact created on disk; owner handoff to researcher.
3. `context_drafted` -- researcher has produced a structured
   release-context note for every unit in the release's fan-out. The
   note is the editorial steer the writer needs, expressed as a
   machine-readable YAML claim-card list (Section 1.2) plus the
   thin prose-steer fields (so_what, historical_comparable,
   quiet_release). Owner handoff to **verifier (fact-checker in
   claims-verification mode)**.
4. `claims_verified` -- the verifier has re-fetched every
   `source_url` in the claim-card list, located the
   `source_text_excerpt` in the fetched content, and confirmed
   the `value` and `claim` are supported. Every card carries
   `verifier_status: passed`. This is the structural defense against
   researcher-side hallucination, source-conflation, and
   recall-not-fetch errors (Section 1.3). Owner handoff to writer.
5. `writer_drafted` -- writer has produced the Mode 2 blurb body
   (2-4 sentences) for each unit, scaffolded by the verified
   claim-cards plus the raw release data plus a description of the
   chart visual. Owner handoff to fact-checker (draft-verification
   mode).
6. `fact_checked` -- fact-checker has verified that every numeric
   token, every named institution, and every cited release date in
   the writer's draft is grounded in a `verifier_status: passed`
   claim-card, plus the absence of TK leakage and banned-source
   phrasing. With the upstream `claims_verified` gate already in
   place, the fact-checker's draft-pass job is lighter: it is
   confirming the writer used the cards correctly, not that the
   underlying claims are true (Section 1.4). Owner handoff to
   style-editor.
7. `style_polished` -- style-editor has polished voice against
   `editorial/writing-style.md` Section 7 Mode A. Owner handoff to
   editorial-director for surface-fit review (Gate 3).
8. `surface_fit_passed` -- editorial-director has run Gate 3 per
   `editorial/review_protocol.md` and the polished draft has cleared
   the surface-fit question (does this content belong on this
   surface, in this context). Catches internal canon-jargon
   ("tri-modal product", "chartbook unit", "Mode 2"), voice doctrine
   bleeding into reader-facing prose, process-talk, template-slot
   drift, and length mismatch with the surface. Owner handoff to
   user.
9. `user_review` -- email lands in user inbox; draft file is in
   `editorial/blurbs/<section>/<unit-slug>/<release-id>.md` with
   `status: ready_for_user`. User opens, reads, rewrites if desired,
   sets `status: approved`. Owner: user.
10. `approved` -- user-approved. The build picks it up on the next
    render pass.
11. `published` -- the build has rendered the approved blurb into the
    live site. Terminal state.

Each transition has a gate, an owner, a fail policy, and an escalation.

| From | To | Gate | Owner | Fails on | On fail |
|---|---|---|---|---|---|
| `pending_release` | `release_landed` | New `release_date` on primary series sidecar | backend-engineer (scheduler) | Calendar window passes with no fetched change | Stale-alert email after N polls (per release-key cadence rule in `pipeline/calendar/releases.py`); user investigates |
| `release_landed` | `context_drafted` | Researcher returns a context note (one entry per unit) containing a claim-card YAML list per Section 1.2 schema | researcher | Researcher declares "quiet release" for all units in fan-out, or returns malformed cards (missing URL, missing source_text_excerpt, vague source_kind) | Cycle short-circuits to the "quiet release" flow (Section 4.1) on legitimate quiet; malformed cards route back to researcher with a specific schema-failure list, counts against the 2-round-trip budget |
| `context_drafted` | `claims_verified` | Verifier (fresh-context fact-checker invocation) re-fetches every `source_url`, locates `source_text_excerpt`, confirms `value` and `claim`. Every card returns `verifier_status: passed` | fact-checker in claims-verification mode | Any card returns `verifier_status: failed:<reason>` per the five-reason taxonomy (Section 1.3) | Route back to researcher with the specific failure list. Researcher revises the failed cards. Budget: 2 researcher round-trips. On the third failure, escalate to user; the blurb does not publish |
| `claims_verified` | `writer_drafted` | Writer returns a 2-4 sentence Mode 2 body that passes voice-validator pre-checks (word count 25-95, sentence count 2-4, ASCII-only, no banned constructions in `writing-style.md` Section 6) | writer | Writer flags an unresolved TK or returns prose that fails mechanical pre-checks | Up to two writer re-runs; on third failure escalate to user |
| `writer_drafted` | `fact_checked` | Fact-checker verifies all numeric tokens within rounding tolerance, all dates against the release calendar, no TK leakage, no Big-Six citation, no banned-source phrasing | fact-checker | Numeric mismatch, TK in body, banned-source phrasing, source URL 404 | Up to two re-drafts (return to writer); on third failure escalate to user with the trace |
| `fact_checked` | `style_polished` | Style-editor returns a polished version (Mode A voice) or asserts the draft already meets the bar | style-editor | Hedging tic, banned cliche, jargon-as-armor, register slip toward Mode B | One re-polish if first pass is rejected by self-check; on second failure escalate to user with diff |
| `style_polished` | `surface_fit_passed` | editorial-director returns surface-fit-PASS or surface-fit-REJECT with cuts (Gate 3 per `editorial/review_protocol.md`) | editorial-director | Internal canon-jargon ("tri-modal product", "chartbook unit", "Mode 2", "Big-Six framing"), voice-doctrine or process-talk bleeding into reader-facing prose, template-slot drift, length mismatch with the surface | Return to writer with the editorial-director's cut list; counts against the Gate 3 re-run budget (max 2 re-runs per cycle). On budget exhaustion, escalate to user with both versions and the cut list attached |
| `surface_fit_passed` | `user_review` | Email to jayzhaomurray@outlook.com sent; file written to disk with `status: ready_for_user` | pipeline orchestrator | SMTP failure | Retry email 3x at exponential backoff (1m, 5m, 30m); after that, fall back to writing only `editorial/blurbs/_inbox.md` and surface a desktop-notification path |
| `user_review` | `approved` | User edits file front-matter from `status: ready_for_user` to `status: approved` and commits | user | User sets `status: rejected` (rare) or leaves draft idle | If idle past one full release-cycle for that series, the draft is auto-retired (`status: stale`); the next cycle's draft becomes the live blurb. Per v1 Section 8.6 |
| `approved` | `published` | The Astro build picks the file up on next push to `main` or on the hourly rebuild | backend-engineer (build) | Build error | Loud failure; the prior approved blurb continues to render |

Two cross-cutting state fields, present on every cycle artifact:

- `last_state` -- where we are now.
- `state_history` -- append-only list of `(state, timestamp, agent_or_user, note)` tuples. This is the audit trail (Section 6).

### 1.1 Why the `claims_verified` gate exists

The v2 design (the version dated 2026-05-11 before this addendum)
had six anti-hallucination guards but they all assumed the
researcher's context note was trustworthy input. They did not defend
against the researcher themselves hallucinating, conflating two
sources they looked up in the same session, recalling-not-fetching
a number from training, or citing a rotted URL.

The Pillar A wave-4 corrections (see
`research/wave4_pillar_a_mortgage_renewal_wall_anchors.md` "TOP-OF-
FILE FACTUAL ALERT") proved this failure mode is real. A prior
fact-check had stamped "BoC overnight rate 2.75% VERIFIED" by walking
the `sections.ts` placeholder chain rather than re-fetching the BoC
press release directly. The chain-of-trust was internally consistent
and false. Wave 5 caught it only because the researcher re-fetched
the actual primary source
(https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/)
and read the verbatim text: "the Bank held its target for the
overnight rate at 2.25%." The rate had been at 2.25% since the
October 29, 2025 cut; the "2.75% on April 29, 2026" claim
propagated through multiple downstream deliverables (homepage
tile-lines, deepdive draft lede, deepdive Section IV framing)
before the primary-source re-fetch caught it.

The structural lesson: an LLM asked to verify its own work tends to
double down on the hallucination it just produced (LLM consistency
bias). A separate verifier with no memory of the researcher's
reasoning and a hard requirement to re-fetch the URL is the defense.

### 1.2 Claim-card schema

The researcher's `context_drafted` output is no longer free-form
prose. For auto-blurb cycles, the researcher emits a structured
YAML list of atomic claim-cards plus a thin prose-steer block. The
prose-steer block carries `so_what`, `historical_comparable`,
`quiet_release`, and `next_print_date` (unchanged from Section 2.1).
The claim-card list carries every numeric or attributable factual
input the writer needs.

Schema (one card per atomic claim):

```yaml
- claim_id: <unit-slug>-<release-id>-<short-slug>
    # e.g. panel-1-cpi_monthly_2026-04-headline-yoy
  claim: <one-sentence summary of the factual claim>
    # e.g. "Headline CPI rose 2.3% Y/Y in April 2026"
  value: <numeric value if applicable, else null>
    # e.g. 2.3
  unit: <unit string if applicable, else null>
    # e.g. "percent y/y" | "basis points" | "C$ billions" | null
  source_url: <primary-source URL -- must be specific, dated, fetchable>
    # e.g. "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm"
    # NOT "https://www.bankofcanada.ca" (root domain is not a valid card)
    # NOT a wire-service or media-summary URL
  source_text_excerpt: <verbatim text from the source containing the claim>
    # 50-300 chars; must appear verbatim in the page body so the
    # verifier can grep-match (whitespace / HTML normalization OK).
    # e.g. "The Consumer Price Index (CPI) rose 2.3% on a year-over-
    #      year basis in April, following a 1.8% increase in March."
  fetched_at: <ISO 8601 timestamp of when the researcher fetched the URL>
    # e.g. "2026-05-14T08:32:00Z"
  source_kind: <enum>
    # one of: statcan_wds | statcan_daily | boc_valet |
    # boc_press_release | boc_mpr | boc_fsr | boc_sap | boc_san |
    # osfi_m4 | osfi_other | cmhc_rmir | cmhc_observer | cba_pdf |
    # dof_fiscal_monitor | dof_budget | pbo_efo | crea_stats |
    # trreb_market_watch | bank_earnings_supplement | open_canada |
    # other
    # "other" requires a one-line note in verifier_notes on
    # researcher's side explaining the source type
  verifier_status: pending
    # set by verifier on the claims_verified pass: passed | failed:<reason>
  verifier_notes: null
    # set by verifier on failure with the specific mismatch
```

Hard constraints on what counts as a valid claim-card:

- `source_url` must be a specific, dated, fetchable URL. Vague
   citations like "BoC press release" or "BoC Staff Analytical
   Paper" without URL+date are NOT valid claim-cards and the
   verifier returns `failed:source_kind_mismatch` (the URL/source
   pair is unverifiable, so it cannot pass).
- `source_text_excerpt` must be verbatim from the source. If the
   researcher had to compute the value (e.g. Y/Y growth from a
   level table), the card must include a derivation card alongside
   the underlying level card -- the writer cannot cite a derived
   value without both atoms verified.
- `fetched_at` is the timestamp at which the researcher actually
   fetched the URL in this cycle. Recall-from-training is not
   permitted: every URL the researcher cites must be fetched at
   output time. A `fetched_at` timestamp more than 24 hours older
   than the cycle's `created_at` is suspect and the verifier may
   flag for re-fetch.
- Sell-side notes (Big-Six bank morning notes) are NOT valid
   sources for claim-cards. Per writing-style.md Section 8, consensus
   inputs from forecaster surveys are fine; cited bank views are
   not. The verifier rejects any card where the URL points to a
   bank research portal as the primary citation.

### 1.3 Verifier behavior

The verifier runs in `claims_verified` mode (see
`.claude/agents/fact-checker.md` Section "Claim verification
(auto-blurb cycle)"). It is dispatched as a **separate agent run**
from the researcher who produced the cards. Fresh context. No
shared conversation. The verifier sees only the claim-card YAML
file -- not the researcher's reasoning, not the prior conversation,
not the so_what prose. This is the structural defense against LLM
consistency bias.

For each claim-card the verifier:

1. Re-fetches `source_url` via WebFetch.
2. Locates `source_text_excerpt` in the fetched content. Fuzzy-match
    acceptable for whitespace / HTML normalization, but the
    substantive text must be present verbatim.
3. Confirms `value` is present in the matched span (numeric
    extraction). For derived values, confirms both the level card
    and the derivation are verifiable.
4. Confirms `claim` is a fair summary of the matched span. This
    is an LLM judgment call; in ambiguous cases, the verifier
    flags for human review rather than guessing.
5. Sets `verifier_status: passed` or `failed:<reason>`.

Failure-reason taxonomy (exactly five, exhaustive):

- `url_404` -- the URL is unreachable (HTTP 4xx / 5xx, DNS failure,
   or returns a "page moved" stub). Researcher must supply a
   working URL.
- `text_not_present` -- the `source_text_excerpt` is not found in
   the fetched content. The page was reached but the excerpt is
   not on it (researcher may have confabulated the excerpt or
   linked to the wrong page on the right domain).
- `value_mismatch` -- the `source_text_excerpt` is present but
   the `value` field is not in the matched span, or differs from
   what the source actually shows. This is the 2.75%-vs-2.25%
   failure mode.
- `claim_overreach` -- the `claim` field summarizes more than the
   source actually supports. The excerpt is on the page and the
   value is right, but the one-sentence claim extrapolates beyond
   what the source said (e.g. claim says "BoC signalled it will
   cut again" but the excerpt only contains "the Bank will continue
   to assess incoming data").
- `source_kind_mismatch` -- the `source_kind` does not match the
   URL. E.g. card is tagged as `boc_press_release` but the URL
   resolves to a Globe and Mail article, or tagged `statcan_daily`
   but resolves to a CBA PDF. Also returned when `source_url` is
   too vague to be fetchable (root domain, undated landing page).

Verifier output is the same YAML file with `verifier_status` and
`verifier_notes` filled in on each card. The orchestrator parses
the file and decides the transition.

### 1.4 Researcher revision budget and post-writer fact-check

If any card fails verification, the orchestrator routes the file
back to the researcher with the specific failures listed. The
researcher revises only the failed cards (passed cards are
sticky -- the verifier does not re-run on passed cards in the next
round; this saves WebFetch calls and limits the failure surface).

The researcher revision budget is **2 round-trips before
escalation**. Cycle paths:

- Round 1: researcher produces N cards; verifier returns K failures.
- Round 2: researcher revises K cards; verifier returns K' failures
   (K' should be strictly smaller than K if the researcher is
   making real progress; the orchestrator flags K' >= K as a
   research-side hygiene problem).
- Round 3: if any cards still fail, the orchestrator escalates to
   user with the full claim-card YAML, the verifier's failure
   trail, and the cycle does not advance. Subject line:
   `Auto-blurb escalation: claims_verified failed for <release-id>`.

**Post-writer fact-check distinction.** The downstream fact-checker
(running in `writer_drafted` -> `fact_checked` mode, Section 2.3)
still runs as before, but with the upstream `claims_verified` gate
in place, its job becomes lighter. It is no longer responsible for
verifying that "BoC rate = 2.25%" against an external source; that
fact is already in a passed claim-card. The post-writer fact-checker
is confirming the writer used the cards correctly:

- Every numeric token in the body resolves to a passed claim-card's
   `value` (within rounding tolerance).
- No numeric token in the body is missing a backing card (writer
   did not invent).
- The writer did not over-stretch a `claim` (writer did not say
   "core-trim accelerated to a 12-month high" when the backing
   card only supports "core-trim ticked up 0.1 pp").
- TK leakage, banned-source phrasing, Big-Six citation in prose
   are caught as before.

This separation -- "claims true at the source" upstream, "writer
used the claims correctly" downstream -- is the structural shape
the v2 design lacked.

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
to `research/blurb_context/<release-id>/<unit-slug>.md`. The note has
two parts: a thin prose-steer block (the editorial steer) and a
claim-card YAML list (the verifiable factual inputs, per Section
1.2 schema). Every numeric or attributable fact in the prose-steer
block must trace back to a claim-card in the list.

```
unit: <section>.<unit-slug>             e.g. inflation_basics.panel-1
release_id: <release-id>                e.g. cpi_monthly_2026-04
reference_period: <YYYY-MM or YYYY-Qn>
historical_comparable: <free text, 1-2 sentences>
   e.g. "First month Y/Y headline has been within the 1-3% BoC
        control band since January 2023." Every factual atom in
        this sentence must have a backing claim-card.
so_what: <free text, 1 sentence>
   The single observation the writer should anchor the third
   sentence on. May be "none for this release" if the print is
   quiet. Atoms backed by claim-cards.
revision_to_prior: <bool, plus delta if true>
next_print_date: <ISO date>
quiet_release: <bool>
   Set true only if the print is genuinely uneventful. Quiet
   releases still produce a 2-sentence blurb; see Section 4.1.

claim_cards:
   - claim_id: ...
     claim: ...
     value: ...
     unit: ...
     source_url: ...
     source_text_excerpt: ...
     fetched_at: ...
     source_kind: ...
     verifier_status: pending
     verifier_notes: null
   - <one card per atomic fact the writer needs:
       print_value, prior_value, consensus_value, surprise_value,
       and every numeric or attributable fact appearing in
       historical_comparable or so_what>
```

Note: `print_value`, `prior_value`, `consensus_value`, and
`surprise_value` are no longer top-level scalar fields. They appear
as individual claim-cards in the `claim_cards` list (this is what
lets the verifier re-fetch and confirm them). The orchestrator
extracts them from the cards by `claim_id` convention
(e.g. `<unit>-<release-id>-print`, `-prior`, `-consensus`,
`-surprise`) for downstream use.

**Pass criteria.** A context note exists for every unit in the
release's fan-out. Every claim-card is well-formed per Section 1.2
schema (specific URL, verbatim excerpt, valid source_kind, fresh
`fetched_at`). Every numeric or attributable atom in the prose-steer
block (`historical_comparable`, `so_what`) is backed by a card.
The so-what sentence is a factual claim (distinguishable from
interpretation; the writer can ground prose on it without inventing).

The researcher's deliverable is the **input** to the
`claims_verified` gate; passing the researcher's pass-criteria is
necessary but not sufficient. The cards then face the verifier's
fresh-context re-fetch pass (Section 1.3). The researcher cannot
self-stamp `verifier_status: passed`; that field is verifier-only.

**Fail / escalation.** If the researcher cannot produce a context note
for a unit (e.g. underlying data is contradictory, or the
historical-comparable claim is uncertain), the researcher returns the
unit with `quiet_release: true` and `so_what: "no defensible
editorial steer for this release"`. The cycle continues with a
shorter blurb; the user sees a flag in the email. If verifier-side
failures exhaust the 2-round-trip revision budget (Section 1.4),
the cycle escalates to user and the blurb does not publish.

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

### 2.3 fact-checker -- two modes

The fact-checker plays two roles in the cycle. The agent's full
brief is in `.claude/agents/fact-checker.md`; the two modes are
distinct invocations.

#### 2.3a Mode: claims verification (upstream, `context_drafted`
-> `claims_verified`)

**Trigger.** Pipeline transitions to `context_drafted`. Orchestrator
dispatches the fact-checker as a **separate agent run**, fresh
context, no shared conversation with the researcher who produced
the cards.

**Inputs.**
- The claim-card YAML file at
  `research/blurb_context/<release-id>/<unit-slug>.md` -- only the
  cards, not the prose-steer block, not the researcher's reasoning.

**Deliverable.** The same YAML file with `verifier_status` and
`verifier_notes` filled in on each card, plus a verdict summary
written to
`editorial/verifications/blurbs/<section>/<unit-slug>/<release-id>.claims.json`.

**Pass criteria.** Every card returns `verifier_status: passed` per
the five-reason taxonomy in Section 1.3.

**Fail / escalation.** Any card fails -> route back to researcher
with the failure list. Budget: 2 round-trips (Section 1.4). On the
third failure, escalate to user.

#### 2.3b Mode: draft verification (downstream, `writer_drafted`
-> `fact_checked`)

**Trigger.** Pipeline transitions to `writer_drafted`. Orchestrator
invokes fact-checker (this is a separate run from the upstream
claims-verification invocation; the same agent file, different mode).

**Inputs.**
- The writer's draft body in the cycle artifact.
- The verified claim-card YAML (every card now carries
  `verifier_status: passed` from the upstream gate).
- `data/processed/<series>.csv` and `<series>.meta.json` for every
  series the unit shows (for rounding-tolerance lookups).

**Deliverable.** A verification verdict written to
`editorial/verifications/blurbs/<section>/<unit-slug>/<release-id>.draft.json`
plus a state transition on the cycle artifact. The verdict file is
the mechanical trace per v1 Section 5: a list of
`(numeric_token, backing_claim_id, source_value, match_status)`
tuples plus the per-claim verdict.

**Pass criteria** (lighter than v1 because claims-verification has
moved upstream):
- Every numeric token in the body resolves to a passed claim-card's
  `value` (within rounding tolerance). The fact-checker does NOT
  re-fetch the source URL in this mode -- that has already been
  done in Section 2.3a.
- No numeric token in the body lacks a backing card (writer did
  not invent a value).
- The writer did not stretch a `claim` past what the card supports
  (claim_overreach in the writer's prose, mirroring the upstream
  failure mode).
- Every cited date matches the release calendar.
- Every institution name uses the convention in writing-style.md
  Section 4 (BoC not BOC; StatCan not Stats Can).
- No TK leakage.
- No Big-Six citation in prose.

**Fail / escalation (draft mode).** Any mismatch fails the gate.
The fact-checker returns the cycle to the writer with the specific
numbers / phrasings that failed and the backing claim-card value
they should be. After two failed re-drafts, escalate to the user
with the trace attached (the user gets the email, opens the draft,
and sees the failed verifications inline).

**Stale source URL handling.** Source URL freshness was a v1 gate
on the draft pass; in v2 it has moved upstream. A `url_404` failure
is now caught at the `claims_verified` gate, where it routes back to
the researcher to supply a working URL. The draft fact-checker does
not re-validate URLs because the upstream gate has already done so.
(Source-URL hygiene for the live site's `sections.json` is a
separate concern handled at build time per Section 4.5.)

**What fact-checker does NOT do.** The fact-checker does not polish
voice. The fact-checker does not run after the user rewrites the
body -- the user's edit ends the verification chain. Soft-warning
post-edit verification (per v1 Section 5 "two-cycle exception") is a
v3 add and not in scope for Phase 1.

**Important: the two modes are dispatched as separate agent runs.**
The upstream claims-verification invocation does not share context
with the downstream draft-verification invocation, and neither shares
context with the researcher who produced the cards. This is the
structural defense against LLM consistency bias (Section 1.1) and
must be preserved in the orchestrator implementation.

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
  - [release_landed,     2026-05-14T08:30:00Z, scheduler]
  - [context_drafted,    2026-05-14T08:35:00Z, researcher]
  - [claims_verified,    2026-05-14T08:37:00Z, fact-checker (claims mode)]
  - [writer_drafted,     2026-05-14T08:39:00Z, writer]
  - [fact_checked,       2026-05-14T08:41:00Z, fact-checker (draft mode)]
  - [style_polished,     2026-05-14T08:43:00Z, style-editor]
  - [surface_fit_passed, 2026-05-14T08:44:00Z, editorial-director (gate 3)]
  - [ready_for_user,     2026-05-14T08:44:00Z, orchestrator]
researcher_context_path: research/blurb_context/cpi_monthly_2026-04/panel-1-headline-cpi.md
researcher_revision_count: 0    # increments on each claims_verified failure routing back to researcher; max 2 before escalation
claims_verified_path: editorial/verifications/blurbs/inflation/panel-1-headline-cpi/cpi_monthly_2026-04.claims.json
claims_verified_status: passed
fact_check_path: editorial/verifications/blurbs/inflation/panel-1-headline-cpi/cpi_monthly_2026-04.draft.json
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

### 4.4a Surface-fit rejects (Gate 3)

The editorial-director runs Gate 3 on the style-polished body per
`editorial/review_protocol.md`. The verdict is one of:

- **PASS.** The polished prose belongs on the named surface in its
  context. Cycle advances `style_polished -> surface_fit_passed ->
  user_review`.
- **REJECT with cuts.** The prose carries internal canon-jargon,
  voice-doctrine bleed, process-talk, template-slot drift, or is
  length-mismatched to the surface. Editorial-director returns a
  cut list. The cycle returns to `writer_drafted` for a re-draft
  that addresses the cuts. Budget: 2 Gate 3 re-runs per cycle. On
  budget exhaustion, escalate to user with both versions (pre-Gate-3
  polished draft and the editorial-director's cut list) attached.

What Gate 3 catches that the upstream gates do not: fact-check asks
"are the numbers true," style-polish asks "is the voice on canon,"
surface-fit asks "should any of this be on this surface at all." A
draft can pass both upstream gates and still ship internal jargon
or a slot the surface does not need; Gate 3 is the answer.

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
   2026-05-14T08:41:00Z editorial-director surface_fit_passed ok
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
  articulate which agent in the pipeline is doing the central
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
style-editor were mechanical validators). v2 is five LLM calls per
unit on the happy path: researcher (context note + claim-cards),
fact-checker in claims-verification mode (verifier; fresh context),
writer (draft), fact-checker in draft-verification mode (separate
fresh context), style-editor (polish).

On the unhappy path: one or two researcher revisions on
claims_verified failure, one or two writer re-drafts on fact-checker
re-route, one re-polish on style-editor. Budget multiplier on cycles
where any retry fires: ~1.5x baseline. Empirical: assume ~1.35x
average across the fleet.

### 8.2 Per-month token budget

Per v1 Section 7's fan-out math: ~45 unit-fires per month at full
coverage steady state.

Per-call token budget per agent (rough, in input + output tokens):

| Agent | Input tokens | Output tokens | Note |
|---|---|---|---|
| researcher | ~4,500 | ~600 | reads context note prior, data sidecars, prior approved blurb, voice canon; emits prose-steer + claim-cards |
| fact-checker (claims mode) | ~3,000 | ~300 | reads claim-card YAML only; WebFetch round trips per card (the costly piece is the fetch, not the LLM token count) |
| writer | ~5,000 | ~150 | reads verified cards, data, chart manifest, voice canon |
| fact-checker (draft mode) | ~3,000 | ~250 | reads draft, verified cards, data sidecars (no URL re-fetch) |
| style-editor | ~3,000 | ~200 | reads draft, voice canon |
| **Per-unit total** | **~18,500** | **~1,500** | round trip |

Per-month token cost at full coverage with the ~1.35x retry
multiplier: ~45 unit-fires/mo * (~18,500 + ~1,500) tokens * 1.35 =
~1,215,000 tokens per month.

At Claude Sonnet pricing of approximately $3 per 1M input tokens and
$15 per 1M output tokens, with ~92% of tokens being input: monthly
LLM cost is approximately **$4 to $10 per month at Phase 3 steady
state**. Slightly higher than the pre-verifier v2 estimate
because the claims-verification mode adds a fresh-context call per
unit, but tokens are still noise relative to developer time. The
fetch-side cost (WebFetch round trips per card) is bounded by the
researcher's card count, typically 3-6 per unit.

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
| researcher (context note + cards) | ~5 min | LLM round trip + WebFetch per card |
| verifier (claims mode) | ~3 min | fresh-context LLM run + WebFetch per card |
| writer (draft) | ~3 min | LLM round trip per unit |
| fact-checker (draft mode) | ~2 min | LLM round trip per unit; no URL re-fetch |
| style-editor (polish) | ~2 min | LLM round trip per unit |
| email send | ~1 min | SMTP |
| slack budget | ~9 min | retry on any stage, queuing latency |
| **End-to-end** | **~30 min** | hard ceiling |

A `claims_verified` failure that round-trips back to researcher
consumes one researcher + one verifier cycle (~8 min) per round-
trip. With the 2-round-trip budget, the worst-case verifier path
adds ~16 min to the baseline -- which would breach the 30-min
ceiling. The orchestrator may flag any cycle that consumed 2 full
round-trips for editorial-director review even when it ultimately
passes, since systematic 2-round-trip cycles indicate the
researcher prompt or the source-kind enum needs tuning.

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
   - Walk the state machine through the full sequence:
     `release_landed` -> `context_drafted` (researcher) ->
     `claims_verified` (verifier, fresh-context fact-checker
     dispatch via `verify_claims.py`) -> `writer_drafted` (writer)
     -> `fact_checked` (fact-checker draft mode) ->
     `style_polished` (style-editor) -> `ready_for_user`.
   - Invoke each agent via the Claude Agent SDK dispatch (see
     existing pattern in repo for agent invocation; if no pattern
     exists yet, use subprocess to the `claude` CLI with a
     `/auto-blurb-<role>` skill -- design the skills under
     `.claude/commands/auto-blurb-<role>.md`).
   - **The `claims_verified` transition must dispatch the
     fact-checker as a fresh agent run, not as a follow-up to the
     researcher's session.** No shared context. The verifier sees
     only the claim-card YAML file. Same constraint for the
     downstream draft-verification invocation: it is a separate
     run from the upstream claims-verification invocation. This is
     enforced in `verify_claims.py` and the corresponding draft
     verification entry point.
   - On verifier failure, increment the researcher's revision
     count on the cycle artifact, re-route to researcher, repeat.
     Budget: 2 round-trips. On round 3 failure, transition to
     `escalated`.
   - On each agent's return, validate the deliverable, update the
     cycle artifact, write the audit log.
   - On final state `style_polished`, transition to
     `ready_for_user` and trigger the email.
   - On any failure that exceeds retry budget, transition to
     `escalated` and email the user with the escalation subject.

4. **Per-agent prompt scaffolding.** Five skill files under
   `.claude/commands/`:
   - `auto-blurb-researcher.md` -- invokes researcher with the
     release-id and unit-slug; returns the context note plus
     claim-card YAML. Template per Section 2.1 deliverable.
   - `auto-blurb-verify-claims.md` -- invokes fact-checker in
     claims-verification mode (fresh context). Input: claim-card
     YAML path only; no researcher context, no prose-steer.
     Output: same YAML with `verifier_status` filled in. Template
     per Section 2.3a.
   - `auto-blurb-writer.md` -- invokes writer with the verified
     claim-cards plus prose-steer block; returns the body.
     Template per Section 2.2.
   - `auto-blurb-fact-checker.md` -- invokes fact-checker in
     draft-verification mode; returns the verdict JSON and
     pass/fail against the writer's body. Template per Section 2.3b.
   - `auto-blurb-style-editor.md` -- invokes style-editor; returns
     the polished body. Template per Section 2.4.

   Each skill embeds the relevant slice of voice canon (Section 7
   Mode A from writing-style.md, Section 6 banned constructions,
   Section 8 consensus prose) inline. The two fact-checker skill
   files embed only the slice relevant to their mode (the
   claims-verification skill embeds the Section 1.2 schema and 1.3
   taxonomy; the draft-verification skill embeds the writer's body
   rules). The skills are versioned; bump on every revision.

4b. **Claim-card verification entry point.**
   `pipeline/blurbs/verify_claims.py` exposing:
   - `verify_claim_file(path: Path) -> VerifyResult` -- reads the
     claim-card YAML at `path`, dispatches the fact-checker in
     claims-verification mode as a **fresh agent run** (separate
     CLI invocation or fresh SDK session; no shared context with
     the researcher's session that produced the file), parses the
     verdict YAML back, writes the updated cards to the same path,
     returns a `VerifyResult` summarizing pass/fail counts and the
     per-card status.
   - `VerifyResult` (pydantic) fields: `total_cards`,
     `passed_count`, `failed_count`, `failures: list[CardFailure]`
     where `CardFailure` is
     `(claim_id, reason, verifier_notes)`.
   - On dispatch, the entry point MUST NOT pass any context other
     than the claim-card YAML file path to the verifier. The
     prose-steer block (`so_what`, `historical_comparable`) is
     stripped before dispatch.
   - Audit-trail append: every verify_claims run appends a single
     line to `<release-id>.log.md` with timestamp, total/passed/
     failed counts, and the failed `claim_id` list with reasons.
   - The state-machine driver in `run.py` calls
     `verify_claim_file()` on the researcher's output, and
     transitions `context_drafted -> claims_verified` if all
     pass, otherwise routes back to researcher and increments
     `researcher_revision_count` on the cycle artifact's
     front-matter.

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
   - `pipeline/blurbs/test_verify_claims.py` -- claim-card
     verification: happy path (all cards pass), each of the five
     failure reasons (`url_404`, `text_not_present`,
     `value_mismatch`, `claim_overreach`, `source_kind_mismatch`)
     against fixture YAML + mocked WebFetch responses.
   - `pipeline/blurbs/test_run.py` -- integration test that mocks
     the five agent dispatches (researcher, verifier, writer,
     draft-fact-checker, style-editor) and walks a cycle from
     `release_landed` to `ready_for_user`, asserts state
     transitions and audit-log content. Includes a path where the
     verifier fails round 1, researcher revises, round 2 passes,
     and the cycle completes; and a path where round 3 escalates.

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
  each with full state history through `ready_for_user`
  (including a `claims_verified` event in the state_history) and
  an email-sent event in the audit log.
- The voice pre-check rejects a body containing "going forward"
  with a specific failure message naming the banned construction.
- The fact-checker helper, given a draft body containing `2.3%`
  and a fixture CSV with `2.3` as the latest value, returns a
  verified verdict; given `2.4%` against the same CSV, returns a
  contradicted verdict.
- `verify_claim_file()` given a fixture YAML with one
  `text_not_present` card and one passing card returns a
  `VerifyResult` with `passed_count=1, failed_count=1` and the
  failed `claim_id` listed.
- The integration test that exercises the round-1-fail / round-2-
  pass path advances the cycle to `ready_for_user` with
  `researcher_revision_count: 1` recorded on the artifact.
- The integration test that exercises the round-3 escalation path
  transitions the cycle to `escalated` and emits the escalation
  email with the failing claim-card YAML attached.
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
- 2026-05-11 (addendum 2): Insert `surface_fit_passed` state between
  `style_polished` and `user_review`. Wires Gate 3 of the canonical
  three-gate review protocol (`editorial/review_protocol.md`) into the
  auto-blurb state machine: editorial-director runs surface-fit
  review on the polished body and either PASSes the draft to the user
  inbox or REJECTs with a cut list that routes the cycle back to the
  writer. Re-run budget: 2 Gate 3 round-trips before escalation.
  Section 4.4a documents the verdict shape. Motivation: the upstream
  fact-check + style-polish gates do not ask "does this content
  belong on this surface" -- the same drift pattern that put lipsum
  and "tri-modal product" canon-jargon on the About page would recur
  in every blurb without Gate 3 in the cycle. editorial-director.
- 2026-05-11 (addendum): Insert `claims_verified` state between
  `context_drafted` and `writer_drafted`. Add claim-card schema
  (Section 1.2), verifier behavior and five-reason failure
  taxonomy (Section 1.3), researcher revision budget and
  post-writer fact-check distinction (Section 1.4). Fact-checker
  brief (Section 2.3) split into two modes: claims-verification
  upstream and draft-verification downstream, both dispatched as
  fresh agent runs to defend against LLM consistency bias. Phase 1
  backend brief (Section 9) gains `verify_claims.py` deliverable
  plus the `auto-blurb-verify-claims` skill file. Motivation: the
  Pillar A wave-4 "BoC rate 2.75%" failure (corrected in wave 5
  via primary-source re-fetch) proved chain-of-trust verification
  is not enough; the verifier must re-fetch and grep-match the
  source text. editorial-director.
