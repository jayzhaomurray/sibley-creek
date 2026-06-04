# Fiscal section lede — gate-3 lift (2026-06-04)

Surface: fiscal section blurb (`src/data/sections.ts` fiscal `blurb.body`).
Serves as fiscal page lede + overview panel blurb.
Voice: take-driven section abstract (writing-style.md §4.1g).
Budget: 2-3 sentences / 90-word cap.

## Amended blurb (full text)

The fiscal stance is mildly expansionary and stays in deficit through the decade—the gap narrows because program spending is held below GDP growth, not because revenue rises. Ottawa's own plan reaches an operating surplus by 2028-29, funded by record bond issuance—but [CLAIM-PENDING:pbo_seu_anchor_assessment_may2026]. Federal debt holds near 41% of GDP on the government's plan; the Parliamentary Budget Officer sees it drifting to 42.5% by 2030-31.

### Placeholder splice text (lands when card approved)

`[CLAIM-PENDING:pbo_seu_anchor_assessment_may2026]` resolves to:

> the budget officer says it cannot verify the surplus, because Ottawa has not disclosed how it sorts operating from capital

Resulting middle sentence once spliced:

> Ottawa's own plan reaches an operating surplus by 2028-29, funded by record bond issuance—but the budget officer says it cannot verify the surplus, because Ottawa has not disclosed how it sorts operating from capital.

## Diff line

- OLD: "Ottawa's own plan reaches an operating surplus by 2028-29 on its own definition of capital, funded by record bond issuance."
- NEW: "Ottawa's own plan reaches an operating surplus by 2028-29, funded by record bond issuance—but [CLAIM-PENDING:pbo_seu_anchor_assessment_may2026]."

Sentence 1 unchanged. Debt sentence unchanged. "funded by record bond issuance" retained. The under-claiming "on its own definition of capital" is cut; the surplus is now framed as a claim the watchdog cannot check, attributed to the PBO. One compact beat — does not inventory plate-2.

## Counts (with placeholder resolved to splice text above)

- Sentences: 3
- Words: 84 (under 90-word cap)

## NEW CLAIMS INTRODUCED

1. **The Parliamentary Budget Officer says it cannot verify the operating surplus because Ottawa has not disclosed how it classifies operating vs. capital spending** — cites card `pbo_seu_anchor_assessment_may2026` (May 4, 2026 PBO assessment of SEU 2026; `pbo_can_verify_anchor: false`, `definitions_disclosed_in_seu: false`). Card is in `_pending/` (status: pending_user) — placeholder used, not direct text; awaits user approval before splice.

Attribution discipline held: the cannot-verify is stated as the PBO's attributed position ("the budget officer says it cannot verify"), not as a fact that Ottawa is misclassifying. No "misclassifying" / "hidden surplus" framing.

## Combined gate (fact + style + surface-fit) — 2026-06-04

**Verdict: PASS with one mechanical fix applied (first-use naming order).**

### Fact-check

1. **"the budget officer says it cannot verify the surplus"** — VERIFIED, not an overreach.
   Card `pbo_seu_anchor_assessment_may2026` excerpt: PBO says "it is not possible to
   advise in depth as to how updates to specific revenue and expenditure items... contribute
   to the government's assertion that this fiscal anchor remains in balance" (`pbo_can_verify_anchor:
   false`). The anchor IS the operating balance — operating spending balanced with revenues by
   2028-29 (the +$0.9bn operating surplus per `dof_operating_balance_projection`). "Cannot verify
   the surplus" is a faithful plain-language compression of "cannot verify the operating-balance
   anchor." Defensible under all readings. The blurb attributes it as the PBO's position ("says
   it cannot verify"), not as a fact of misclassification — attribution discipline held.

2. **"Ottawa has not disclosed how it sorts operating from capital"** — VERIFIED.
   Card excerpt: "No additional insights on the definitions used for classification under the
   framework were provided in terms of key concepts of capital expenditures" (`definitions_disclosed_in_seu:
   false`). Faithful summary.

3. **Sentence 1 + sentence 3 verbatim-identical to live `src/data/sections.ts` fiscal `blurb.body`**
   — CONFIRMED. Both match the live text character-for-character (sections.ts line 558). Sentence 2
   is the changed beat, as designed by the diff.

### Internal consistency / first-use naming order — FIX APPLIED (mechanical)

House convention (writing-style.md line 327: "Parliamentary Budget Officer | PBO"): full
institutional name on first reference, abbreviation thereafter. The draft inverted this — informal
lowercase "the budget officer" appeared first (sentence 2), full "the Parliamentary Budget Officer"
second (sentence 3). No canon support for "the budget officer" as a deliberate informal variant.

Mechanical fix (auto-applied per review_protocol.md — naming/drift correction, not a take change):
- Sentence 2: "the budget officer" -> "the Parliamentary Budget Officer" (+1 word)
- Sentence 3: "the Parliamentary Budget Officer" -> "the PBO" (-2 words)
- Net -1 word; sentence 3's verified numeric phrasing ("sees it drifting to 42.5% by 2030-31")
  untouched. Within +/-5-word budget.

### Style checklist

- Sentences: 3 (cap 3). PASS.
- Words: 82 (cap 90). PASS.
- Take-mechanism-land at abstract register: S1 take+mechanism (mildly expansionary, deficit through
  decade; gap narrows via restrained spending not revenue); S2 the dispute (claimed surplus the
  watchdog can't check); S3 lands on the debt trajectory with the contested track. PASS.
- Banned vocab ("corridor", "load-bearing"): none present. PASS.
- Em-dash/semicolon rhythm: 2 em-dashes + 1 semicolon, varied. PASS.
- Acronyms: GDP/PBO are spoken acronyms; PBO now expanded on first use. PASS.

### Surface-fit checklist

- Serves both the fiscal page lede and the splash overview panel — stands alone, no chart-caption
  dependency. PASS.
- No page-internal references (no "plate-2", no "/research/", no "see below"). PASS.
- Synthesizes (selects the two disputes: unverifiable surplus + debt-track disagreement) rather than
  inventorying every panel. PASS.
- No internal/voice-doctrine jargon leakage. PASS.

### Ops note (not a gate failure)

Card `pbo_seu_anchor_assessment_may2026` is `status: pending_user` in `_pending/`. The claim itself
verifies against the fetched card; the build-time pending-claim gate (draft line 42) holds this in
`_holding/` until approved via `npm run approve-claim`. That is a dispatcher gating step, not a
fact-check block.

### FINAL SHIP TEXT

> The fiscal stance is mildly expansionary and stays in deficit through the decade—the gap narrows
> because program spending is held below GDP growth, not because revenue rises. Ottawa's own plan
> reaches an operating surplus by 2028-29, funded by record bond issuance—but the Parliamentary
> Budget Officer says it cannot verify the surplus, because Ottawa has not disclosed how it sorts
> operating from capital. Federal debt holds near 41% of GDP on the government's plan; the PBO sees
> it drifting to 42.5% by 2030-31.

---

## Re-gate note

Re-enters all three gates. Gate 1 (fact-check) covers the one new claim above; the surplus and bond-issuance content is already grounded (cards `dof_operating_balance_projection`, abstractCitations live). Build-time pending-claim gate will hold this draft in `_holding/` until the card is approved via `npm run approve-claim`.
