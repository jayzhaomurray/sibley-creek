# Review protocol — the three gates

Status: canonical. Authority: editorial-director (owns the protocol;
gate 3 is editorial-director's own work; gates 1 and 2 dispatch to
fact-checker and style-editor respectively).

---

## The rule

**Every piece of reader-facing prose written for Sibley Creek must pass
three independent review gates before it ships to a reader-visible
surface.** No exceptions for length. No exceptions for the surface
("it's just an About page" / "it's just a chart caption" / "it's just
a blurb"). No exceptions for the author ("it was written by a senior
agent / by me / from a verified insight base"). The gates apply to
draft prose, to blurb prose, to deep-dive prose, to institutional-page
prose, to inter-chart descriptive copy, to chart titles, to chart
captions, to figure callouts.

Reader-facing means: any text the visitor to sibleycreek.ca will see
on screen. NOT internal documentation, NOT code comments, NOT
verification reports, NOT insight bases — those are reviewer-facing
and have their own quality bar.

---

## The three gates

### Gate 1 — Fact check (fact-checker)

**Owner:** `fact-checker`. **Question:** Are the numeric and dated
claims true?

Verifies every number, every date, every cited source against primary
data (`data/site/sections.json`, `data/site/panel_data/*.json`,
`data/raw/*.csv`, BoC press releases, StatCan tables, IRCC announcements,
etc.). Numbers that don't match: fixed. Claims that can't be verified:
either re-anchored to a verifiable claim, or cut. A piece with one
unverified central number does not pass this gate.

### Gate 2 — Style polish (style-editor)

**Owner:** `style-editor`. **Question:** Is the prose at the
publication's voice + length discipline?

Applies the voice canon (`editorial/writing-style.md` Section 1 + Section
9 working notes proactively). Cuts hedging, kills "going forward" /
"interestingly," splits paragraphs at "but" / "however," push
argument-bearing clauses to the front, prefer verbs over nominalizations.
Concision: every word, sentence, paragraph must earn its place. When
uncertain, cut.

### Gate 3 — Surface fit (editorial-director)

**Owner:** `editorial-director`. **Question:** Does this content belong
on this surface, in this context?

The question no other gate asks. Voice doctrine doesn't belong in
reader-facing prose; cut. Internal canon-jargon ("chartbook unit",
"tri-modal product", "Big-Six competitors framing", "Mode 2") doesn't
belong in reader-facing prose; cut. Implementation detail ("the
pipeline LLM-drafts blurbs and human-reviews them") doesn't belong;
cut. Length appropriate to the surface (About page = scanned;
methodology page = read once; deep dive = read deeply; chart-pair
review surface = crisp short descriptions).

If a surface auto-fills with placeholder slots (the lipsum-in-template
pattern that produced 7 visible lorem ipsum blocks on the splash for
months), gate 3 cuts the slot. The Vignelli register's restraint
discipline applies: if it doesn't earn its place, it doesn't ship.

---

## Sequence and dispatch model

The gates run **in order**: fact-check → style-edit → surface-fit. A
failure at any gate stops promote-to-published until the gate passes.

When the dispatcher (main Claude) commissions reader-facing prose:

1. Brief writer / researcher (depending on which produces the prose).
2. On writer's draft output: dispatch fact-checker (Gate 1).
3. On fact-checker's verified output: dispatch style-editor (Gate 2).
4. On style-editor's polished output: dispatch editorial-director for
   surface-fit review (Gate 3). Editorial-director may cut sections
   wholesale, may demand re-scoping, may approve as-is.
5. Only after Gate 3 PASS: promote to `editorial/published/`, update
   `src/data/sections.ts` `publishedPath`, commit, push.

Gates can run in parallel only when explicitly compatible (gates 1 and
2 touch different aspects, but the convention is to run fact-check
first so style polish doesn't waste work on prose that gets factually
corrected anyway). Gate 3 is always last — editorial-director needs to
see the polished prose to judge surface fit.

---

## What this protocol fixes

Drift before the protocol existed:
- Splash panels rendered 7 lipsum blocks because no gate asked "does
  the surface need this slot at all?"
- About page shipped with internal canon-jargon ("tri-modal product",
  "chartbook unit", "Big-Six competitors") because no gate asked
  "does this voice doctrine belong on reader-facing About prose?"
- Chart-pair review surfaces auto-generated verbose inter-chart copy
  because no gate asked "is this length appropriate for a review
  surface the user will delete most of tomorrow?"
- Pillar A v3 shipped with a "Byline: [author TK]" placeholder
  because no gate flagged user-visible TK.

The protocol makes these failures impossible to ship if it runs.

---

## Practical enforcement

This is process discipline, not a literal Claude Code hook. There is
no automated PostToolUse hook that catches reader-facing prose writes
and dispatches reviewers. Enforcement is the dispatcher's
responsibility (main Claude) and the editorial-director's
responsibility (the role that owns the protocol).

When you (any agent or main Claude) catch yourself about to push
reader-facing prose without all three gates having run, STOP. Run
the gates first.

When the user catches reader-facing prose on the live site that should
have been gated, the immediate action is: cut it, codify why the gate
missed it, redispatch with the gate in place.

---

## Source-currency — how stale citations get caught

Pipeline-backed series (StatCan tables via API, BoC Valet, FRED) auto-
refresh through the daily pipeline run; stale series surface as
pipeline errors or as visible "not wired" states on the site.

PDF/HTML publications (BoC MPR, FOMC statements, BoC inflation mandate,
IRCC plans, IMF Article IV, OECD Economic Survey, BoC neutral-rate
Appendix) do NOT auto-refresh. The publication on the BoC site moves
forward, our prose stays anchored to the old vintage, and a claim that
was true yesterday is editorially out of register today.

**The registry:** `editorial/source_cards/registry.yaml` lists every
PDF/HTML publication cited in reader-facing prose or as a chart
constant. Schema and example entries are in the file. Required fields
include `url`, `verified_value`, `verified_at`, `next_expected`,
`cadence`, and `cited_in`.

**The cron:** `.github/workflows/source-currency-check.yml` runs the
registry probe weekly. `scripts/check_sources.mjs` fetches each
`currency_probe_url`, flags `PAST-DUE` entries (where `next_expected`
has passed) and `NEWER-VINTAGE-MAYBE` entries (where the probe response
contains dates newer than `verified_at`). Failing the workflow on
PAST-DUE makes the staleness visible in the Actions tab.

**On demand:** the `/check-sources` skill runs the same probe locally
and surfaces the punch list. Used between cron runs when a new vintage
is known to have shipped (e.g., a fresh MPR just dropped) and the user
wants to verify everything currently cited is current.

**The discipline:** when a redraft pass references any registry entry,
the fact-checker's brief includes "verify the registry entry's value
against the cited URL is still the current published value." This
extends the Redraft Re-gating rule below to source-currency, not just
pipeline data. When researcher dispatch confirms a new vintage exists,
the researcher updates the registry entry (new `url`,
`verified_value`, `verified_at`, `vintage_label`, `next_expected`) and
flags any prose surfaces that need rewording.

The registry plus the cron close the silent-staleness loop. The
discipline depends on actually opening and acting on the cron's output
on the weeks publications ship.

---

## Redraft re-gating — the rule that closes the most common leak

**Any new claim introduced during a redraft re-enters Gate 1.** No
exceptions. If the writer rewrites a blurb in response to a style
audit, or adds editorial context to fill a methodology cut, or
introduces a forward-looking framing line — every new numeric,
dated, or countable claim in the new text gets fact-checked before
the redraft is applied to the live page.

This is the most common way reader-facing claims slip through:

1. Initial fact-check passes on draft A (verified numbers).
2. Style audit flags draft A for voice issues.
3. Writer rewrites to draft B, introducing new numbers / counts /
   "first since" / "Nth consecutive" claims to replace cut prose.
4. Dispatcher applies draft B to the live page WITHOUT re-checking
   the new claims — assumes the original Gate 1 covered them.
5. Wrong number ships.

The fix: after every writer redraft, dispatch fact-checker scoped to
the **delta between draft A and draft B**. The fact-checker brief
names the specific new claims (e.g., "verify the '3-mo average
negative since late-2024 stall' claim by enumeration"; "verify
'spread negative for nearly two years' by walking the series back
from latest"). PASS → apply. FAIL → fix the claim and re-check.

This rule applies to:
- `/refresh-blurbs` redraft passes (writer rewrites failing surfaces).
- Auto-blurb pipeline redrafts after the verifier flags a claim card.
- Any one-off writer dispatch where the writer adds prose beyond what
  the source claim-cards directly carry.
- Deep-dive revision cycles where new sub-claims appear in revision.

A writer's redraft is not "trusted because the writer already had the
verified inputs." The writer's job is prose; verification is the
fact-checker's. The gate runs every time new claims appear.
