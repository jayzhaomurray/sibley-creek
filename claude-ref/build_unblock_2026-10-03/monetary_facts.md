# Monetary section fact pack -- build unblock 2026-10-03

Prepared 2026-10-03 (fetches 16:49-16:53 UTC). For the writer redrafting the
`slug: "monetary"` block in `src/data/sections.ts` (tileLine + blurb body).
Primary sources only: bankofcanada.ca pages, BoC Valet, and the repo pipeline
files. Repo pipeline files were last fetched 2026-10-03T00:48Z (per their
`.meta.json`); a refresh rewrote them at 12:46-12:48 local today, so every
value below carries its own as-of date. Re-read the as-of date before shipping
if another refresh lands.

Format of each fact: value | as-of | source | suggested `source:` string.

---

## 1. Bank of Canada decisions since July 15, 2026

There has been exactly ONE fixed-announcement-date decision since July 15, and
it was on **September 2, 2026** (not September 9).

- F1.1 Decision: HOLD. Overnight target 2.25%, Bank Rate 2.5%, deposit rate 2.20%.
  | as-of 2026-09-02
  | https://www.bankofcanada.ca/2026/09/fad-press-release-2026-09-02/ (title: "Bank of Canada maintains the policy rate at 2 1/4%")
  | `card:boc_fad_press_release_2026_09_02`
  Verbatim: "The Bank of Canada today held its target for the overnight rate at 2.25%, with the Bank Rate at 2.5% and the deposit rate at 2.20%."

- F1.2 Policy-stance paragraph, verbatim and complete (final paragraph of the release):
  "With the economy and inflation evolving broadly as forecast in the July MPR,
  Governing Council agreed to leave the policy rate unchanged. However, the
  upside risks to inflation have increased, while new tariffs make growth
  prospects more uncertain. Governing Council will assess the sustainability of
  the economic rebound and the outlook for inflation, and is prepared to adjust
  monetary policy as needed. The Bank remains committed to maintaining
  Canadians' confidence in price stability through this period of global
  upheaval."
  (The source renders the apostrophe in "Canadians'" as a curly quote, U+2019.)
  | as-of 2026-09-02 | same URL
  | guidance sentence: `card:boc_fad_2026_09_02_guidance`
  | risk sentence: `card:boc_fad_2026_09_02_inflation_risks`

