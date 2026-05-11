# Fact-check report -- homepage_index_tile_lines.md

Reviewer: fact-checker (macro-research-department)
Date: 2026-05-11
Subject: editorial/drafts/homepage_index_tile_lines.md (7 single-sentence
tile lines for the homepage tiles, one per section)
Method: per-claim verification against W3-R1 (GDP), W3-R2 (Inflation),
Wave 2 fiscal index and vector resolutions, src/data/sections.ts
placeholders, and primary sources where available.
ASCII-only.

---

## Summary verdict

PASS-WITH-FLAGS for GDP, Inflation, Policy. UNVERIFIED for Labour,
Housing, Markets, Trade -- writer has correctly self-flagged each as
relying on src/data/sections.ts placeholders without Wave-3 research
coverage. The directional / interpretive language in those four tiles
is grounded in the sparkline trajectories in sections.ts; the precise
numbers are pipeline placeholders.

Critical correction confirmed: the Inflation tile line says "core
measures holding near target." The original prompt anchor (per
src/data/sections.ts line 287 placeholder blurb: "Shelter is still
doing most of the work") is STALE -- W3-R2 verifies the opposite for
March 2026 (shelter cooled to 1.7%, well below the 2.4% headline and
below all-services 2.5%; mortgage-interest cost essentially extinguished
at 0.3%; energy at 3.9% and food at 4.0% are now the marginal pressure
points). The writer's correction is supported and the original prompt
anchor is canonically stale.

---

## Per-tile verdicts

### GDP tile (Line 27)
Line: "Real GDP rose 0.2% in February 2026, but the quarterly cut contracted 0.2% in Q4 2025."

| Claim | Verdict | Source |
|---|---|---|
| Real GDP rose 0.2% February 2026 | VERIFIED | StatCan Daily 2026-04-30 (re-fetched); W3-R1 Section B Panel 1. |
| Quarterly cut contracted 0.2% Q4 2025 | VERIFIED | W3-R1 Section B Panel 1; StatCan Daily 2026-02-27. |
| Word count 16 | VERIFIED | Counted, 16 words. |

Verdict: VERIFIED. Tile-line ready for style polish.

### Inflation tile (Line 30-31)
Line: "Headline CPI ticked up to 2.4% in March 2026, with core measures holding near target."

| Claim | Verdict | Source |
|---|---|---|
| Headline CPI ticked up to 2.4% in March 2026 | VERIFIED | StatCan Daily 2026-04-20 (re-fetched); W3-R2 Panel 1. |
| Core measures holding near target | VERIFIED | BoC CPI page 2026-05-11: trim 2.2%, median 2.3%; W3-R2 Panel 2. |
| Word count 15 | VERIFIED | Counted, 15 words. |

Critical override-check on the prompt's "shelter doing the work" anchor:
The prompt-supplied placeholder anchor (per sections.ts line 287 blurb body)
reads "Shelter is still doing most of the work, with mortgage interest cost
the largest single contributor." This is the April 2026 placeholder copy in
sections.ts and explicitly flagged in the writer's draft (Lines 96-104) as
conflicting with Wave-3 research. W3-R2 Panel 4 verifies:
- Shelter Y/Y March 2026: 1.7% (BELOW the 2.4% headline)
- All-services Y/Y: 2.5% (also above shelter)
- Mortgage interest cost Y/Y: 0.3% (essentially extinguished)
- Energy Y/Y: 3.9% (marginal pressure-point)
- Food Y/Y: 4.0% (other marginal pressure-point)

The prompt-supplied "shelter doing the work" framing is canonically stale
for the March 2026 vintage. The writer correction to "core measures holding
near target" is supported by Wave-3 research and is the right framing for
this tile vintage.

Verdict: VERIFIED with override-confirmation. Researcher / editorial-director
should be informed that the sections.ts placeholder blurb (line 287) needs
a parallel update to remove the shelter-doing-the-work framing.

### Labour tile (Line 34-35)
Line: "Unemployment held at 6.1% in April 2026, while per-capita employment kept falling on a yearly basis."

