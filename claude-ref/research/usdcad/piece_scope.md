# Piece scope — "The oil money stopped coming home" (working frame)

Scoped 2026-06-05 in conversation with Jay. Status: skeleton complete, NO data work done yet.
Kill-test required before drafting (see below).

## Thesis (Jay's original contribution)

Canada's export-currency link is broken by OWNERSHIP/PAYOUT STRUCTURE, not by commodity.
Oil is the documented instance (St-Arnaud); gold is the unclaimed test case.

## The two rival narratives being arbitrated

1. **Flows / St-Arnaud**: post-2014 capital discipline -> oil revenue goes to
   dividends/buybacks -> increasingly foreign (US) shareholder base -> USD revenue
   never converts to CAD -> link severed structurally. FULLY PUBLISHED by St-Arnaud
   (C.D. Howe Dec 2022 w/ Hodgson; Alberta Central "petro-currency no more";
   Bloomberg Apr 2026). Cite, don't restate. Idea reached Jay via drinks with
   St-Arnaud; published work means clean citation, no attribution problem.
2. **Shock-source / Scotiabank (Gervais, Apr 2026)**: channel intact; shocks changed.
   Post-shale oil moves are supply-driven; supply-driven oil doesn't lift CAD.
   Demand-driven rallies should still work.

Prior art file: `st_arnaud_prior_art.md` (same folder) — includes gold-beta sweep.
Key gold prior art: Desjardins / Mirza Shaheryar Baig "Gold and the Loonie" Sep 26 2025
(gold ~12% of weekly USDCAD variance; no beta/rolling series published). Cite as
observation, rebuild numbers from primary sources. Ownership-structure-applied-to-gold
lane is EMPTY (verified 2026-06-05).

## The three discriminating tests (each = one reader-legible chart + appendix stats)

1. **"The petrocurrency trade" (the referee).** Classify weeks: oil up + global
   equities up = demand ("good-news") rally; oil up + equities down = supply.
   Weekly freq; S&P/MSCI World NOT TSX (energy contamination); dead zone |oil| < ~1%.
   Chart: cumulative return of "buy CAD every good-news oil week," 2000-present.
   Scotiabank right -> line keeps climbing post-2014. St-Arnaud right -> flat forever
   after 2014-15. The 2021 reopening rally is the discriminating scene (demand-driven,
   loonie shrugged). WARNING: 2008-vs-2022 contrast is confounded (demand vs supply
   spike) — it is Scotiabank's evidence, not ours. Benchmark check: NY Fed Oil Price
   Dynamics decomposition (downloadable). Appendix: interaction-dummy OLS, Chow break
   test, Newey-West SEs.
2. **"Where the barrel money went" (the paper trail).** Two ledgers: (a) top-down
   StatCan BoP investment-income debits vs energy export revenue, pre/post 2014
   (mind spurious regression — both trend; Wooldridge ch18 handling); (b) bottom-up
   ~15 large listed producers from filings: revenue, capex, dividends+buybacks,
   foreign-ownership share, annual to ~2005. Chart: cents per revenue dollar to
   Canadian capex vs to shareholders, lines crossing 2014-15. Rebuild St-Arnaud's
   25%->9% reinvestment and 62%->78% foreign ownership from primary sources.
3. **"When the traders gave up" (the transmission).** CFTC CoT, CAD futures,
   leveraged-funds net position (TFF back to 2006). Rolling correlation of weekly
   position changes vs oil returns. Chart: the line falling to zero; date the death.
   If death = 2015-16 (capex collapse), timing ties expectations channel to flows
   mechanism. Caveat (one sentence in piece): futures = small window on OTC market.

## Gold coda (the original lane)

Question: how much gold beta is the loonie MISSING? Predicted CAD demand under full
conversion of gold export revenue vs observed beta; miner ownership/payout data
explains the gap. Works under either verdict (same disease / no mechanism). Gold is
the fact neither narrative was built on — Lakatos/holdout logic.

## Pre-committed frames (written BEFORE data; do not let data pick the story)

- St-Arnaud wins: **"The oil money stopped coming home."** Branch-plant nerve.
- Scotiabank wins: **"The loonie never stopped being a petrocurrency — oil stopped
  being oil."**
- Ending either way: published predictions for the next demand-driven oil rally,
  to be publicly scored (franchise format: narrative scorecard).

## House method (candidate methodology-page content, user-authored)

1. Find two stories that disagree about one number.
2. Get the number; it must be visible in a chart ("interocular standard").
3. Write both stories before you look (pre-commitment wall).
4. Publish picture + story + recipe so anyone can check.
5. Judge stories by facts they weren't built on; write predictions down before
   facts arrive.
Lineage if ever needed: Platt strong inference; Berkson/Edwards-Lindman-Savage
interocular trauma test; Tukey EDA; McCloskey rhetoric; Lakatos novel facts; Tetlock
scoring.

## Sequencing

1. KILL-TEST FIRST (cheap): build classifier + cumulative petrocurrency-trade line.
   Look at it. If no clean break, rescope before writing anything.
   -> RUN 2026-06-05. Verdict: MURKY, leaning St-Arnaud. Cumulative line still climbs
   post-2014 (slower); rolling demand-beta HALVED but break dates ~2020, NOT 2014-15 —
   timing mismatch with the capex mechanism. 2021 reopening barely moved CAD (bad for
   Scotiabank). Crux has moved to DATING the break: CoT test now decisive. Needed
   refinement: equity-controlled beta (demand-week gains may be generic risk-on; R2
   only 0.03-0.04 in both eras). Results: kill_test_results.md; charts in
   work/research/usdcad/; script pipeline/research/usdcad/kill_test.py.
2. If break is clean: BoP pulls, miner filings, CoT series, gold beta.
3. Charts to art-director spec; copy through writer + 3 gates as usual.
4. Pre-publication: send draft to St-Arnaud (relationship move; flattering, builds
   senior web). Reader fit: Phil (State Street FX sales/trading) is the target reader.

## Data sources

- USDCAD: BoC Valet (already in pipeline). WTI/Brent: FRED. Equities: FRED/Yahoo.
- NY Fed Oil Price Dynamics Report (benchmark decomposition).
- StatCan BoP quarterly; StatCan capex surveys.
- CFTC CoT TFF weekly (free, 2006+).
- Producer filings (SEDAR+) for payout/ownership; Desjardins Sep 2025 for comparison.
