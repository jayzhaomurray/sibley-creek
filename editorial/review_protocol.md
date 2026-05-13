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

## Authorship is not a gate exemption — user-written prose follows the same rules

**The author of a piece of prose does not change whether it gets fact-
checked.** Whether the prose was drafted by an LLM agent, edited by a
human in a chat redraft, hand-typed directly into the source file, or
pasted in from somewhere else — every numeric, dated, or countable
claim must be tagged with a citation, and the citation must be
verifiable against its source.

The build-time citation gate (`scripts/check_citation_coverage.mjs`)
treats every reader-facing prose surface identically. A surface with
citable tokens but no `citations[]` array fails the build, regardless
of who wrote the prose. The gate doesn't read authorship; it reads
prose and citations.

The principle, from the user: *"I am not above AI. I am equally at
risk of writing something incorrect."* Authorship-blind enforcement is
how we protect the publication's credibility against author errors —
including the user's own.

When the user (or any human) edits a section page, section abstract,
deep-dive markdown, splash hero, or tile line and introduces a new
number, date, or countable claim:

1. The change must include a corresponding `citations[]` entry (for
   inline plate/section/tile surfaces) or sidecar YAML entry (for
   research deep dives).
2. On `npm run build`, the gate runs first. Uncovered tokens fail the
   build. Nothing reaches the live site without passing this gate.
3. The redraft re-gating rule (below) also applies — new claims
   re-enter Gate 1 (fact-check) regardless of authorship.

This is non-bypassable by design. Convention is too easy to forget; a
build-time check that refuses to ship uncovered prose is the only
durable enforcement.

---

## Registered-source rule — every citation must resolve to a known source

**Every `source:` field on a citation must be one of three types:**

1. `pipeline:<provider>:<key>` — the value flows through the data
   pipeline and refreshes on a known cadence. The pipeline-source
   resolver maps to a clickable upstream page (StatCan tableViewer,
   BoC Valet series page, FRED, etc.).
2. `card:<id>` — the claim points at a registered source card in
   `editorial/source_cards/registry.yaml`. Each card carries `url`,
   verbatim `excerpt`, `verified_at`, `next_expected`, and the surfaces
   it's cited in.
3. `derived` — the value is arithmetic from other tagged claims on the
   same surface (e.g. "X% minus Y% = Zpp"). The note must show the
   derivation.

`other:<freeform note>` is NOT acceptable. The previous practice of
inlining a freeform source description in the citation note was the
easy escape valve for sources that should have been registered. The
result: ~136 claims on the site pointed at sources that no automated
freshness check or click-through verification could touch.

Migrating an `other:` citation requires one of:

- **Promote to `card:`** — add an entry to `registry.yaml` with the
  url, the verbatim excerpt that contains the cited claim, the date
  you verified it, and when you expect the source to publish a new
  version. Then change the citation's source to `card:<id>`.
- **Replace with `pipeline:`** — if the underlying number lives in
  the data pipeline, tag it with the appropriate `pipeline:<prov>:<key>`
  and drop the freeform note.
- **Replace with `derived`** — if the claim is arithmetic from other
  tagged claims, show the math in the note and tag as `derived`.

The build-time gate refuses `other:` sources. The audit pages flag
any that slip through.

---

## Tiered verification — every card has an explicit epistemic status

**Every card in `editorial/source_cards/registry.yaml` carries a
`verification_tier` field that records how the claim's verification
chain closes.**

The publication's positioning rests on a simple promise: every fact
on the site is verifiable by the reader. AI may draft, AI may
triangulate, AI may surface candidates. What counts as fact on the
site is approved by the user (jzm). The tier system encodes that
discipline.

### The four tiers

**Tier A — Primary verified.** The researcher fetched the primary
source, extracted the verbatim excerpt that contains the cited
value, and captured it on the card. No triangulation needed. The
reader can click the card's URL, find the verbatim excerpt at the
expected location, and confirm the number matches. AI may ship
Tier A cards without explicit user approval.

**Tier B — Triangulated secondary.** Primary unreachable to
WebFetch (typically WAF blocks, PDF binaries, JS-rendered pages).
Two or more independent credible secondaries from the allowlist
in `editorial/credible_secondaries.md` reproduce the claim with
consistent wording. Card carries the would-be primary URL, the
triangulation block (each secondary with verbatim excerpt and
credibility statement), and requires `user_confirmed_at` +
`user_confirmed_by` before shipping. Build-time gate refuses any
Tier B card without those fields filled.

**Tier C — Single credible secondary.** Primary unreachable; only
one credible secondary reproduces the claim, or two converge on
the number without verbatim agreement. Card requires explicit
user approval AND a justification field describing why the
single-secondary trail is sufficient. Used sparingly; most cases
that would qualify for Tier C should either find a second secondary
(promote to Tier B) or be cut (drop to Tier D).

**Tier D — Below the bar.** Claim cannot be sourced under the
above rules. **The claim does not ship.** Softening the language
is not a substitute — Tier D claims are cut entirely from prose,
or the user explicitly provides the verification (which promotes
the card to Tier A or B). No third path.

### What independent triangulation means

