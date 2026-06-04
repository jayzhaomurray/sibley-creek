# Fiscal section lede — Gate-3 surface-fit touch (2026-06-04)

Surface: fiscal section `blurb.body` (src/data/sections.ts ~line 558). Serves as both
the fiscal page lede and the overview-page fiscal panel blurb.
Register: take-driven section abstract. Canon §4.1f-2, §4.1g, take-mechanism-land.

This is a TOUCH, not a rewrite. Only the operating-surplus sentence changes; every
other claim stays verbatim and inherits its 2026-06-02 gate passage.

---

## Amended blurb (body)

The fiscal stance is mildly expansionary and stays in deficit through the decade—the gap narrows because program spending is held below GDP growth, not because revenue rises. Ottawa's own plan reaches an operating surplus by 2028-29, but only by its own definition of what counts as capital rather than day-to-day spending[CLAIM-PENDING:dof_vs_pbo_operating_capital_dispute]; record bond issuance funds the difference. Federal debt holds near 41% of GDP through the forecast—well below the 66.6% of the mid-1990s, elevated against the past decade.

---

## What changed (one-line diff)

Replaced "by 2028-29 while booking capital investment separately as debt" with
"by 2028-29, but only by its own definition of what counts as capital rather than
day-to-day spending[CLAIM-PENDING:...]" — turns the flat assertion into a
contested-definition signal so the lede no longer contradicts the DoF-vs-PBO plate.

---

## Word count

- Current: 78 words.
- Amended (placeholder counted as zero, prose stands without it): 81 words. +3, within ±15.
- The dropped clause "while booking capital investment separately as debt" was the
  mechanism the new plate now carries in full; the lede no longer needs to pre-empt it.

---

## Honesty notes (placeholder + verification)

- The qualifier "only by its own definition of what counts as capital rather than
  day-to-day spending" is grounded in the ALREADY-VERIFIED card
  `dof_operating_balance_projection` (citation note, line 562 of sections.ts:
  "meeting the stated fiscal anchor under DoF's own definition"). It is the DoF
  series' own qualifier surfaced in prose, not a new claim. No new countable claim.
- The `[CLAIM-PENDING:dof_vs_pbo_operating_capital_dispute]` placeholder reserves the
  PBO attribution — that the Parliamentary Budget Officer, on a narrower capital
  definition, reads the operating books as never reaching balance. That is the
  contested-definition view and lives in the pending card; it splices in on approval.
- Prose stands WITHOUT the placeholder: "only by its own definition of what counts
  as capital" already carries the contest. The splice adds the named counterparty.
- Frame test honoured: no "misclassifying" stated as fact; no same-year DoF-minus-PBO
  delta. The sentence asserts only that the surplus depends on DoF's own definition —
  verified and defensible.

---

## abstractCitations — note for the splice/build pass

The existing citation for "reaches an operating surplus by 2028-29"
(card:dof_operating_balance_projection) still covers the verified spine of the
sentence. The dropped phrase "booking capital investment separately as debt" had no
dedicated citation entry, so no citation needs removing. When the PBO card is
approved, the splice should add a `card:dof_vs_pbo_operating_capital_dispute` citation
for the spliced PBO clause.

---

## NEW CLAIMS INTRODUCED

