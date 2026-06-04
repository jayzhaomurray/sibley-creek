# Fiscal plate-4 — both forecast tracks (DoF + PBO), reframe

Draft date: 2026-06-04
Surface: src/pages/fiscal.astro plate-4 (federal debt % of GDP) + sections.ts fiscal blurb.body debt sentence
Voice: take-driven chartbook canon (writing-style.md §4.1i take-mechanism-land; §4.2 chart-title voice — terminal period, one verb, names the finding; GDP page is live reference)
Status: DRAFT — re-enters all three gates

---

## Reframe summary (why this draft exists)

The current plate-4 copy frames the DoF and PBO tracks as a fork ("see different
paths forward" / "whether the ratio holds depends on whose forecast you take").
Verified today: PBO calls its own track "projected to remain flat over the medium
term" (RP-2627-002-S, p. 9). The two lines draw nearly parallel, ~1pp apart. The
fork framing overstates the difference and must be retired. The honest take:
stability is agreed — both Ottawa and the watchdog hold the ratio roughly flat
near 41-43%; the PBO line just sits persistently higher because it scores bigger
deficits. The fiscal fight on this page lives in plate-2, not here.

---

## Job 1 — plate-4 title

**TITLE (proposed):**

> Federal debt sits elevated but flat, and both Ottawa and its watchdog agree on that.

(13 words, terminal period, one finding: elevated-but-flat, and the agreement.)

**Alternate (tighter, 10 words) if the line wraps:**

> Ottawa and the PBO both see the debt ratio holding flat.

(Drops "elevated"; the interpretation carries the level. Use if layout needs the shorter line.)

---

## Job 1 — plate-4 interpretation

**INTERPRETATION (proposed):**

> Canada's federal debt ratio is elevated but stable—far below its mid-1990s
> extreme. The pandemic pushed it to 47% in 2020-21, well under the 66.6% peak
> that more than a decade of consolidation had cut to a pre-crisis low of 28%.
> Where the ratio goes next is not in dispute: Ottawa's plan holds it near 41%
> through the decade, and the Parliamentary Budget Officer—costing the same
> books in June—calls its own track flat too, near 42-43%. The watchdog's line
> simply runs a notch higher every year, because it scores larger deficits and
> dollar debt climbing past $1.6 trillion. The argument over this budget is not
> about the debt ratio.

Word count: 95 (at the cap; see trim variant below).
Sentences: 5.

**TRIM VARIANT (84 words, 5 sentences) — recommended for the 40-70 target / 95 cap:**

> Canada's federal debt ratio is elevated but stable—far below its mid-1990s
> extreme. The pandemic pushed it to 47% in 2020-21, well under the 66.6% peak
> that more than a decade of consolidation had cut to a pre-crisis low of 28%.
> Where the ratio goes next is not in dispute: Ottawa's plan holds it near 41%
> through the decade, and the Parliamentary Budget Officer—costing the same
> books in June—calls its own track flat too. The watchdog's line just runs a
> notch higher, near 42-43%, because it scores larger deficits. The fight over
> this budget is not about the debt ratio.

Word count: 84.
Sentences: 6.

Structure check (take-mechanism-land):
- Take (s1): elevated but stable.
- Mechanism (s2-4): the historical spine establishes "stable"; then the agreed-flat
  framing with the PBO-higher-because-bigger-deficits mechanism.
- Land (s5): the debt ratio is not where the fight is — points the reader to plate-2.

NOTE on dropped phrase: current copy's "dollar debt keeps climbing past $1.6 trillion"
is preserved in the 95-word version but cut from the 84-word trim. If the trim is
chosen and the $1.6T anchor is wanted, swap the land sentence to: "Dollar debt still
climbs past $1.6 trillion; the fight over this budget is just not about the ratio."
(adds 1 sentence, lands at 88 words.)

---

## Job 2 — sections.ts fiscal blurb.body debt sentence

Sentences 1-2 of the blurb stay verbatim (per brief). Only the third (debt) sentence
changes.

**CURRENT (sentence 3):**

> Federal debt holds near 41% of GDP on the government's plan; the PBO sees it
> drifting to 42.5% by 2030-31.

**PROPOSED (sentence 3):**

> Federal debt holds roughly flat near 41% of GDP on the government's plan—42.5%
> on the watchdog's—two tracks that barely diverge.

This keeps both numbers (41%, 42.5%), drops "drifting" (which reads as more dispute
than exists), and frames them as two roughly-flat tracks. "barely diverge" carries
the reframe in three words.

**FULL REVISED BLURB (for the gate, sentences 1-2 verbatim):**

> The fiscal stance is mildly expansionary and stays in deficit through the
> decade—the gap narrows because program spending is held below GDP growth, not
> because revenue rises. Ottawa's own plan reaches an operating surplus by
> 2028-29, funded by record bond issuance—but the Parliamentary Budget Officer
> says it cannot verify the surplus, because Ottawa has not disclosed how it
> sorts operating from capital. Federal debt holds roughly flat near 41% of GDP
> on the government's plan—42.5% on the watchdog's—two tracks that barely diverge.

Word count (full blurb): 89 (within the 90 cap).

---

## Source insights drawn from

- **card:pbo_efo_june2026_debt_gdp** (_pending/fiscal/) — PBO June 2026 EFO track:
  41.3% FY2025-26 rising to 42.5% FY2030-31, peaking 42.6% in FY2028-29 / FY2029-30;
  deficits avg $4.6bn/yr above the SEU track; dollar debt $1.66T by 2030-31; PBO's
  own "projected to remain flat over the medium term" (p. 9) characterization.
- **pipeline:fiscal:panel-9** (gate-passed) — DoF track: 41.1% FY2025-26 to 41.6%
  FY2030-31 (forecast-stable).
- **Historical spine** (gate-passed, reused verbatim) — 66.6% peak mid-1990s
  (FY1995-96), 28% pre-crisis low, 47% pandemic (FY2020-21), ~41% now; dollar debt
  past $1.6 trillion.

---

## PENDING-CARD DEPENDENCY (read before gating)

The PBO numbers (42.5%, "42-43%", "notch higher every year", "$1.6 trillion" on the
PBO track, the agreed-flat framing) rest on **card:pbo_efo_june2026_debt_gdp**, which
is in `editorial/source_cards/_pending/fiscal/` — NOT yet user-approved. Per the
pending-claims protocol the build-time gate will refuse this draft until the user
walks the card. The 42.5% figure already appears in the live sections.ts citation
block (line 566) bound to this same pending card, so approving the card unblocks both
surfaces together. No placeholder is used because the entire reframe is structurally
dependent on the PBO "remain flat" characterization — without it, there is no honest
"both agree" take and the section would revert to the fork framing. This is the
"halt-equivalent": do not ship plate-4 until the card is approved.

---

## NEW CLAIMS INTRODUCED (re-gating — fact-checker dispatch list)

These are claims NOT in the original plate-4 copy or the original lede, introduced by
this redraft. Each re-enters Gate 1.

1. **"both Ottawa and its watchdog agree" / "not in dispute" / "two tracks that barely
   diverge"** — the central reframe claim: that DoF and PBO agree the ratio holds
   roughly flat. Grounds in PBO's own "projected to remain flat over the medium term"
   (card p. 9) + the two tracks running ~1pp apart (41.1→41.6 DoF vs 41.3→42.5 PBO).
   VERIFY: that "agree / barely diverge" is a faithful compression of a ~1pp parallel
   gap and PBO's self-characterization, not an overstatement in the other direction.

2. **"near 42-43%"** (PBO track described as flat near 42-43%) — NEW range phrasing.
   Grounds in card debt_to_gdp_by_fy: 41.3 / 41.6 / 42.4 / 42.6 / 42.6 / 42.5 across
   FY2025-26 to FY2030-31. VERIFY: "42-43%" fairly brackets a 41.3-42.6 path. (Note:
   the series opens at 41.3, so "42-43%" describes the medium-term plateau, not the
   full path; confirm this reading is defensible or tighten to "low-42s.")

3. **"runs a notch higher every year, because it scores larger deficits"** — causal
   claim that the PBO line sits above DoF because of bigger deficits. Grounds in card:
   deficits avg $4.6bn/yr above the SEU track. VERIFY: PBO higher debt EVERY forecast
   year (40.7/41.3/41.6/42.4/42.6/42.6/42.5 PBO vs DoF 41.1→41.6 — confirm DoF is at
   or below PBO in every overlapping year, especially the front years where both sit
   near 41).

4. **"costing the same books in June"** — retained from current copy but re-stated;
   confirm PBO EFO June 2026 costs the same SEU 2026 fiscal plan (it scores deficits
   vs the SEU track per the card, so yes — flag only for completeness).

5. **Lede sentence "two tracks that barely diverge"** — same as claim 1, applied to the
   sections.ts blurb. Re-verify in the blurb context (89-word total stays within cap).

Claims REUSED verbatim from gate-passed copy (NOT new, no re-check needed): 47% in
2020-21, 66.6% peak, 28% pre-crisis low, "$1.6 trillion" dollar debt, "near 41% through
the decade" (DoF), "42.5% by 2030-31" (PBO) — all already gate-passed in the current
plate-4 / lede.

---

## Combined gate (fact + style + surface fit) — 2026-06-04

**OVERALL: FAIL with mechanical corrections. Two pieces ship after fixes (title, lede); the interpretation needs the recommended-trim variant replaced — it does not meet its stated word count or target, and it carries one causal overstatement the primary source explicitly warns against.**

### GATE 1 — FACT (enumeration done against panel-9, both tracks materialized)

panel-9 already materializes BOTH tracks (primary = DoF SEU; secondary = PBO EFO June 2026). No re-derivation needed; read directly. Year-by-year enumeration, overlapping forecast FYs:

| FY | DoF | PBO | gap (PBO−DoF) | DoF ≤ PBO |
|----|-----|-----|------|-----|
| 2024-25 | — | 40.7 | (no DoF forecast overlap) | — |
| 2025-26 | 41.1 | 41.3 | 0.2 | yes |
| 2026-27 | 41.5 | 41.6 | 0.1 | yes |
| 2027-28 | 41.8 | 42.4 | 0.6 | yes |
| 2028-29 | 41.9 | 42.6 | 0.7 | yes |
| 2029-30 | 41.8 | 42.6 | 0.8 | yes |
| 2030-31 | 41.6 | 42.5 | 0.9 | yes |

DoF forecast range 41.1→41.9 (peaks 41.9, ends 41.6). PBO 40.7→42.6 plateau, ends 42.5.

- **Claim 1 (agree-flat / barely diverge): VERIFIED.** Both tracks hold within a ~1pp band; PBO's own card characterization "projected to remain flat over the medium term" (p. 9, in card) is faithful. "Barely diverge" is fair — the gap is 0.1–0.2pp in the front years, never exceeding 0.9pp. Does NOT overstate the other way: PBO sits at or above DoF in every overlapping year, so "agree" does not erase the persistent PBO-higher fact, which the copy keeps visible ("a notch higher"). Note: the draft's INTERNAL framing ("~1pp apart" / "~1pp parallel gap," lines 15, 154) slightly overstates the gap — it is 0.1–0.2pp early, reaching ~1pp only at the 2030-31 tail. Reader-facing "barely diverge" / "a notch higher" is the more accurate phrasing; keep it.

- **Claim 2 (PBO "near 42-43%"): FAIL — mechanical fix.** PBO path is 41.3 / 41.6 / 42.4 / 42.6 / 42.6 / 42.5. It OPENS at 41.3 (not 42) and the maximum is 42.6 — **it never reaches 43%.** "42-43%" both mis-describes the opening years and implies a 43-handle that does not exist. CORRECTION (auto-apply): "in the low-42s." This is true to the medium-term plateau (42.4–42.6) and to the 42.5 endpoint. Applied in all three ship texts below.

- **Claim 3 (PBO higher EVERY year because larger deficits): PARTIAL FAIL — overstated causation.** The "higher every year" half is VERIFIED (DoF ≤ PBO in all six overlapping FYs; enumerated above). The "**because** it scores larger deficits" half is a single-cause attribution the primary source explicitly contradicts. panel-9's own build note: *"the ~1pp gap reflects higher PBO deficit projections AND different denominators — do NOT present as purely deficit-driven."* PBO uses its own GDP denominators (different vintage from SEU/FRT), so part of the level gap is the denominator, not the deficit. The card's $4.6bn/yr-above-SEU figure supports "larger deficits contribute," not "the gap is because of deficits." CORRECTION: soften to a contributory, denominator-inclusive phrasing — "on bigger deficits and a softer GDP path" — OR drop the causal clause to "a notch higher in the low-42s." Both options provided below. The bare "because it scores larger deficits" CANNOT ship.

- **Claim 4 (costing the same books in June): VERIFIED.** PBO EFO June 2026 scores deficits against the SEU 2026 track (card excerpt: "$4.6 billion per year above the government's Spring Economic Update 2026 track"). Faithful.

- **Claim 5 (lede "two tracks that barely diverge"): VERIFIED** — same basis as Claim 1.

- **Spine spot-check (2 of 6, per brief): VERIFIED.** 66.6% peak → panel-9 FY1995-96 = 66.6 ✓. 28% pre-crisis low → panel-9 FY2008-09 = 28.2 ✓ ("28%" is a fair round). Also confirmed in passing: 47% pandemic = 47.2 (FY2020-21) ✓; DoF ~41% endpoint = 41.6 ✓.

- **Lede verbatim sentences 1-2: VERIFIED** against live sections.ts line 558 — exact match.

### GATE 2 — STYLE

- **Title 1 (15 words): FAILS the brief's ≤14w constraint** (and the plate-title soft wordMax = 14). It is under the 22-word hard cap and 110-char cap (84 chars), so it would not hard-fail the build — but the brief sets ≤14w and §4.2 canon favors the tightest title that names the finding. **Use Title 2 (11 words, 56 chars), which passes clean and carries the same finding.** Title 2 is the ship text.
- **Interpretation: FAILS its own stated metrics.** Draft claims the trim is "84 words, 5 sentences" (line 56) then "84 words" / "6 sentences" (lines 67-68) — self-contradictory. Actual count of the line 58-65 trim: **~99-102 words, 5 sentences** (em-dashes join word pairs). That is far above the claimed 84 and over the 70-word soft target (`plate-blurb` wordMax 70, hardCap 110, sentenceMax 4, sentenceHardCap 6). It does not hard-fail the build but does NOT meet the "40-70 target" the draft says it was built for. The 95-word version is worse. **Replacement interpretation provided below** (75 words / 4 sentences — within sentence soft-max, modestly over the 70 word soft-target, well under hard cap; a strict ≤70 option also given).
- **Banned vocabulary: CLEAN.** No "corridor," no "load-bearing," none of the tic list in title/interp/lede.
- **Take-mechanism-land: holds** in the replacement interpretation (take = elevated-but-stable; mechanism = historical spine + agree-flat with PBO-higher; land = the fight is not about the ratio).
- **Lede blurb: 82 words (corrected) / 89 (draft) — within 90 cap and `plate-blurb` 110 hard cap.** sentences 1-2 verbatim. Clean.

### GATE 3 — SURFACE FIT

- **Land verified standalone.** "The fight over this budget is not about the debt ratio" points the reader to the page's real dispute WITHOUT any literal cross-reference. The draft's reframe summary mentions "plate-2" internally (line 19) but NO ship text contains a page-internal reference — confirmed. The blurb stands alone. PASS.
- The reframe (retire the fork framing) is sound and surface-appropriate: the chart shows two near-parallel lines; the old "different paths" copy contradicted the visual. Reframe improves framing alignment.

### PENDING-CARD GATE (carries through)

All PBO numbers rest on `card:pbo_efo_june2026_debt_gdp`, status `pending_user`. Do not ship plate-4 or the revised lede until the card is user-approved. The 42.5% figure is already live in sections.ts line 566 bound to this same card, so one approval unblocks both surfaces. This verdict is conditional on that approval; it does not override the pending gate.

### FINAL SHIP TEXT (corrections auto-applied)

**TITLE (ship Title 2):**
> Ottawa and the PBO both see the debt ratio holding flat.

**INTERPRETATION (ship — replaces both draft variants; 75 words, 4 sentences):**
> Canada's federal debt ratio is elevated but stable, far below its mid-1990s extreme. The pandemic pushed it to 47% in 2020-21, well under the 66.6% peak that a decade of consolidation had cut to 28%. Where it goes next is not in dispute: Ottawa holds it near 41% through the decade, and the Parliamentary Budget Officer calls its own track flat too, a notch higher in the low-42s. The fight over this budget is not about the debt ratio.

> STRICT-≤70 alternate (drop the spine carve-out detail, 70 words) — use only if the build flags the 70-word soft target: replace sentence 2 with "The pandemic pushed it to 47% in 2020-21, far below its 66.6% mid-1990s peak." and sentence 1's tail accordingly. (Keeps all gate-passed numbers; loses the "decade of consolidation to 28%" arc.)

> NOTE on the dropped causal clause: "because it scores larger deficits" was cut, not softened, in the ship text — the bare deficit attribution fails Gate 1 (panel-9: gap is deficits AND denominators). If the causal mechanism is wanted back, the denominator-honest phrasing is "...flat too, in the low-42s, on bigger deficits and a softer GDP path." (+8 words → 83 words; still under hard cap). Do NOT restore "because it scores larger deficits."

**LEDE sentence 3 (ship — "low-42s" replaces the bare 42.5% only if matching interp; 42.5% is itself verified and may stay):**
> Federal debt holds roughly flat near 41% of GDP on the government's plan—42.5% on the watchdog's—two tracks that barely diverge.

(42.5% here is the verified FY2030-31 PBO endpoint and is fine to keep as a point figure; "barely diverge" is verified. Full revised blurb = 82 words, within the 90 cap.)
