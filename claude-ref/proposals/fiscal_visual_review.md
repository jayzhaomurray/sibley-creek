# Fiscal page — critical visual review

Art-director pass, 2026-06-02. Fresh holistic eye on the rendered state (deviceScaleFactor 2 screenshots). Drift/token audit already applied; this is composition, legibility, and "looks-wrong" only. Placeholder *wording* ([TITLE TK]/[CAPTION TK]/[ANNO TK]) is the writer's job and is NOT flagged — but placeholder *rendering* (overflow, collision, wrong color) IS.

Severity key: **P0** = looks broken / ship-blocker · **P1** = looks off / noticeably amateur · **P2** = polish.

---

## P0 — looks broken

### 1. Plate 5 occupies ~40% of its frame; the rest is dead whitespace
**Plate:** 5 (issuance). The stacked-bar plot renders at roughly a third of the available width — the bars cluster on the left, and the right ~55–60% of the frame is empty. Next to the four full-width line/bar plates above it, this reads as a rendering failure, not a design choice. It is the single most "fucky"-looking thing on the page and is almost certainly what Jay noticed first.
**Fix:** Force the plot area to fill the canon plot width (match plate 1's bar-plot extents). This is a width/`x`-range or category-padding problem in the bar layout, not a data problem. The 8 fiscal years should span the full axis like plate 1's bars span 1983→2031.

### 2. Plate 5 has no legend / no bucket identification
**Plate:** 5. Three textures stack (solid black top, cross-hatch middle, diagonal-line bottom) but NOTHING tells the reader which is bills, notes, or bonds. Plate 1 labels its two textures ("Operating"/"Capital") at the right; plate 5 labels none of its three. A stacked chart with unlabeled stacks is unreadable.
**Fix:** Add right-edge terminus labels (Bills / Notes / Bonds) in the plate-1 pattern, OR an inline legend. Match plate 1's labelling convention so the set is consistent.

### 3. Plate 5 forecast divider is missing / invisible
**Plate:** 5. Brief says a forecast divider should sit before FY25-26/26-27, and there's a "FORECAST" word top-right — but no dashed vertical divider is visible between the bars (unlike the clear dashed dividers on plates 1–4). The "FORECAST" label floats with nothing under it.
**Fix:** Render the dashed vertical divider between FY24-25 and FY25-26 bars, matching the line-plate divider style. Without it the FORECAST label is orphaned.

### 4. Plate 2 — terminus placeholder labels collide and double-print
**Plate:** 2 (merged rev/exp). At the right edge two "[CAPTION TK:" placeholders are stacked directly on top of each other (double-printed, overlapping glyphs) and they overrun the "15.7%" value label, producing a muddy gray smear. Even allowing for placeholder *wording*, the *rendering* is broken: two labels at the same anchor with no vertical separation.
**Fix:** Give the two line termini distinct vertical offsets so their end-labels don't stack. The revenue (solid) and program-expense (dashed) lines end ~0.5pp apart — their labels need ~14px of vertical separation or a leader to split them. This will also be needed once real captions replace the TKs.

---

## P1 — looks off

### 5. Plate 1 — "Operating/Capital" labels imply the whole 40-year series is split, but only the forecast tail is
**Plate:** 1 (balance). The dominant element is 40 years of solid-black total-balance bars. The opex/capex texture split appears ONLY on the ~6 forecast bars at the right. But the "Operating" and "Capital" legend labels sit at the right edge against those forecast bars in a way that reads as a legend for the ENTIRE chart. A reader scanning left sees solid black bars and now wonders whether those are "Operating." The two-thing legend is describing a sub-segment of 6 bars out of ~48.
**Fix:** Either (a) drop the texture split entirely — it's carrying almost no analytical weight on 6 forecast bars and is the source of most of plate 1's confusion — or (b) scope the labels visually to the forecast region (e.g. a small bracketed legend above the forecast tail only), so it's unambiguous the split applies to forecast bars alone.

### 6. Plate 1 — the opex/capex proportions look wrong (capital >> operating)
**Plate:** 1. On the forecast bars, the solid-black "Operating" segment is a thin sliver at the top and the cross-hatch "Capital" segment is the large lower bulk. In reality federal capital spending is a *small* share of the deficit; operating is the bulk. The visual says the opposite. Either the segments are inverted, or the split is mislabeled, or it's plotting something other than what the labels claim.
**Fix:** Verify the segment assignment against source. If correct, the labels are misleading and need rethinking; if inverted, swap. Flagging for chart-builder + data check (do not author the fix here).

### 7. Plate 1 — COVID bar (-$327B) crushes 40 years of structural detail
**Plate:** 1. The single COVID FY20-21 bar drives the axis to -360, so every other bar (the entire 1983–2019 structural story, the -$36B forecasts) is compressed into the top ~12% of the canvas. The bottom three-quarters of the plate is empty white below the historical bars. The interesting fiscal history is unreadable.
**Fix:** This is the classic outlier-dominates problem. Options, worst-first: (a) clip/break the COVID bar with an axis-break or a capped bar annotated "-$327B"; (b) accept it but tighten — there's no good answer with a single shared axis. At minimum the empty lower half is wasted; an axis break would reclaim it. Editorial call for Jay, but the current state buries the data.

### 8. Plate 2 — solid vs dashed reads, but the COVID dashed spike is ambiguous at the crossing
**Plate:** 2. Generally the solid (revenue) and dashed (expense) lines are distinguishable. But around the 2020 COVID spike the dashed expense line shoots to 28% and crosses/runs alongside the solid line in the 2019–2022 cluster; in that dense region the dash pattern is hard to follow against the solid. It's the one spot where the two-line-on-one-axis choice strains.
**Fix:** Minor — slightly heavier weight on the solid line, or a touch more dash contrast, would separate them in the crowded COVID years. Low effort, real readability gain.

### 9. Plate 3 is a near-duplicate of plate 2's dashed line
**Plate:** 3 vs 2. Plate 3 (standalone program-expenses %GDP) is the same series as plate 2's dashed line, redrawn solid. Side by side in the set it reads as "why am I seeing expenses twice." The COVID spike, the 2024 plateau, the 15.x% terminus — all repeat. This is a genuine redundancy, not just my eye.
**Fix:** Editorial/structural decision for Jay: either (a) cut plate 3 entirely (plate 2 already carries expenses), or (b) repurpose plate 3 to show something plate 2 can't — e.g. expense *composition* (program vs debt-service), or a decomposition — so it earns its slot. As-is it's filler.

### 10. Plates 2, 3, 4 — red latest-dot collides with the right-edge value label and TK caption
**Plate:** 2, 3, 4. On all three line plates the red forecast dot sits hard against the axis frame, and the value label (15.7% / 15.1% / 41.6%) plus the "[CAPTION TK:" text crowd into a tight right-margin strip, partly clipping at the frame edge. The dot is nearly touching the axis spine.
**Fix:** Add a few px of right padding inside the plot so the terminal dot isn't kissing the frame, and reserve a clean right-margin gutter for the value label so it doesn't tangle with the dot or the (eventual) caption. Consistent gutter across all three line plates.

---

## P2 — polish

### 11. Annotation leader lines cross the decimal point and misread
**Plate:** 4 (debt), and 1, 3. The "66.6%", "47.2%", "28.2%", "28.1%", "-$36.3B" callouts have a short vertical leader that lands ON or immediately beside the decimal point — e.g. "66 | 6%", "47 | 2%", "-$36 | .3B". The leader tick reads as part of the number, so "66.6%" momentarily scans as "66 6%". Confirmed on plate 4 (all three callouts) and plate 1's -$36.3B.
**Fix:** Offset the leader line so it doesn't intersect the number's baseline/decimal. Either anchor the leader to the side of the label or add vertical gap between leader-top and the number. Small but it's in the most-read spot (the callout).

### 12. Plate 1 "Operating"/"Capital" labels are larger than the section's body/label type
**Plate:** 1. The two right-edge labels render noticeably heavier/larger than the axis tick labels and the other plates' terminus labels (compare to plate 4's "41.6%"). Out of step with the type scale.
**Fix:** Bring to the canon terminus-label size used on plates 2–4.

