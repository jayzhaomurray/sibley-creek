# Fiscal plate-5 — debt-service cost

Surface: NEW fiscal plate-5, sits between plate-4 (debt ratio flat) and plate-6 (issuance to a record). The plate answers "can they pay for it": the ratio is flat, but the carrying cost rises anyway, because federal debt grows faster than revenue. Chart: monthly public-debt-charges-to-revenues ratio (Fiscal Monitor), 5-year trailing band, named PBO anchor at the 2030-31 endpoint.

Voice: take-driven chartbook canon (writing-style.md §4.2 chart-plate titles; §4.1 chartbook interpretation).

---

## Index label (plateIndexLabel)

**Proposal:** `Carrying cost`

Alternates, in order of preference:
1. `Carrying cost` — the noun phrase the take turns on; not a recitation of "debt charges."
2. `Cost to carry`
3. `Debt service`

Rationale: plate-4's label is the *ratio*; plate-6's is *issuance*. "Carrying cost" names the thing this plate isolates — the bill, not the stock — and reads as a distinct beat in the index rail.

---

## Title (≤14 words, terminal period, one verb)

**Proposal:**

> The debt ratio is flat, but the bill to carry it keeps rising.

- 13 words. One extending clause off a comma (canon §4.2: "one clause preferred; one extending clause OK").
- Carries the takeaway, not the chart's data. Does not contradict plate-4 — it *names* the coexistence plate-4 sets up: flat ratio, rising bill.
- No number in the title: the number is the chart's job, and the takeaway here is the divergence, not a level.

Alternate (observation–interpretation, em-dash form, if the page wants the mechanism in the title):

> Debt charges climb even as the ratio holds — the stock is rolling onto a bigger base.

(11 words; sharper but pushes mechanism into the title that the interpretation already carries. I prefer the comma form above.)

---

## Interpretation (40–70 target / 95 cap / 2–4 sentences)

**Proposal (draft):**

> Plate-4's flat debt ratio does not mean a flat bill. Federal debt charges now run near eleven cents of every revenue dollar, up from the lows of the zero-rate years, as the existing stock rolls onto today's coupons. [CLAIM-PENDING:pbo_interest_burden_forecast_2030] The driver is not a fresh rate shock — it is that debt is still growing faster than the revenue meant to service it.

Word count: ~62 (excluding the placeholder, which splices to a short PBO-anchor clause). Within target.

**The pending splice.** `[CLAIM-PENDING:pbo_interest_burden_forecast_2030]` is the chart's named PBO anchor — the projection that carries the plate's forward read. On approval it splices to:

> The Parliamentary Budget Officer projects that share rising to roughly thirteen cents by 2030-31, debt charges growing faster than revenues across the window.

The surrounding prose reads as finished without it: sentences 1–3 establish flat-ratio-but-rising-bill and name the mechanism (debt outgrowing revenue, stock rolling onto current coupons) entirely from defensible framing. The PBO clause extends the read forward; it is not what holds the paragraph up.

**Note on the "eleven cents" figure.** The "near eleven cents" reading is the current-period observation tied to `dof_fiscal_monitor_debt_service_share` (10.3¢ YTD, Apr–Feb). Both that card and the PBO card are in `_pending/`. Because the chart's monthly line is pipeline-refreshed and will move, I have written "near eleven cents" rather than a fixed YTD decimal, per the card's vintage note. If the page wants the prose to read with zero pending dependency until both cards clear, swap sentence 2 to:

> Federal debt charges still consume a rising share of every revenue dollar, as the existing stock rolls onto today's coupons.

— which is defensible from the chart alone (the chart shows the rising monthly line) and carries no pending number. **Recommend shipping this zero-dependency sentence-2 form** so the plate clears the build gate before the cards are approved; restore "near eleven cents" on approval if desired.

**Zero-dependency interpretation (recommended ship form):**

> Plate-4's flat debt ratio does not mean a flat bill. Federal debt charges consume a rising share of every revenue dollar, as the existing stock rolls onto today's coupons. [CLAIM-PENDING:pbo_interest_burden_forecast_2030] The driver is not a fresh rate shock — debt is still growing faster than the revenue meant to service it.

~58 words. One pending dependency (the PBO forward anchor, which is genuinely the chart's named anchor and cannot be cut without gutting the plate's job). Everything else is grounded in the chart's own line plus plate-4's established framing.

---

## Suggested source line

> Public debt charges: Department of Finance Canada, The Fiscal Monitor (monthly). Forward projection: Parliamentary Budget Officer, Main Estimates 2026-27 (RP-2627-004-S, May 2026).

Both are primary publishers of their own data. The PBO line is attributed in-prose ("The Parliamentary Budget Officer projects") per the constraint that projections carry attribution.

---

## NEW CLAIMS INTRODUCED

Re-enters all three gates. Countable / factual claims introduced in this draft that need fact-check verification:

1. **"near eleven cents of every revenue dollar"** (only if the non-zero-dependency interpretation form is chosen) — ties to `dof_fiscal_monitor_debt_service_share` (10.3¢ YTD). PENDING card. Recommend the zero-dependency form instead, which drops this claim.
2. **PBO anchor "roughly thirteen cents by 2030-31"** (splice text for `[CLAIM-PENDING:pbo_interest_burden_forecast_2030]`) — **DISCREPANCY TO RESOLVE.** The brief specifies 13.1%. The verified card `pbo_interest_burden_forecast_2030` (RP-2627-004-S, directly-quoted PBO sentence) says **13.2%**. The 13.1% figure appears only in `pbo_efo_june2026_debt_gdp` (June 4 EFO). The "roughly thirteen cents" rounding I've used is true under both, so prose is safe either way — but the chart's *plotted* PBO anchor point must pick one. Recommend the chart plot **13.2% (RP-2627-004-S)** as the cleaner verification chain, OR 13.1% if the page is anchoring to the same-day June EFO; fact-checker to confirm which card the chart binds to.
3. **"debt charges growing faster than revenues across the window"** (splice text) — grounded in PBO's own characterization ("as federal debt grows faster than revenues"); verify against the EFO card excerpt.
4. **Driver framing: "not a fresh rate shock — debt is still growing faster than the revenue meant to service it."** — Not a number, but a causal claim. Grounded in the PBO characterization. Per the brief constraint, the driver is debt-outgrowing-revenue, NOT "rates rising"; this clause is written to honour that. Fact-checker to confirm the mechanism claim is supported and does not overstate.

## Combined gate

**Verdict: FAIL (one mechanical re-point applied; one driver claim contradicted by the card; one mechanism unverified). Returns to writer for the driver sentence. Title, label, and the level claims PASS.**

### Fact-check

**1. Forward anchor — mechanical re-point applied (auto).** Per dispatcher ruling, the forward anchor is **13.1%** from the June 4 EFO (`card:pbo_efo_june2026_debt_gdp`, `verified_value.debt_service_ratio_2030_31_pct: 13.1`), freshest vintage. The draft's placeholder `[CLAIM-PENDING:pbo_interest_burden_forecast_2030]` points to the May Main Estimates card (RP-2627-004-S, 13.2%). **Re-pointed to `card:pbo_efo_june2026_debt_gdp/13.1%`.** Note: "roughly thirteen cents" rounds true under both, so the prose splice text is unaffected; only the binding changes. The chart's plotted anchor must also bind 13.1% (EFO), not 13.2% — resolving the draft's open chart-binding question in favour of the EFO per the freshest-vintage rule.

**2. Level claims — VERIFIED.** "Federal debt charges consume a rising share of every revenue dollar" is supported by the EFO card (10.5% 2024-25 rising to 13.1% 2030-31) and the Fiscal Monitor card (10.3¢ YTD). The recommended zero-dependency form carries no fixed number for the current period — safe.

**3. Driver claim — CONTRADICTED by the card. This is the fail.** The ship text asserts: *"The driver is not a fresh rate shock — debt is still growing faster than the revenue meant to service it."* The card data refutes this. The EFO card states debt/GDP is **flat** across the window (40.7 → 42.5, `pbo_own_characterization`: "projected to remain flat over the medium term"). If debt/GDP is flat and revenue/GDP is roughly stable, debt and revenue grow at similar rates — so the debt-service SHARE of revenue rising ~25% relative (10.5 → 13.1) **cannot** be explained by "debt outgrowing revenue." A rising interest-cost-to-revenue ratio against a flat debt stock is an **effective-interest-rate** story: low-coupon pandemic-era debt maturing and refinancing at higher rates. The brief's instructed driver is arithmetically inconsistent with the card's own numbers. The constraint cannot be honoured without publishing a claim the source contradicts.

**4. "Rolling onto today's coupons" — UNVERIFIED in the cards, but it is the CORRECT mechanism.** Neither card contains "coupon," "roll," "rate," or any rate-mechanism language (grep-confirmed). So the clause imports a mechanism not stated in the sources — by the letter of the no-unverified-mechanism rule, it should be cut. The irony is that it is directionally *right* (refinancing onto higher coupons is exactly what drives a rising DSR against a flat debt stock), whereas the brief's preferred "debt outgrowing revenue" driver is *wrong*. Resolution: do not assert EITHER causal mechanism in ship text. State only what the cards support — the share rises, PBO projects it rising further — and attribute the projection to PBO. Drop both the "debt outgrowing revenue" sentence and the "rolling onto today's coupons" clause.

**5. PDC $80.2B (brief) — not in any card.** The brief frames the source card as holding "PDC $53.7B→$80.2B." Only $53.7B (2026-27) exists, and only in the Main Estimates card, not the EFO card. $80.2B has no card. The draft does not use it in ship text — moot for ship, but flag: do not let $80.2B enter the chart or prose without a card.

