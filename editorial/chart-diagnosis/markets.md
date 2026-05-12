# Markets — chart diagnosis

Page: https://sibleycreek.ca/markets
Last updated: 2026-05-12

How to use: open /markets in another tab. For each plate, answer the
two questions — what should the reader retain, and why isn't the
current chart getting them there. Mark cuttable yes / no / maybe.
The starter checkboxes are optional jog-the-thinking material; skip
them if the free-text already covered it.

Note: this page has the most unwired plates of any section (three of
six). Read the per-plate diagnosis questions for those plates as
"should this plate exist? if so, what should be wired?" — the
disposition for each is largely a wiring decision.

---

## P1 — USDCAD spot

Title: "The loonie has settled into a range well below last fall's
stress reach."

Current geometry (my guess): single line of USDCAD daily, ~5 years.
The "settled into a range" story needs the range and the prior stress
peak to be visible.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Single line — "range well below stress" implies a reference band could mark the recent 1.36–1.38 range; the prior 1.42 stress peak could be annotated
- [ ] BoC effective exchange rate (CEER) flagged as "not yet wired" in the blurb — backend lift would unlock a secondary line
- [ ] Time window — last 12 months captures the recent range; longer captures the stress episode
- [ ] Daily cadence creates a busy line — could decimate to weekly closes for visual cleanliness
- [ ] Something else:

---

## P2 — GoC yield curve

Title: "The front end has repriced on firmer inflation while the long
end stayed anchored."

Current geometry (my guess): could be either (a) time-series of 2y /
5y / 10y / 30y yields as separate lines, OR (b) a CURVE snapshot
(yield vs tenor at a fixed date). The blurb mentions 2s10s spread of
59 bps suggesting time series.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] If time-series of all four tenors: classic spaghetti; eye can't track each tenor
- [ ] Could be two-panel small multiples: left = yields over time; right = current curve snapshot (yield vs tenor with month-ago shadow)
- [ ] Or: just the 2s10s spread (the editorial story is the steepening) as a single line — kills the level dimension but the slope reads
- [ ] "Front end repriced, long end anchored" thesis needs the divergence to be visible
- [ ] Time window
- [ ] Something else:

---

## P3 — Canadian corporate credit spreads (NOT WIRED)

Title: "Canadian investment-grade and high-yield spread series
pending, with GoC 10y shown as the rate benchmark."

Current geometry: **NOT WIRED.** Currently displays the GoC 10y as a
placeholder. Title says so explicitly.

**Should this plate be on the page at all? (yes / no / maybe):**


**If yes, what should the chart actually be? (Canadian IG OAS + HY
OAS — but the data feed is the constraint):**


**If no, where (if anywhere) does the credit-spreads idea live?
(Park until a feed is sourced? Drop entirely?):**


_Notes_: Canadian IG/HY OAS data is paywalled (Bloomberg, ICE).
Public alternatives are sparse — some BoC FSR data on credit-cycle
indicators may be a substitute. Decision is whether to wait for a
feed or replace with a different read.

---

## P4 — Energy (WTI, Brent, WCS)

Title: "Crude has broken higher and the Canadian heavy differential
has compressed sharply."

Current geometry (my guess): three lines — WTI daily, Brent daily,
WCS monthly. Different cadences AND levels. The "differential
compressed" story is the gap between WTI and WCS.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Three series in different cadences (daily + daily + monthly) on one axis is awkward
- [ ] Should be two-panel small multiples: left panel = WTI + Brent (both daily, USD/barrel); right panel = WCS-to-WTI differential (the "compressed" story)
- [ ] Or: just two lines (WTI + WCS), drop Brent. The "Canadian heavy" focus is sharper without the Brent context
- [ ] The differential is the EDITORIAL point — could be a separate small panel showing WTI-WCS spread directly
- [ ] AECO gas flagged as "not in feed" — out of scope
- [ ] Time window
- [ ] Something else:

---

## P5 — Bank stability (NOT WIRED)

Title: "Big-Six PCL and common-equity tier-1 ratio series pending,
with settlement balances at $63.9 billion."

Current geometry: **NOT WIRED.** Currently displays settlement
balances as a placeholder. Title says so explicitly.

**Should this plate be on the page at all? (yes / no / maybe):**


**If yes, what should the chart actually be? (Big-Six PCL ratios?
CET1 vs DSB? OSFI bank-stability indicators?):**


**If no, where (if anywhere) does the bank-stability idea live?
(Research deep dive? Wait for OSFI feed?):**


_Notes_: Big-Six bank-disclosure data lives in quarterly earnings
releases. Could be manually pulled from RBC/TD/BMO/Scotia/CIBC/NBC
quarterly results — research-task, not pipeline-task. OSFI Domestic
Stability Buffer (DSB) and capital adequacy metrics are public.

---

## P6 — Financial conditions (NOT WIRED)

Title: "Standardized financial conditions series pending, with GoC
10y and USDCAD shown as rate and FX inputs."

Current geometry: **NOT WIRED.** Currently displays GoC 10y + USDCAD
as placeholder inputs. Title says so explicitly.

**Should this plate be on the page at all? (yes / no / maybe):**


**If yes, what should the chart actually be? (BoC FCI? Goldman /
Bloomberg FCI? In-house composite?):**


**If no, where (if anywhere) does the FCI idea live? (Research
deep dive? Build an in-house FCI as a project?):**


_Notes_: BoC publishes its own FCI (financial-conditions index)
through its Indicators of Capacity and Inflation Pressures research.
Goldman Sachs and Bloomberg publish proprietary FCIs (paywalled).
In-house FCI is a research project — would anchor a deep dive.

---

## Page-level notes

Cross-cutting issues (THREE of six plates not wired — the page is
substantially incomplete; the editorial decision is whether to
ship 3 plates and remove the placeholders, or keep them visible
as commitment to a future state. Other patterns: cadence mismatch
across plates, plate ordering, deep-dive exits):

