# Fiscal plate-2 redraft — same-vintage two-definition chart

Branch: fiscal-chartbook
Surface: /fiscal/ plate-2 (02) — title + interpretation
Date: 2026-06-04
Chart change: ONE document (Budget 2025) drawn twice — as presented (crosses zero
FY2028-29) vs re-booked on the standard international capital definition (never
balances). Same vintage throughout; NO vintage caveat needed. Source: PBO
RP-2526-017-S Table 4.

Deck sequence: this plate reads after plate-1 ("Ottawa plans to balance day-to-day
spending and borrow only for capital.").

---

## TITLE

**Recommended (new):**

> Whether the books balance depends entirely on which capital definition you accept.

(13 words, terminal period. Reads in deck after plate-1's "plans to balance... borrow
only for capital" — plate-1 states the plan; plate-2 says the plan's success hinges on
a definition. Names what the chart literally shows: one budget, two tracks, balance
contingent on the line drawn.)

**Fallback (keep, still accurate, still fits the deck):**

> The budget watchdog can't confirm the operating books balance—the capital definition is undisclosed.

(Accurate to the May 2026 land, but it now leads with the watchdog rather than the
chart's literal two-track contrast; the redesigned chart argues the definition split
first and the can't-verify second. Recommend the new title; this is the safe fallback.)

---

## INTERPRETATION

> One budget, two sets of books. As Ottawa presents Budget 2025, day-to-day spending
> swings into surplus by 2028-29; re-booked on the standard international definition of
> capital, the Parliamentary Budget Officer's recast never reaches balance. The gap is
> reclassified spending—and a year later, the watchdog still cannot confirm the plan,
> because the definitions remain unpublished.

(54 words by audit tokenizer; em-dash-joined tokens count separately. 3 sentences.
Two numbers: "2028-29" and "Budget 2025" — wait, "Budget 2025" is a document name, not
a quantity; the only numeric quantity is the year 2028-29. Within the max-two cap.)

Take-mechanism-land check:
- Take (opener): "One budget, two sets of books."
- Mechanism (middle): as presented it reaches surplus; re-booked on the standard
  definition it never balances; the gap is reclassified spending — WHY the two tracks
  diverge.
- Land (close): a year later the watchdog still cannot confirm the plan because the
  definitions are unpublished. (May 2026 beat preserved.)

Attribution check (§ frame test):
- "the Parliamentary Budget Officer's recast" — PBO recast attributed by name. PASS.
- "the standard international definition of capital" — stated as the definition PBO
  applies; not asserted as the only correct one. The contrast is "as Ottawa presents"
  vs "re-booked on [the standard] definition," which frames Ottawa's as a choice without
  calling it wrong.
- "misclassifying" NEVER used as fact. "reclassified spending" describes what the chart
  shows (the gap inside each pair) — neutral, names the mechanic, does not assert Ottawa
  erred. PASS.
- "the watchdog still cannot confirm the plan, because the definitions remain
  unpublished" — both grounded in pbo_seu_anchor_assessment_may2026. PASS.

§4.1k forecast markers: the as-presented surplus (2028-29) and the PBO recast are both
forecast tracks. "is set to" / "projected" register carried by "as Ottawa presents
Budget 2025... swings into surplus by 2028-29" (the year-marker signals forecast) and
"the PBO's recast never reaches balance" (recast = projection). No present-tense
assertion of a realised surplus.

---

## CITATION PHRASE LIST

- phrase: "swings into surplus by 2028-29"
  source: card:dof_vs_pbo_operating_capital_dispute
  note: Budget 2025 as-presented day-to-day operating balance (PBO RP-2526-017-S Table 4):
        -4.1, -33.0, -8.7, -5.5, +1.7, +3.0 over FY2024-25→2029-30; crosses zero (into
        surplus) FY2028-29. SAME vintage as the PBO recast — both Budget 2025 (Nov 2025).

- phrase: "the Parliamentary Budget Officer's recast never reaches balance"
  source: card:dof_vs_pbo_operating_capital_dispute
  note: PBO-definition track (RP-2526-017-S Table 4): -10.5, -45.8, -25.3, -23.3, -18.1,
        -17.6 over FY2024-25→2029-30; never crosses zero over the published horizon.

- phrase: "the standard international definition of capital"
  source: card:dof_vs_pbo_operating_capital_dispute
  note: IMF Government Finance Statistics 2014 standard, per PBO RP-2526-017-S. Capital =
        spending producing a durable public asset; excludes tax expenditures and subsidies.

- phrase: "The gap is reclassified spending"
  source: card:dof_vs_pbo_operating_capital_dispute
  note: Per-year pair gaps 6.4, 12.8, 16.6, 17.8, 19.8, 20.6 = cumulative ~$94bn; the three
        reclassified-out categories are corporate income-tax expenditures, investment tax
        credits, and operating subsidies. Do NOT assert "defence/housing reclassified."

- phrase: "the watchdog still cannot confirm the plan, because the definitions remain unpublished"
  source: card:pbo_seu_anchor_assessment_may2026
  note: NT-2627-002-S (May 4, 2026): "not possible to advise in depth as to how updates...
        contribute to the government's assertion that this fiscal anchor remains in balance";
        "No additional insights on the definitions used for classification... were provided."

Source line (unchanged structure; both series now one document):
> Parliamentary Budget Officer, Budget 2025: Issues for Parliamentarians (RP-2526-017-S,
> November 2025), Table 4; PBO Assessment of Spring Economic Update: Fiscal Anchors
> (NT-2627-002-S, May 2026).

asOf stamp: should change from "DoF Apr 2026; PBO Nov 2025" to **"PBO Nov 2025"** —
the chart is now a single document (Budget 2025), single vintage. (Flag for the wiring
pass; do NOT edit src/ per brief.)

---

## NEW CLAIMS INTRODUCED (for the fact gate — Gate 1 re-entry)

These are NEW numerics/claims not in the original plate-2 copy (which was written for the
old mixed-vintage chart). The original Gate 1 did NOT cover them.

1. "as Ottawa presents Budget 2025, day-to-day spending swings into surplus by 2028-29"
   — NEW: the as-presented track and its FY2028-29 zero-crossing. Values: -4.1, -33.0,
   -8.7, -5.5, +1.7, +3.0 (FY2024-25→2029-30). Verify against PBO RP-2526-017-S Table 4.

2. "re-booked on the standard international definition of capital, the PBO's recast never
   reaches balance" — the PBO track was in the old copy, but its pairing as the SAME-
   document re-booking (not a separate-vintage line) is NEW framing. Verify the PBO track
   (-10.5, -45.8, -25.3, -23.3, -18.1, -17.6) and that Table 4 presents BOTH as one
   document.

3. "The gap is reclassified spending" cumulating to the $94bn wedge — verify the per-year
   gaps (6.4, 12.8, 16.6, 17.8, 19.8, 20.6) literally sum to ~$94bn AND that they are the
   visible pair-gaps in the chart (the new chart's annotation). NEW as a literal-sum claim.

4. Vintage assertion: BOTH tracks are Budget 2025 (Nov 2025), single document, no vintage
   mismatch. NEW — supersedes the old card's vintage_mismatch_warning, which applied to the
   OLD chart (DoF SEU line vs PBO recast). Confirm Table 4 carries both tracks before
   approving removal of the vintage caveat.

5. "a year later, the watchdog still cannot confirm the plan" — "a year later" is a NEW
   temporal claim (Budget 2025 Nov 2025 → PBO assessment May 2026 ≈ 6 months, not a year;
   OR Budget 2025 → the current SEU plan it can't verify). FLAG: "a year later" may be
   imprecise. Nov 2025 → May 2026 is ~6 months. Recommend the fact-checker confirm or the
   phrase be cut to "and the watchdog still cannot confirm the plan" (drops the interval).
   See note below.

### Self-flag on "a year later"

The interval is soft. Budget 2025 tabled ~Nov 2025; the PBO cannot-verify assessment is
May 4, 2026 — that is ~6 months, not a year. If "a year later" is read against the
ORIGINAL Budget 2025 anchor-setting vs the May 2026 SEU, it still isn't a clean year.
**Safer interpretation copy** (drops the interval, keeps the land):

> One budget, two sets of books. As Ottawa presents Budget 2025, day-to-day spending
> swings into surplus by 2028-29; re-booked on the standard international definition of
> capital, the Parliamentary Budget Officer's recast never reaches balance. The gap is
> reclassified spending—and the watchdog still cannot confirm the plan, because the
> definitions remain unpublished.

(52 words, 3 sentences, one number. This is the version I recommend shipping. Use the
"a year later" variant ONLY if the fact-checker confirms a defensible ~12-month interval.)