- F1.3 The word "appropriate" does NOT appear anywhere in the September 2
  statement (checked programmatically against the page text). The July 15
  sentence was: "Governing Council judges the current policy rate remains
  appropriate to sustain the economic recovery and bring inflation back to the
  2% target, in line with the MPR projections."
  (https://www.bankofcanada.ca/2026/07/fad-press-release-2026-07-15/, re-fetched today.)
  OBSERVATION: the "remains appropriate" sentence is absent in September and
  "the upside risks to inflation have increased" is new.
  INTERPRETATION (mine, not the Bank's words): the statement shifted in a
  hawkish direction. The Bank did not say it has a tightening bias; do not
  write that it did. There is no card for the July sentence; if the writer
  wants the July-to-September contrast in prose, request a card for it first.

- F1.4 Other verbatim lines from the same September 2 release that could carry a "why" (no cards created; request one if used):
  - "Financial conditions have tightened since July. Long-term bond yields have moved up globally, including in Canada."
  - "CPI inflation has been hovering around 3% in recent months, mainly because of persistently higher gasoline prices."
  - "excluding gasoline, inflation was 2.2% and measures of core inflation remained close to 2% in July."
  - "with the Middle East conflict still ongoing and little progress reopening the Strait of Hormuz, upside risks to the Bank's inflation forecast have increased."
  - "new US tariffs and Canadian counter-measures have been announced following the breakdown of trade talks between Canada and the United States."
  - "Overall, recent data reaffirm Governing Council's view of a broadening recovery in Canada's economy."

- F1.5 No other decision on or before 2026-10-03. The Bank's rate table lists
  September 2, 2026 as the most recent row, and the 2026 schedule has nothing
  between September 2 and October 28.
  | https://www.bankofcanada.ca/core-functions/monetary-policy/key-interest-rate/ (fetched 2026-10-03T16:49Z)
  | covered by `card:boc_fad_holds_post_oct_2025_cut`

- F1.6 Next scheduled decision: **October 28, 2026**, with a Monetary Policy Report. Then December 9, 2026.
  Verbatim (Sep 2 release): "The next scheduled date for announcing the overnight rate target is October 28, 2026. The Bank's next MPR will be released at the same time."
  | `card:boc_fad_press_release_2026_09_02` (the card's notes record this; excerpt is the decision sentence)

- F1.7 Suggested slot values (writer/dispatcher to apply, I did not touch src/):
  heroKicker "September rate decision"; latestReleaseDateOverride "Sep 2, 2026";
  updatedAt Date.UTC(2026, 8, 2, 13, 45) (the Bank announces at 9:45 ET = 13:45 UTC).

## 2. Consecutive holds since the October 29, 2025 cut

The count is now **SEVEN** (was six). September 2 was a hold, so the streak is intact.

Full enumeration (Bank of Canada rate table, "Target 2.25, Change ---" on every row):
1. 2025-12-10
2. 2026-01-28
3. 2026-03-18
4. 2026-04-29
5. 2026-06-10
6. 2026-07-15
7. 2026-09-02

Anchor row: October 29, 2025, target 2.25, change -0.25.
| source https://www.bankofcanada.ca/core-functions/monetary-policy/key-interest-rate/
| `card:boc_fad_holds_post_oct_2025_cut` with `expected_count: 7`

Card updated today: enumeration now has 7 entries, verified_at 2026-10-03,
vintage_label "Sep 2, 2026 FAD (latest hold)", next_expected 2026-10-28.

**BUILD WARNING.** The build validates `expected_count` against the card length.
With the card at 7, every citation still saying `expected_count: 6` now fails.
There are FOUR of them, and three are outside the block the writer was asked to redraft:
- `src/data/sections.ts` line 524 -- "six straight decisions"
- `src/pages/monetary.astro` line 54 -- "sixth consecutive hold"
- `src/pages/monetary.astro` line 55 -- "Six holds in" (a plate title)
- `src/pages/monetary.astro` line 85 -- "BoC has held since October"
All four need the prose and the count moved to seven in the same pass.

## 3. Neutral range (card:boc_mpr_neutral_range, 2.25% to 3.25%)

STILL STANDS. Not revised.

- F3.1 April 2026 MPR appendix, re-fetched today, excerpt still present verbatim:
  "The Canadian nominal neutral rate is estimated to be within the range of 2.25% to 3.25%, unchanged from that in the April 2025 Report."
  | https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/appendix/
  | `card:boc_mpr_neutral_range` (card not modified)

- F3.2 July 2026 MPR (the only MPR since April; the next is October 28) reaffirms it:
  "The nominal neutral interest rate in Canada is assumed to be at the midpoint of its estimated 2.25% to 3.25% range."
  | https://www.bankofcanada.ca/publications/mpr/mpr-2026-07-15/tariff-assumptions/
  | no card for this sentence; the existing card covers the claim.
  The July MPR has no appendix (the neutral range is reviewed once a year, in April). I searched all eight July MPR sections; this is the only mention.

- F3.3 "Floor of the neutral range" still holds as arithmetic: overnight target 2.25% equals the range's lower bound 2.25%. | `derived`

## 4. Latest values from repo data

File key: `data/site/panel_data/monetary.json` (generatedAt 2026-10-03T00:48:20Z)
and the underlying CSVs. BoC values cross-checked today against Valet
(https://www.bankofcanada.ca/valet/observations/V39079,BD.CDN.2YR.DQ.YLD,AVG.INTWO/json?start_date=2026-08-18); all match.

### Levels

- F4.1 Overnight target: **2.25%** | as-of 2026-10-01 | `data/raw/overnight_rate_daily.csv`, Valet V39079; panel-1.secondary | `pipeline:boc:V39079`
- F4.2 GoC 2-year benchmark yield: **3.27%** | as-of 2026-10-01 | `data/raw/yield_2yr.csv`, Valet BD.CDN.2YR.DQ.YLD; panel-2.primary | `pipeline:boc:yield_2yr`
- F4.3 UST 2-year (constant maturity): **4.78%** | as-of 2026-10-01 | `data/raw/us_2yr.csv`, FRED DGS2 | (no slot in monetary.json; used only inside the derived spread)
- F4.4 Canada-US 2-year spread: **-151 bps** | as-of 2026-10-01 | `data/processed/goc_ust_spread_2y.csv` (value -1.51 pp) | `derived`
  Arithmetic: 3.27 - 4.78 = -1.51 pp = -151 bps.
- F4.5 GoC 2-year minus overnight target: **+102 bps** | as-of 2026-10-01 | `derived`
  Arithmetic: 3.27 - 2.25 = 1.02 pp = 102 bps.

Calendar note: there is no GoC yield observation for 2026-09-30 (Valet returns
blank; National Day for Truth and Reconciliation), so the previous GoC close is
2026-09-29. There is no 2026-10-02 observation in the repo for any of these yet.

### History at the comparison dates (same files)

| Date | GoC 2y | UST 2y | Spread (bps) | Overnight | 2y minus overnight (bps) |
|---|---|---|---|---|---|
| 2026-07-15 (July decision) | 2.82 | 4.13 | -131 | 2.25 | 57 |
| 2026-08-20 (old copy) | 3.02 | 4.19 | -117 | 2.25 | 77 |
| 2026-09-01 (day before decision) | 3.01 | 4.39 | -138 | 2.25 | 76 |
| 2026-09-02 (decision day close) | 3.11 | 4.39 | -128 | 2.25 | 86 |
| 2026-09-23 (2y peak) | 3.40 | 4.85 | -145 | 2.25 | 115 |
| 2026-09-28 (spread trough) | 3.37 | 4.92 | -155 | 2.25 | 112 |
| 2026-09-29 | 3.37 | 4.89 | -152 | 2.25 | 112 |
| 2026-10-01 (latest) | 3.27 | 4.78 | -151 | 2.25 | 102 |

(Sep 23 UST 4.85 is implied by the spread file: 3.40 - (-1.45) = 4.85.)

### Moves (all `derived`)

Since 2026-08-20 (old copy):
- GoC 2y: 3.27 - 3.02 = **+25 bps**
- UST 2y: 4.78 - 4.19 = **+59 bps**
- Spread: -151 - (-117) = **34 bps more negative**
- 2y minus overnight: 102 - 77 = **+25 bps**
- Overnight target: unchanged at 2.25%

Since the decision, measured from the 2026-09-02 close:
- GoC 2y: 3.27 - 3.11 = **+16 bps**
- UST 2y: 4.78 - 4.39 = **+39 bps**
- Spread: -151 - (-128) = **23 bps more negative**

Since the day before the decision (2026-09-01 close), if the writer wants the move to include decision day:
- GoC 2y: 3.27 - 3.01 = **+26 bps** (10 bps of that came on decision day itself, 3.01 to 3.11)
- UST 2y: 4.78 - 4.39 = **+39 bps**
- Spread: -151 - (-138) = **13 bps more negative**

Latest daily move: GoC 2y fell 10 bps from 3.37 (Sep 29) to 3.27 (Oct 1); UST 2y fell 10 bps from 4.88 (Sep 30) to 4.78 (Oct 1).

### Since-when comparisons (computed from the full repo history; all `derived`)

- GoC 2y at 3.40% on 2026-09-23 is the highest close since 2024-07-31 (3.46%).
- GoC 2y had not closed at or above 3.27% between 2024-11-22 (3.37%) and September 2026.
- The 2-year spread had not been at -151 bps or wider since 2025-03-17 (-151). The 2026 trough is -155 bps on 2026-09-28. The all-time widest in the file is -170 bps on 2025-02-03. So "widest since March 2025" is true; "widest on record" is false.
- Before September 2026, the last day the GoC 2y sat 102 bps or more above the overnight target was 2022-10-20 (103 bps), during the hiking cycle. The peak of this episode is 115 bps on 2026-09-23.
- On 2025-10-30, the first day after the last cut took effect, the same gap was 17 bps.
- UST 2y had not closed at or above 4.78% between 2024-06-11 (4.81%) and September 2026.

## 5. Other slots that moved and could carry the "why"

- F5.1 **US policy rate went UP.** Repo `data/raw/fed_funds.csv` steps from 3.75 to 4.00 on 2026-09-17 (the series tracks the top of the target range). Confirmed on the Federal Reserve's own table: a 25 bps increase effective September 17, 2026, to a 3.75-4.00% range (https://www.federalreserve.gov/monetarypolicy/openmarket.htm, fetched today). Before that the last change in the file was a cut on 2025-12-11.
  Derived policy-rate gap: 2.25 - 4.00 = **-175 bps** (BoC target minus top of the Fed range), as-of 2026-10-01; it was -150 bps on 2026-08-20.
  CAVEATS: (a) The existing `fomc_target_rate` card still points to the April 29, 2026 statement at 3.50-3.75% and is now stale; I did not fetch the September statement itself, so there is no card for the hike. If the writer wants to name the Fed hike, a card is needed first. (b) The monetary panel's own series `boc_fed_spread_monthly` (panel-2.tertiary) stops at 2026-08-01 with -150 bps; it does not show the hike yet. Do not cite -175 as a pipeline slot; it is `derived` from two daily files.
  OBSERVATION: most of the spread widening since Aug 20 came from the US side (+59 bps) rather than the Canadian side (+25 bps).

- F5.2 **CORRA is trading above target.** CORRA 2.30% on 2026-10-01 = 5 bps above the 2.25% target (Valet AVG.INTWO; `data/processed/corra_overnight_spread_bps.csv`, panel-4.extras7). It was exactly on target (0 bps) on 2026-08-20 through 2026-08-28, and has been 3 to 6 bps above every day since 2026-09-01 (6 bps on 2026-09-29). | `derived` (CORRA minus target); the processed file is current to 2026-10-01.
  Note: `data/raw/corra_daily.csv` is stale (ends 2026-09-01, fetched 2026-09-02) even though the processed spread file is current. Cite the processed spread, not the raw CORRA file.

- F5.3 **Balance sheet** (weekly, Wednesdays; repo as-of 2026-09-23, C$ billions; `data/raw/boc_*.csv`):

  | | 2026-08-19 | 2026-09-02 | 2026-09-16 | 2026-09-23 (repo latest) | 2026-09-30 (Valet only) |
  |---|---|---|---|---|---|
  | Total assets (V36610) | 229.699 | 223.217 | 224.001 | 235.988 | 242.555 |
  | GoC bonds (V36613) | 145.285 | 136.660 | 135.757 | 135.777 | 135.645 |
  | Repos (V44201362) | 44.551 | 46.530 | 47.482 | 59.407 | 65.929 |
  | Settlement balances (V36636) | 70.393 | 64.324 | 63.059 | 78.082 | 83.440 |

  Moves: bond holdings fell 9.0 (145.700 on Aug 26 to 136.660 on Sep 2) and have been flat since. Repos rose 11.9 in one week (47.482 to 59.407, Sep 16 to Sep 23) and another 6.5 the next (to 65.929). Settlement balances rose 15.0 in one week (63.059 to 78.082) and are at 83.440 on Sep 30.
  FRESHNESS FLAG: the repo and the monetary panel stop at 2026-09-23. Valet already has the 2026-09-30 print (fetched 2026-10-03T16:52Z). A reader-facing number citing the pipeline slot must use the Sep 23 values until the pipeline picks up Sep 30; the Sep 30 values are primary-verified but not yet in panel data.
  Context: `card:boc_floor_system_operating_range` records the Bank's C$50-70 billion settlement-balance range (January 2025 speech). Both the Sep 23 (78.1) and Sep 30 (83.4) prints are above the top of it; Sep 2 and Sep 16 were inside it.
  INTERPRETATION, unverified: repo operations rising while CORRA sits above target is consistent with the Bank adding liquidity into quarter-end funding pressure. I found no Bank of Canada statement saying so and did not look for a market notice. Treat as a hypothesis, not a citable claim.

- F5.4 **Longer yields** (Valet, as-of 2026-10-01): GoC 5y 3.62% (3.35% on Aug 20, +27 bps); GoC 10y 3.94% (3.75% on Aug 20, +19 bps). Canada-US 10-year spread -130 bps. Files `data/raw/yield_5yr.csv`, `data/raw/yield_10yr.csv`, `data/processed/goc_ust_spread_10y.csv`. Not slots in monetary.json.
  Derived: GoC 2s10s = 3.94 - 3.27 = 67 bps on Oct 1, versus 3.75 - 3.02 = 73 bps on Aug 20 (the short end rose more than the long end).

- F5.5 **Market-implied path: CANNOT BE VERIFIED.** `data/raw/corra_futures_curve.csv` was last fetched 2026-06-08 and is four months stale. There is no current futures or swap data in the repo. The only defensible market-pricing statement is the one the old copy already used: the 2-year yield relative to the overnight target (F4.5). Do not write that markets "price a hike" or put a number on hike odds.
  What can be said: the gap is 102 bps over the target, it peaked at 115 bps on 2026-09-23, and before September 2026 it was last this wide in October 2022.

## 6. Cards touched (all in `editorial/source_cards/registry.yaml`)

Updated:
- `boc_fad_holds_post_oct_2025_cut` -- appended "2026-09-02" (7 entries), verified_at, vintage_label, next_expected.

Created (Tier A; each excerpt fetched today and string-matched against the page HTML):
- `boc_fad_press_release_2026_09_02` -- decision sentence (2.25 / 2.5 / 2.20).
- `boc_fad_2026_09_02_guidance` -- "Governing Council will assess the sustainability of the economic rebound and the outlook for inflation, and is prepared to adjust monetary policy as needed."
- `boc_fad_2026_09_02_inflation_risks` -- "However, the upside risks to inflation have increased, while new tariffs make growth prospects more uncertain."

Each new card lists `src/data/sections.ts (monetary abstract)` under cited_in in
anticipation of the redraft. If the writer does not use one, the orphan check
will report it (report only, does not fail the build); delete the unused card.

Not touched: `boc_mpr_neutral_range` (still valid), `fomc_target_rate` (now stale, see F5.1), everything under `src/`.
Registry parses as valid YAML; 42 cards, no duplicate ids. I did not run the full build.

## 7. What changed since the old copy

Old tileLine: "BoC stayed at 2.25%; 2y GoCs are near 3.02% and the Canada-US spread is -117 bps."
- "stayed at 2.25%" -- still true.
- "3.02%" -- outdated. It is 3.27% (Oct 1).
- "-117 bps" -- outdated. It is -151 bps (Oct 1).
- The citation notes say "unchanged since July 15 2026 FAD decision"; the latest decision is now September 2.

Old blurb, claim by claim:
- "On hold." -- still true as a description of the rate. As a description of the stance it is weaker than it was: the Bank dropped the sentence calling the rate appropriate and added that upside inflation risks have increased.
- "stayed at 2.25% through six straight decisions" -- FALSE now. It is seven.
- "still at the floor of its 2.25 to 3.25% neutral range" -- still true.
- "and now calls the rate appropriate" -- FALSE for the current statement. That was July's language; September's statement does not contain it. The current guidance is "is prepared to adjust monetary policy as needed", after noting "the upside risks to inflation have increased".
- "Markets see it the same way" -- no longer supportable as written. The 2-year yield has moved 25 bps further above the policy rate since the old copy and sits more than a full point above it. That is the market leaning toward a higher rate, not agreeing with a hold. (Interpretation; the hard fact is the 102 bps gap.)
- "the 2-year GoC yield sits at 3.02%" -- outdated. 3.27%.
- "77 bps above the overnight rate" -- outdated. 102 bps.
- "the Canada-US 2-year spread is still deeply negative at -117 bps" -- outdated. -151 bps, the widest since March 2025, and the widening was driven mostly by US yields after the Federal Reserve raised its rate on September 17.

Old metadata:
- heroKicker "July rate decision" -- should be September.
- latestReleaseDateOverride "Jul 15, 2026" -- should be Sep 2, 2026.
- blurb date "Aug 20, 2026" -- stale.
- Citation note "No new FAD decision since; next expected ~Sep 2, 2026" -- false; that decision has happened. Next is October 28, 2026.
- Citation note flagging "migrate to a source card for the July 15 statement" -- moot if the July sentence is dropped; September statement cards now exist.

## 8. Could not verify

- Market-implied rate path (futures data in the repo is from June 8).
- Why repos and settlement balances jumped in late September (no Bank statement found; not searched exhaustively).
- The Federal Reserve's September statement text (only the Fed's rate-change table was fetched; no card exists for the hike).
- Whether any pipeline refresh is still mid-run: file timestamps were stable at 12:46-12:48 local across my reads, and BoC values matched Valet, but I did not check for a running process.