- None that are countable/numeric. The amended verified prose ("only by its own
  definition of what counts as capital rather than day-to-day spending") restates the
  existing verified DoF-definition qualifier; it introduces no new number, date, or
  count. Gate-1 re-check: confirm the qualifier is faithful to the
  `dof_operating_balance_projection` citation note ("under DoF's own definition").
- The PBO-attribution content is held behind the pending-card placeholder and
  re-enters its own gate on approval, not in this redraft.

---

## Round 2 — plate-4 + lede EFO attribution (2026-06-04)

Trigger: PBO Economic and Fiscal Outlook – June 2026 (RP-2627-002-S), released
2026-06-04. The chart on plate-4 plots the DoF Fiscal Reference Tables + Spring
Economic Update track, which is flat. Stating "the trajectory is flat" without
attribution now presents the *government's* plan as settled fact; the fiscal
watchdog, as of today, reads the ratio drifting up. Both touches attribute the
flat track to Ottawa's plan and land the PBO drift as the counterpoint. The
historical reading (66.6% mid-90s peak, 28% pre-crisis low, 47% pandemic, ~41%
now) survives verbatim and keeps its prior gate passage.

---

### Job 1 — plate-4 title + interpretation

**Title (amended):**

> Federal debt has stabilized near 41% of GDP—but the path past the mid-1990s peak forks ahead.

**Interpretation (amended, 92 words):**

> Canada's federal debt ratio is elevated but stable—far below its mid-1990s extreme. The pandemic pushed it to 47% in 2020-21, well under the 66.6% peak of the mid-1990s that two decades of consolidation had cut to a pre-crisis low of 28%. Dollar debt keeps climbing past $1.6 trillion; whether the ratio holds depends on whose forecast you take. Ottawa's plan keeps it flat near 41% through the decade. The Parliamentary Budget Officer, costing the same books in June, sees it drifting up to 42.5% by 2030-31.

**What changed (plate-4 diff):**

- Title: dropped "far below its mid-1990s peak" tail, replaced with
  "—but the path past the mid-1990s peak forks ahead." Keeps the verified
  stabilized-vs-peak historical claim; the new clause flags that the *forward*
  path is contested, not settled. Terminal period, sentence-form, one finding.
- Interpretation: the historical spine (47% pandemic / 66.6% peak / 28% low)
  is preserved verbatim in substance. The old closing "The level is elevated;
  the trajectory is flat" asserted flatness as fact—now cut. Replaced with the
  attribution fork: "whether the ratio holds depends on whose forecast you take,"
  then Ottawa's flat-near-41% plan, then the PBO's 42.5%-by-2030-31 drift as the
  counterpoint. Take-mechanism-land: take (elevated-but-stable, contested
  forward) → mechanism (dollar debt climbs; ratio depends on the forecast) →
  land (the two forecasts fork). 92 words, within the ≤95 budget.
- `source` line on the plate should add the PBO EFO citation alongside the
  existing DoF sources (build/splice note below).

---

### Job 2 — fiscal section blurb, second touch

This stacks on the Round-1 amended blurb (operating-surplus sentence with the
`[CLAIM-PENDING:...]` placeholder). Only the final debt sentence changes.

**Amended blurb (body), full text:**

> The fiscal stance is mildly expansionary and stays in deficit through the decade—the gap narrows because program spending is held below GDP growth, not because revenue rises. Ottawa's own plan reaches an operating surplus by 2028-29, but only by its own definition of what counts as capital rather than day-to-day spending[CLAIM-PENDING:dof_vs_pbo_operating_capital_dispute]; record bond issuance funds the difference. Ottawa's plan holds federal debt near 41% of GDP through the forecast—well below the 66.6% of the mid-1990s; the Parliamentary Budget Officer sees it drifting to 42.5% by 2030-31.

**What changed (lede diff):**

- Old final sentence: "Federal debt holds near 41% of GDP through the
  forecast—well below the 66.6% of the mid-1990s, elevated against the past decade."
- New final sentence: "Ottawa's plan holds federal debt near 41% of GDP through
  the forecast—well below the 66.6% of the mid-1990s; the Parliamentary Budget
  Officer sees it drifting to 42.5% by 2030-31."
- The flat-41% claim is now explicitly Ottawa's plan, not a free-standing fact.
  The PBO drift lands as compact contrast. Dropped "elevated against the past
  decade" to make room (the historical contrast survives via the 66.6% anchor).

**Word count (lede):**

- Round-1 touched version: 81 words (placeholder counted as zero).
- Round-2 amended: 84 words (placeholder counted as zero). +3 vs Round-1,
  within ±15 of the current-touched version.

---

### abstractCitations — build/splice note (Round 2)

- The existing `pipeline:fiscal:panel-9` citation for "Federal debt holds near
  41% of GDP" still covers "Ottawa's plan holds federal debt near 41% of GDP
  through the forecast" and "well below the 66.6% of the mid-1990s" (both DoF/FRT
  series). The phrase binding should update from "Federal debt holds near 41% of
  GDP" to "Ottawa's plan holds federal debt near 41% of GDP."