### 13. Plate 4 — upper "[ANNO TK]" for the 66.6% peak nearly touches the top axis frame
**Plate:** 4. The peak callout's "[ANNO TK]" line sits right at the 70% gridline / top frame, slightly cramped. Will matter once real text (longer than the placeholder) lands.
**Fix:** Ensure the top callout has clearance below the frame; budget for real anno text being longer than "[ANNO TK]".

### 14. Set-level: plate heights/aspect inconsistent once plate 5 is fixed
**Plate:** set. The four line/bar plates read as a consistent stack; plate 5's broken width (finding 1) currently makes the set feel unbalanced at the bottom. Once 5 is widened, re-check that all five share the same plot-area aspect and left-axis alignment so the stack reads as one chartbook.
**Fix:** After fixing #1, eyeball the five left axis spines for vertical alignment and equal plot width.

---

## Suggested fix order
1. Plate 5 width (#1) — biggest visual break, likely the user's complaint.
2. Plate 5 legend + forecast divider (#2, #3).
3. Plate 2 terminus label collision (#4).
4. Plate 1 opex/capex: verify proportions/labels, decide whether to keep the split at all (#5, #6).
5. COVID-bar axis treatment on plate 1 (#7) + plate 3 redundancy decision (#9) — both editorial calls for Jay.
6. Right-margin gutter on line plates (#10), leader-line offset (#11), then remaining polish.

Editorial decisions that need Jay (not chart-builder): keep-or-cut plate 3 (#9), keep-or-cut the opex/capex split (#5/#6), and the COVID-bar axis-break call (#7).