Two secondaries are *independent* when they have different
institutional affiliations and different revenue/incentive
structures. A Reuters story republished across ten outlets is one
secondary, not ten. A government source plus a major news outlet
quoting that government source are not independent — they're the
same chain. A law firm's client alert plus a different law firm's
client alert ARE independent (different institutions, different
liability structures).

For numeric or dated facts, two independent credible secondaries
are required. For direct quotations, two independent OR one
official mirror (BIS Review, government transcript archive). For
regulatory or treaty text, one government secondary suffices (the
text is legally fixed and reproducible). For historical claims
(pre-2010), more flexibility is allowed since the fact has been
re-reproduced widely.

### The pending queue

When a researcher drafts a Tier B or Tier C card, it lands in
`editorial/source_cards/_pending/<surface>/<id>.yaml`, NOT in the
live registry. The writer's draft uses a `[CLAIM-PENDING:<id>]`
placeholder in `editorial/drafts/_holding/<slug>.md`, and the
surrounding prose is written without the claim — either cut from
the draft entirely or held with a placeholder until approval.

The audit infrastructure surfaces pending cards through a
verification view at `editorial/source_cards/audit/_verify/<draft-slug>.html`,
linked from the master audit index at
`editorial/source_cards/audit/index.html`. The user walks each
pending card: opens the secondaries, attempts the primary in a
browser, then approves or rejects. Approval flips the card to the
live registry with `user_confirmed_at` filled and triggers a
splice pass that replaces the holding draft's `[CLAIM-PENDING:<id>]`
markers with the verified claim text. Rejection deletes the card
and marks the draft placeholder as cut.

### Mechanical fact corrections auto-apply (no user approval required)

A fact-check that surfaces a **mechanical** correction — wrong numeric
value vs the underlying data, wrong date, drifted StatCan / Valet
table ID, stale vintage label, arithmetic error in a derived claim,
typo in an enumeration — applies automatically during /refresh-blurbs
and equivalent workflows. The agent fixes it; the user does not need
to approve each one.

Mechanical = the correction is unambiguous and editorially neutral:
the right value is what the primary data shows, and there is no
editorial judgment about which framing to use.

**Examples that auto-apply:**
- "Headline CPI 2.4% in March" when StatCan shows 2.3% → fix.
- "$330bn peak in 2021-22" when raw series shows $394bn in March 2021
  → fix to "$394bn peak in March 2021" or "near $400bn peak."
- "FAD enumeration: Jan 29, Mar 12, Apr 16, Apr 29" when calendar is
  Dec 10, Jan 28, Mar 18, Apr 29 → fix the dates.
- "0.5-point jump from 1.8% to 2.3%" when prose says 0.4-point → fix
  the arithmetic.

**Examples that DO need user veto** (editorial judgment, not mechanical):
- Framing decisions: "restrictive" vs "at neutral floor" — different
  defensible reads, the user picks the framework.
- Take selection: "widest since 1996-97" vs "second-deepest after
  1996-97" — voice-canon defaults apply (true superlative per §4.1h),
  but the user can override.
- Cuts that remove an editorial argument: if the only way to fix a
  claim is to drop the take it supports, that's an editorial decision.
- New citations introducing a new card or pipeline slot — the user
  reviews the source.

The /refresh-blurbs loop applies mechanical corrections inline; the
final report lists them so the user can see what changed but does not
require pre-approval. Editorial-judgment items get surfaced for veto
before the redraft proceeds.

### Mode 3 — Analysis citations require user approval

A separate path from Tier A/B/C is the **analysis citation** mode
documented in `editorial/writing-style.md` §8c. When the editorial
point is what a third-party (typically a bank economics desk)
argued, not what is true, the citation appears as Mode 3. Mode 3
cards carry `mode: 3` and require `user_approved_at` +
`user_approved_by` before shipping, with the same pending-queue
mechanics as Tier B/C.

The frame test for Mode 3: replace "X argues Y" with "Y is true."
If the sentence still works, the framing is honest analysis
citation. If the editorial punch evaporates when you add "X
argues," the claim is being smuggled in as fact when it isn't —
reframe or cut.

### Bank economics desks are not credible secondaries

Bank economics desks are competitors, not fact-reproducers. They
do NOT count as credible secondaries for Tier B or C
triangulation. A bank desk repeating a BoC press release does not
add a verification chain — the primary is the same, and citing
the desk implies an authority we should not lend competitors.

Bank desks may appear in two narrow modes: aggregated into
consensus framing (Mode 2 in writing-style.md §8c), or as
the subject of Mode 3 analysis citations. Both require explicit
discipline; the default is not to cite them.

See `editorial/credible_secondaries.md` for the full allowlist
and exclusions.

### How the gate enforces the tier system

The build-time gate (`scripts/check_citation_coverage.mjs`):

- Refuses any `source:` value that isn't `pipeline:<provider>:<key>`,
  `card:<id>`, or `derived`.
- Refuses any `card:<id>` whose registry entry has
  `verification_tier: "B"` (or higher) AND empty `user_confirmed_at`.
- Refuses any `card:<id>` whose YAML file lives in
  `editorial/source_cards/_pending/` rather than the live
  `registry.yaml`.
- Refuses any Mode 3 card without `user_approved_at` filled.

The build runs the gate after audit-page regeneration. The audit
pages render verification-tier badges on every claim so a reader
of the audit can see the epistemic chain on every fact.

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