- A NEW citation entry is needed for the PBO drift clause on BOTH surfaces:
  `{ phrase: "drifting to 42.5% by 2030-31", source: "card:pbo_efo_june2026_debt_gdp",
  note: "PBO Economic and Fiscal Outlook – June 2026 (RP-2627-002-S): federal
  debt-to-GDP 41.3% in FY2025-26 rising to 42.5% by FY2030-31." }`. The card must
  be created from the dispatcher-fetched primary before this splices live.
- Plate-4 `source` line: append "Parliamentary Budget Officer, Economic and
  Fiscal Outlook – June 2026 (RP-2627-002-S)." to the existing DoF source string.

---

### Frame test (Round 2)

- "The Parliamentary Budget Officer sees it drifting to 42.5% by 2030-31" — apply
  the frame test by deleting the attribution: "it drifts to 42.5% by 2030-31"
  would assert the PBO projection as settled fact, contradicting Ottawa's flat
  track. The attribution is essential and honest; the clause must keep "the
  Parliamentary Budget Officer sees." Mode-3-style named attribution, correct here
  because two credible forecasts genuinely diverge and the plate/lede surfaces the
  divergence rather than picking a winner.
- The June EFO does NOT update PBO's operating/capital recast (still the Nov 2025
  analysis); neither touch claims it does. The operating-surplus dispute stays
  behind its own pending card—not conflated with the debt-ratio drift.

---

### NEW CLAIMS INTRODUCED (Round 2 — for Gate 1)

All three carry the dispatcher-fetched primary citation: **Parliamentary Budget
Officer, Economic and Fiscal Outlook – June 2026, RP-2627-002-S.**

- **[PRIMARY-CITED]** PBO projects federal debt-to-GDP rising to **42.5% by
  2030-31** (FY2030-31). Lands on both plate-4 interpretation and the lede.
- **[PRIMARY-CITED]** PBO's FY2025-26 federal debt-to-GDP starting point is
  **41.3%** (used in plate-4 interpretation only as context for the "drifting up"
  framing; the 42.5% endpoint is the countable claim that ships).
- **Re-confirm (already verified, prior gate):** plate-4 historical anchors —
  47% pandemic (2020-21), 66.6% mid-1990s peak, 28% pre-crisis low, ~41% now —
  and lede "near 41% through the forecast" / "66.6% of the mid-1990s." These are
  unchanged in substance; flag only because surrounding prose moved.
- **Attribution reframe (not a new number):** "flat near 41%" / "holds federal
  debt near 41%" is now attributed to *Ottawa's plan*. No new value; verify the
  attribution is faithful (the flat track is the DoF FRT + SEU series the chart
  plots).