| Claim | Verdict | Source |
|---|---|---|
| Unemployment held at 6.1% in April 2026 | UNVERIFIED | No Wave-3 labour research pack on file. Source is sections.ts line 312 placeholder. Writer self-flagged Lines 110-113. The May 2 2026 LFS release referenced in sections.ts line 350 blurb date implies the print has landed, but no W3 research has been routed to verify. NOTE: wave2_vector_resolutions.md lines 132-136 confirms the correct LFS Canada unemployment-rate vector is v2062815, with April 2026 print 6.9% per StatCan WDS getDataFromVectorsAndLatestNPeriods receipt on 2026-05-11. |
| Per-capita employment kept falling on a yearly basis | UNVERIFIED | Wave-3 GDP per-capita research addresses GDP per-capita, not employment per-capita. Writer self-flagged Lines 116-121. |
| Word count 16 | VERIFIED | Counted, 16 words. |

CRITICAL: the 6.1% placeholder appears to contradict the backend WDS
receipt in wave2_vector_resolutions.md (Canada unemployment rate v2062815
April 2026 = 6.9%, March 2026 = 6.7%). This is a 0.8pp gap from the
prompt placeholder. The wave2 receipt is a primary-source-derived value
(WDS getDataFromVectorsAndLatestNPeriods on 2026-05-11) and should be
treated as authoritative over the sections.ts placeholder.

Verdict: UNVERIFIED + APPARENT CONTRADICTION. Hold-for-research. Recommend
the writer pause this tile line until the researcher confirms the April
2026 LFS print, OR the writer swaps to the verified 6.9% value with
appropriate directional framing (e.g., "unemployment rose to 6.9%"
rather than "held at 6.1%").

### Housing tile (Line 38-39)
Line: "MLS HPI fell 1.4% year-over-year in April 2026, with the national benchmark still in negative territory."

| Claim | Verdict | Source |
|---|---|---|
| MLS HPI fell 1.4% Y/Y April 2026 | UNVERIFIED | No Wave-3 housing research on file. Source is sections.ts line 373 placeholder. Writer self-flagged Lines 123-128. |
| Still in negative territory | VERIFIED directionally from sections.ts sparkline | sections.ts lines 377-380 sparkline shows ~12 consecutive monthly readings at or below 0, with the series crossing through zero from positive territory. Directional framing supported. |
| Word count 16 | VERIFIED | Counted, 16 words. |

Verdict: UNVERIFIED on numeric, VERIFIED on direction. Hold-for-research
on the -1.4% value pending CREA April 2026 release verification.

### Policy tile (Line 42-43)
Line: "The Bank of Canada cut 25 basis points to 2.75% on April 29, 2026."

| Claim | Verdict | Source |
|---|---|---|
| Bank of Canada cut 25 bps to 2.75% on April 29, 2026 | VERIFIED | sections.ts line 432-434 confirms 2.75% on Apr 29, 2026 with -25 bps delta. W3-R1 Section B Panel 1 cites BoC FAD release URL. |
| Word count 14 | VERIFIED | Counted, 14 words. |

Verdict: VERIFIED. Tile-line ready for style polish.

### Markets tile (Line 46-47)
Line: "USDCAD closed at 1.378 on May 9, 2026, with the loonie drifting weaker through the spring."

| Claim | Verdict | Source |
|---|---|---|
| USDCAD closed at 1.378 on May 9, 2026 | UNVERIFIED, plausible vs sections.ts | sections.ts line 498-500 placeholder shows USDCAD 1.378 asOf May 9, 2026. W3-R2 Panel 6 has USDCAD 1.3575 at 2026-05-01 (month-end-last in boc-tracker), a different vintage. The sections.ts placeholder shows the daily series walking 1.348 -> 1.378 over 24 observations. |
| Loonie drifting weaker through the spring | VERIFIED directionally from sections.ts sparkline | sections.ts sparkline trajectory supports the directional claim. |
| Word count 16 | VERIFIED | Counted, 16 words. |

Verdict: UNVERIFIED on the precise 1.378 closing value. Hold-for-research
on a verified BoC Valet FXUSDCAD daily-series pull dated 2026-05-09 (or
the next BoC publication day) before this tile ships.