### Style checklist

- **Title:** 13 words ≤14 cap. PASS. Terminal period. PASS. One verb-bearing clause + one extending clause off a comma — within §4.2. PASS. No banned vocabulary ("load-bearing," "corridor" absent). PASS.
- **Interpretation:** recommended form ~58 words, within the 95 cap and 2-4 sentence budget BEFORE the driver-sentence cut. After cutting sentence 3 (the contradicted driver), it lands at 2 sentences + the PBO splice — still ≥2, within budget. PASS on budget.
- **Banned vocabulary:** clean. No "corridor," "load-bearing," no math symbols, no Big-Six citation. PASS.
- **Acronyms:** "PBO" expanded in-prose as "the Parliamentary Budget Officer" in the splice. PASS.

### Surface fit

- **Index label "Carrying cost":** no collision with the six-label set (Operating balance / Capital, disputed / Revenue vs spending / Debt/GDP / Carrying cost / Issuance by instrument). Distinct from plate-4 "Debt/GDP" (the stock) and plate-6 "Issuance by instrument" (the flow). PASS. NOTE: this plate inserts as a NEW plate-5; the EXISTING plate-5 in `src/pages/fiscal.astro` ("Issuance by instrument," `chartKey: fiscal-plate-5`, number "05") must be renumbered to plate-6/"06" when this lands. That is a build/wiring task, not a copy task — flagged below.

- **Title coherence with plate-4 — PASS, and the pairing is strong.** Plate-4: "Ottawa and the PBO both see the debt ratio holding flat." Plate-5 (this): "The debt ratio is flat, but the bill to carry it keeps rising." The new title explicitly picks up plate-4's "flat" and turns it — flat ratio, rising bill. No contradiction; it's a deliberate hand-off. The two cohere. PASS. (This coherence is also why the contradicted driver in the interpretation matters more, not less: plate-4 has already told the reader the ratio is flat, so an interpretation that then says "debt is growing faster than revenue" reads as self-contradiction against the adjacent plate.)

- **Framing-alignment check (title direction vs data trajectory):** title asserts the carrying cost "keeps rising." Data: DSR 10.5% (2024-25) → 13.1% (2030-31), monotonic rise; YTD 10.3¢. Trajectory matches the verb. PASS.

### Required revisions before ship

1. Apply the 13.1% re-point (done above; binding moves to `card:pbo_efo_june2026_debt_gdp`).
2. **Cut the contradicted driver sentence** ("debt is still growing faster than the revenue meant to service it") and the **"rolling onto today's coupons"** clause. Replace with card-only language that asserts no unverified causal mechanism. Final ship text below.
3. Chart anchor binds 13.1% (EFO), not 13.2%.

### FINAL SHIP TEXT (fact-checker's corrected form)

- **Index label:** `Carrying cost`
- **Title:** `The debt ratio is flat, but the bill to carry it keeps rising.`
- **Interpretation (ships only after `pbo_efo_june2026_debt_gdp` is user-approved; that card already gates plates 2 and 4, so the page is gated regardless):**

  > Plate-4's flat debt ratio does not mean a flat bill. Federal debt charges already take a rising share of every revenue dollar, and the Parliamentary Budget Officer projects that share climbing to roughly thirteen cents by 2030-31. A flat debt stock does not hold the carrying cost flat.

  (3 sentences, ~46 words, within the 40-70 target. No causal mechanism asserted beyond what the cards state. The forward number is the EFO's 13.1%, rounded to "roughly thirteen cents" — true under the EFO. No `[CLAIM-PENDING]` token survives; the splice is written in.)

- **Source line (re-pointed to the EFO, the binding card):**

  > Public debt charges: Department of Finance Canada, The Fiscal Monitor (monthly). Forward projection: Parliamentary Budget Officer, Economic and Fiscal Outlook – June 2026 (RP-2627-002-S).

  (Corrects the draft's source line, which cited the May Main Estimates RP-2627-004-S; the binding is now the June EFO per the dispatcher ruling.)

## Flagged for the dispatcher

- **Both source cards are in `_pending/`.** Draft lands in `editorial/drafts/_holding/` per protocol if the holding-splice flow is active. The recommended ship form carries exactly one pending dependency (the PBO forward anchor), which is structurally the chart's named anchor and cannot be cut.
- **13.1% vs 13.2% must be resolved before the chart is built** — this is a chart-binding decision, not a prose decision. The prose ("roughly thirteen cents") is safe under both; chart-builder needs the exact plotted point.
- Mid-1990s ~35¢ context was deliberately NOT used — no verified card supports it (grep confirmed no verified historical debt-service card in `editorial/source_cards/`). Stayed inside the verified window per the brief.