- The deficit figures from the June EFO ($72.0bn / 2.2% of GDP for 2025-26;
  $4.6bn/yr average above the SEU track; DoF's $66.9bn) are NOT used in either
  touch—reserved, not introduced. No Gate-1 obligation on them here.

---

## Surface fit round 2 (Gate 3 — plate-4 + lede EFO attribution)

Scope: ONLY the "## Round 2 — plate-4 + lede EFO attribution" section. Round-1 verdicts (lede-needs-touch, operating-surplus contested signal) stand.

**Plate-4 title (after): PASS.** "Federal debt has stabilized near 41% of GDP—but the path past the mid-1990s peak forks ahead." Reader-facing finding, terminal period, one verb-driven idea. "Forks ahead" honestly signals contestation without naming a winner. Belongs on this surface.

**Plate-4 interpretation (after): PASS.** Take-mechanism-land holds; named PBO attribution is correct on a chartbook plate because two credible forecasts genuinely diverge and the plate surfaces the divergence rather than picking one. No doctrine, no jargon. The "whose forecast you take" pivot is editorial framing, not process-talk. Good on this surface.

**Question (2) — is "Ottawa flat ~41% vs PBO 42.5%" the right amount of repetition across lede and plate? PASS as drafted, with the division handled correctly.** The two surfaces carry the SAME contrast but at different resolution, and that is the right call, not redundancy:

- The PLATE argues it: full mechanism (dollar debt climbs past $1.6T; ratio depends on the forecast; Ottawa flat; PBO 42.5% by 2030-31 costing "the same books in June"). The plate earns the detail because the chart is right there and the reader is reading deeply.
- The LEDE synthesizes it: one compact clause ("the Parliamentary Budget Officer sees it drifting to 42.5% by 2030-31"), no $1.6T, no "same books," no starting-point 41.3%. That is synthesis, not a second argument.

This matches canon: the section abstract states the contest; the plate carries the WHY. The 42.5% number appearing on both is acceptable — it is the single anchor of the contrast, and a lede that gestured at "the watchdog disagrees" without the number would be weaker, not cleaner. PASS. No cut.

**Question (3) — does the lede now over-carry TWO contested signals and become a dispute inventory? NO — it stays a section abstract, but it is at its ceiling. PASS, with a sequencing call.**

The lede now carries: (a) operating-surplus definitional dispute [CLAIM-PENDING], and (b) debt-trajectory dispute (Ottawa vs PBO 42.5%). Read whole, it still scans as a take-driven abstract because the two disputes are NOT parallel inventory items — they sit at different points of one argument:

- Sentence 2 (operating surplus) is about whether the deficit narrowing is *real*.
- Sentence 3 (debt trajectory) is about whether the resulting *level holds*.

That is a narrowing→holding progression, the same spine as the plate sequence — so it reads as one descending argument, not a list of two grievances. The mechanism sentence ("the gap narrows because program spending is held below GDP growth") still leads, so the abstract opens on a TAKE, not on a dispute.

BUT it is full. Both contested signals can stay ONLY because each is one subordinate clause, not a sentence. Guardrail for the wiring pass: if either dispute later wants more than a single clause in the lede, the operating-surplus signal yields first and the plates carry it alone — the operating-surplus dispute is the more definitional/inside-baseball of the two, and plate-2 already argues it in full. The debt-trajectory contrast is the one the lede must keep, because it is the cleaner, more legible "two credible forecasters disagree on the headline number" signal and it pairs with the most-scanned figure on the page (the debt ratio). So: **both stay now; if pressure comes, lede keeps the debt-trajectory dispute, plates keep the operating-surplus dispute alone.**

**One CUT — flagged, mechanical, for the wiring pass (not blocking).** The lede's `[CLAIM-PENDING:dof_vs_pbo_operating_capital_dispute]` placeholder must NOT ship visible. Per the no-TK rule, if the PBO operating/capital card is not approved and spliced by publish time, the operating-surplus sentence ships on its prose alone ("only by its own definition of what counts as capital rather than day-to-day spending" — which the draft confirms stands without the placeholder, line 47-48), and the placeholder token is deleted, not rendered. Confirm at wiring: no bracketed token reaches the reader surface.

**Both round-2 touches ship as drafted. No surface-fit cut to prose. Two wiring-pass guardrails: (1) delete the [CLAIM-PENDING] token if its card isn't live by publish; (2) if dispute-signal pressure grows later, lede keeps debt-trajectory, plates keep operating-surplus.**

---

## Style pass round 2 — plate-4 title + interpretation + lede

### Plate-4 title

**Before:**
Federal debt has stabilized near 41% of GDP—but the path past the mid-1990s peak forks ahead.

**After:**
Federal debt has stabilized near 41% of GDP, but Ottawa and the PBO see different paths forward.

Word count (after): 17. Within hard cap (18). Terminal period: PASS.

Notes: "the path past the mid-1990s peak forks ahead" failed on two counts. "Past the mid-1990s peak" implies the ratio is currently beyond the peak — it is far below it, so the phrase misdirects. And "forks ahead" is strained as a title verb; the reader cannot tell what is forking or why. The title's actual finding is that two credible forecasts diverge from here. Named attribution ("Ottawa and the PBO") is exact and gives the reader the fork's meaning immediately. The em-dash replaced with a comma — the clause does not interrupt the subject; it continues it. Structural edit on the tail clause; the opener is unchanged. Routes to writer for veto on named-attribution form.

### Plate-4 interpretation

**Before:**
Canada's federal debt ratio is elevated but stable—far below its mid-1990s extreme. The pandemic pushed it to 47% in 2020-21, well under the 66.6% peak of the mid-1990s that two decades of consolidation had cut to a pre-crisis low of 28%. Dollar debt keeps climbing past $1.6 trillion; whether the ratio holds depends on whose forecast you take. Ottawa's plan keeps it flat near 41% through the decade. The Parliamentary Budget Officer, costing the same books in June, sees it drifting up to 42.5% by 2030-31.

**After:**
Canada's federal debt ratio is elevated but stable—far below its mid-1990s extreme. The pandemic pushed it to 47% in 2020-21, well under the 66.6% peak that two decades of consolidation had cut to a pre-crisis low of 28%. Dollar debt keeps climbing past $1.6 trillion; whether the ratio holds depends on whose forecast you take. Ottawa's plan keeps it flat near 41% through the decade. The Parliamentary Budget Officer, costing the same books in June, sees it drifting to 42.5% by 2030-31.

Word count (after): 89 words, 5 sentences. Budget: 40-70 target, 95 cap. Within cap; above target. NOTE: 89 words reflects the structural need to carry both attributions. If one sentence can be merged on a future pass without losing either attribution, do it — but do not cut either the Ottawa flat-track or the PBO projection.

Notes: "of the mid-1990s" in sentence 2 appeared twice in one sentence — the first reference establishes it; the second is redundant. Cut from "the 66.6% peak of the mid-1990s" to "the 66.6% peak." "Drifting up" reduced to "drifting" — the direction is established by the contrast structure ("flat" vs "drifting to 42.5%"); "up" is redundant. Both mechanical cuts; no structural change.

### Lede final sentence

**Before:**
Ottawa's plan holds federal debt near 41% of GDP through the forecast—well below the 66.6% of the mid-1990s; the Parliamentary Budget Officer sees it drifting to 42.5% by 2030-31.

**After:**
Ottawa's plan holds federal debt near 41% of GDP—well below the 66.6% of the mid-1990s. The Parliamentary Budget Officer sees it drifting to 42.5% by 2030-31.

Notes: the em-dash-plus-semicolon chain loaded three claims into one sentence (Ottawa's flat track, historical anchor, PBO contrast), which compressed the PBO attribution into a subordinate position. The PBO contrast is the editorial point; it needs its own sentence. "Through the forecast" cut — the phrase is implicit in "Ottawa's plan" framing; "holds near 41% of GDP" is already a forward-looking claim and "through the forecast" added no precision. Three words saved; the 66.6% anchor moves to an em-dash aside on the Ottawa sentence, matching the plate's handling. Attribution structure unchanged.

**Full lede (after), word count:**
The fiscal stance is mildly expansionary and stays in deficit through the decade—the gap narrows because program spending is held below GDP growth, not because revenue rises. Ottawa's own plan reaches an operating surplus by 2028-29, but only by its own definition of what counts as capital rather than day-to-day spending[CLAIM-PENDING:dof_vs_pbo_operating_capital_dispute]; record bond issuance funds the difference. Ottawa's plan holds federal debt near 41% of GDP—well below the 66.6% of the mid-1990s. The Parliamentary Budget Officer sees it drifting to 42.5% by 2030-31.

Word count (after, placeholder counted as zero): 83 words, 4 sentences. Section-abstract budget: 2-3 sentences / 45-75 target / 90 cap. NOTE: 4 sentences and 83 words are over the standard section-abstract budget. Escalation to writer: the debt paragraph requires two sentences to carry both attributions honestly. Consider merging the operating-surplus sentence and the bond-issuance sentence to recover one sentence slot — that would bring the count to 3 sentences and approximately 71 words (just over target), which is defensible given the content load. Do not cut either attribution.

---

## Gate 1 round 2 — verdicts (plate-4 + lede EFO attribution, 2026-06-04)

Verified against the POST-STYLE "after" copy: plate-4 title line 244, plate-4
interpretation line 256, lede line 273. PBO numbers checked against the source card
`editorial/source_cards/_pending/fiscal/pbo_efo_june2026_debt_gdp.yaml` (source of
record per brief; no network in sandbox). Historical spine + DoF flat track checked
against `data/derived/frt_federal_debt_pct_gdp.csv` (fiscal.json panel-9).

**OVERALL: PASS WITH ONE FLAG.** All PBO numbers, attribution structure, historical
anchors, and the DoF-vs-PBO non-conflation verify. One framing flag on "two decades of
consolidation" (~13 years peak-to-trough); not a fail, writer's call.

**PBO numbers (card = source of record):**
- **"42.5% by 2030-31" — PASS.** Card `debt_to_gdp_pct_2030_31: 42.5`; excerpt verbatim
  "rising to 42.5 per cent by 2030-31." Tier A, triangulated Globe + BNN. Lands on
  plate-4 interpretation (line 256) and lede (line 273). Verified.
- **"41.3% in FY2025-26" (PBO start) — PASS.** Card `debt_to_gdp_pct_2025_26: 41.3`;
  excerpt verbatim. Context only; not a standalone shipped countable claim. Verified.
- Citation "Parliamentary Budget Officer, Economic and Fiscal Outlook – June 2026,
  RP-2627-002-S" — **PASS.** Matches card id/title/url; source_kind correct (PBO EFO).

**Attribution structure — PASS.**
- Flat-near-41% attributed to "Ottawa's plan" → DoF FRT+SEU track. Panel-9 DoF series:
  FY2025-26 41.1% → FY2030-31 41.6% (flat near 41%). Reframe from round-1's
  free-standing "Federal debt holds near 41%" to "Ottawa's plan holds federal debt near
  41%" is faithful. Verified.
- PBO drift to 42.5% attributed to PBO. Correct.
- **Non-conflation with the Nov 2025 operating/capital recast — PASS.** Card scope note
  (lines 33-38): June EFO does NOT update the recast (RP-2526-017-S, Nov 14 2025 remains
  PBO's classification position). Draft frame test (lines 174-176) confirms neither
  touch claims it does. Operating-surplus dispute stays behind its own pending card.
  Nothing conflated.

**Plate-4 historical spine vs panel-9 — PASS.**
- 66.6% peak FY1995-96 — CSV 66.6 at 1995-96, series max. Verified.
- 28% low — CSV pre-GFC trough 28.2% (FY2008-09); panel-9 notes confirm. Fair round.
- 47% pandemic (2020-21) — CSV 47.2%; panel-9 notes confirm. Fair round.
- ~41% now — CSV FY2024-25 41.2%, FY2025-26 41.1%. Verified.

**FRAMING / DIRECTION CHECK — PASS.** Post-style plate-4 title (line 244): "Federal debt
has stabilized near 41% of GDP, but Ottawa and the PBO see different paths forward."
DoF track is flat ~41-42% ("stabilized" ✓); the DoF-vs-PBO divergence (41.6% DoF vs
42.5% PBO by FY2030-31) is genuine ("different paths forward" ✓). The style pass's fix
of the old "past the mid-1990s peak forks ahead" tail is an improvement — the old phrase
could misread as "ratio is now beyond the peak" (it is far below). Named attribution
defuses the round-1 inversion-class risk (no single forecast asserted as settled).
Direction matches trajectory.

**FLAG (not a fail): "two decades of consolidation had cut to a pre-crisis low of 28%"
(line 256, survives the style pass).** Peak 66.6% is FY1995-96; pre-GFC trough 28.2% is
FY2008-09 — ~13 years peak-to-trough, not two decades. "Two decades of consolidation"
overstates the decline's duration as written (it is anchored to the peak→28% cut).
RECOMMEND "more than a decade of consolidation," or drop the duration. Writer's call —
framing, not a numeric error.

**Lede other claims verbatim-unchanged from round-1 — PASS.** Diff vs sections.ts L558:
sentence 1 (mildly expansionary / gap narrows on spending) unchanged; sentence 2
(operating surplus 2028-29 + DoF-definition qualifier + bond issuance) is the round-1
touched version with the `[CLAIM-PENDING]` placeholder — round-1 verdict stands, not
re-verified. Only the debt sentence(s) changed; that change is the PBO attribution
verified above. No drift in carried claims. (Word-count overrun on the lede is a
style/surface matter, not Gate 1.)

**Wiring guardrail (carried from surface-fit, fact-relevant):** the `[CLAIM-PENDING]`
token must not ship visible; if the operating/capital card isn't live by publish, the
sentence ships on prose alone and the token is deleted (no-TK rule).

---

## Gate 1 round 2 — Item 3: internal-consistency sweep (2026-06-04)

Cross-checked the round-2 draft copy against plate-1 live copy (`fiscal.astro` plate-1,
budget-balance / operating-capital, lines 69-71) and across the three round-2 surfaces.

**OVERALL: PASS. No contradictions.**

**(a) Plate-3 round-2 vs plate-1 vs lede — spending / revenue / balance.**
- Plate-3 ("deficit narrows from the spending side; revenue holds") and the lede ("the
  gap narrows because program spending is held below GDP growth, not because revenue
  rises") assert the SAME direction. Consistent.
- Plate-3's program-expense-below-revenue crossover (FY2027-28) is a DIFFERENT measure
  from plate-1's operating-surplus-by-2028-29: program expenses exclude public debt
  charges; the operating balance excludes capital. No contradiction. Plate-3's own
  body (line 204) explicitly states revenue-above-program-spending is NOT a surplus
  (debt service uncovered), pre-empting the conflation. The lede confirms the deficit
  "stays in deficit through the decade," so the FY2027-28 crossover cannot misread as a
  total surplus. Consistent.
- The operating/capital DISPUTE is framed identically everywhere it appears: plate-1
  (DoF surplus by 2028-29 vs PBO never, $94bn definitional gap) and the lede sentence 2
  (operating surplus "only by its own definition" + `[CLAIM-PENDING]`). Same dispute,
  same direction, no clash. The $94bn same-year delta lives ONLY on plate-1; the lede
  carries no DoF-minus-PBO number — correct (frame test honoured).

**(b) Plate-4 vs lede — 41 vs 42.5.**
- Plate-4 interpretation and the lede both carry "Ottawa flat near 41%" / "PBO drifting
  to 42.5% by 2030-31," same numbers, same attribution, same framing direction (DoF
  flat / PBO drifts up). The lede synthesizes (one clause, no $1.6T, no 41.3% start);
  the plate argues it (full mechanism). Different resolution, identical substance.
  Consistent.

**No numeric or directional contradiction across plate-1, plate-3, plate-4, and the
lede.** The page reads as one descending argument (is the surplus real → where does the
narrowing come from → does the level hold), with the spending-side story and the
DoF-vs-PBO disputes framed consistently on every surface that touches them.