### Trade tile (Line 50-51)
Line: "Canada merchandise trade balance posted a 2.3-billion-dollar deficit in March 2026, extending the run of deficits."

| Claim | Verdict | Source |
|---|---|---|
| Merchandise trade balance -2.3B March 2026 | UNVERIFIED | No Wave-3 trade research pack. Source is sections.ts line 557-558 placeholder. Writer self-flagged Lines 140-144. The wave2_fiscal_citation_index.md is about fiscal (DoF/PBO), not merchandise trade, so does not help here. |
| Extending the run of deficits | VERIFIED directionally from sections.ts sparkline | sections.ts lines 562-565 sparkline shows ~12 consecutive negative monthly readings. Directional framing supported. |
| Word count 16 | VERIFIED | Counted, 16 words. |

Verdict: UNVERIFIED on the 2.3B value. Hold-for-research on the StatCan
Table 12-10-0119-01 March 2026 print verification before this tile ships.

NOTE: the draft as written uses "Canada's merchandise trade balance" with
the possessive apostrophe; primary-source value verification has not been
performed in this fact-check pass. Style-editor may keep the possessive.

---

## Voice / canon principle checks

| Principle | Compliance | Note |
|---|---|---|
| 12-16 words per tile, active voice, declarative, sentence-case (Path C spec) | PASS on all 7 tiles | Counted; all within 14-16 words. |
| No hedging | PASS | No "may", "could", "might", "we think". |
| No Big-Six citation in prose | PASS | No bank names appear. |
| Names the latest dated print | PASS-WITH-CAVEAT | GDP, Inflation, Policy: anchored to verified primary-source prints. Labour, Housing, Markets, Trade: anchored to sections.ts placeholders (acknowledged by writer in flags). |
| No editorializing on direction beyond what the data supports | PASS | Inflation tile's "core measures holding near target" is the conservative phrasing relative to the contradicted prompt anchor; verified by W3-R2 Panel 2 trajectory. |
| Tile-line distinct from headline question and blurb body | PASS | Tile-lines name a recent print and a directional read, not the section's evergreen headline question. |

---

## Hand-off note for style-editor

Safe to polish: GDP tile, Inflation tile, Policy tile. All three are
anchored to verified primary-source data.

Hold-for-research on:
- Labour tile (UR 6.1% appears contradicted by 6.9% per wave2 vector
  resolutions; per-capita employment Y/Y not pinned to a verified
  number).
- Housing tile (MLS HPI -1.4% from sections.ts placeholder; CREA April
  release verification needed).
- Markets tile (USDCAD 1.378 May 9 from sections.ts placeholder; BoC
  Valet daily FXUSDCAD verification needed).
- Trade tile (merch balance -2.3B March from sections.ts placeholder;
  StatCan Table 12-10-0119-01 verification needed).

Do not change in the verified tiles:
- "Real GDP rose 0.2% in February 2026" -- exact verified value.
- "Quarterly cut contracted 0.2% in Q4 2025" -- exact verified value.
- "Headline CPI ticked up to 2.4% in March 2026" -- exact verified value.
- "Core measures holding near target" -- W3-R2-supported correction
  vs the stale "shelter doing the work" prompt anchor.
- "25 basis points to 2.75% on April 29, 2026" -- exact verified value.

Need writer rework / researcher routing:
1. **Labour tile (UNVERIFIED + APPARENT CONTRADICTION):** The 6.1%
   placeholder disagrees with the v2062815 WDS receipt (6.9% April
   2026). Writer needs to either pause this tile until research is
   routed, or refresh to the verified 6.9% value. The "per-capita
   employment kept falling on a yearly basis" half also needs a
   research pull (StatCan Table 14-10-0287-01 / 17-10-0009-01
   derivation).
2. **Inflation tile (override-confirmed):** writer's correction is
   supported; recommend researcher / editorial-director update the
   sections.ts placeholder blurb body (line 287) in parallel to
   remove the now-stale shelter-doing-the-work framing.
3. **Housing / Markets / Trade tiles (UNVERIFIED):** writer correctly
   flagged each as relying on the prompt placeholder. Hold for
   research routing or accept the placeholders as v1 launch copy with
   explicit "placeholder, refresh on next release" stamps.

End of report.
