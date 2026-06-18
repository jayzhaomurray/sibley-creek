# Sibley Creek â€” operating dashboard

**Last updated:** 2026-06-05 (May LFS: commentary published + corrected, labour section refreshed, Reuters citation)
**Purpose:** I (Claude) read this at session start to load context and surface what matters to Jay in the terminal. Jay doesn't need to open this directly â€” ask me "where are we?" and I'll tell you.

---

## What's active right now

### DEPLOY UNFROZEN + FISCAL IN CAROUSEL — fixed 2026-06-18 (master `daad8a7`, deploy green, live-verified)
The fiscal chartbook shipped panels 6-11 in `fiscal.astro` but never added their specs to `pipeline/io/panel_data.py` (only 1-5 were declared). Publish baked 6-11 into `fiscal.json` statically; the 2026-06-17 daily refresh regenerated from the incomplete spec, dropped 6-11, failed `check_panel_data_wired`, and **froze ALL deploys** — so the carousel fix (`3015272`, which drops fiscal from the splash-carousel filter) sat on master undeployed and fiscal never appeared in the homepage carousel. Fixed durably by porting the panel-6..11 spec block into master's `panel_data.py` (they read already-tracked `frt_*` derived CSVs; `_read_slot` reads them directly, no fetcher needed). Regenerated `fiscal.json` (panels reproduce identically: 48/48/48/48/8/6 records), built green locally, pushed. Deploy `daad8a7` succeeded; live homepage now carries all 8 carousel slides incl. `data-slug="fiscal"`. Lesson → memory `feedback_new_panels_need_spec_or_refresh_wipes`. **Then (also 2026-06-18, master `b7c86b4`, deploy green, live-verified):** the `/overview/` indicator grid still hard-coded a fiscal "In development" placeholder cell — replaced it with the normal live `SectionPanel` (renders Federal balance FYTD −$55.3B). Also dropped the stale `debt-service-share` print scaffold from the fiscal canon in sections.ts (pipeline stopped emitting it 2026-05-28, so it rendered as TK cells and tripped the reader-copy-leakage gate). **Note:** the `macro-fiscal` worktree branch has diverged far beyond fiscal (recession-watch, prose-engine deletions, markets/monetary rewrites) — do NOT merge it wholesale; the fiscal page itself already shipped via `25874b0`.

**Phase 3 — /overview/ fiscal indicator panel reworked (2026-06-18, master `2af7fcc`, deploy green, live-verified).** Per Jay: (1) renamed "Federal balance (FYTD)" -> "Federal budget balance" in both render spots; (2) sparkline changed line -> bars via `tileChartKind: "bars"` in sections.ts; (3) rewrote the tileLine to describe ONLY the sparkline's realized data ("The federal deficit is running wider this fiscal year than last."), citing card `dof_fiscal_monitor_debt_service_share`; (4) added three actuals-only supporting prints reading tracked `frt_*` derived CSVs — Federal debt 41.2% of GDP (-0.9pp), Program expenses 16.1% of GDP (-0.1pp), Interest 10.5% of revenue (+0.2pp), all FY2024-25. New `is_forecast` filter in `_read_series` (site_data.py) drops projection rows so tile value/delta/sparkline are realized-only; new `fiscal-year` as-of format ("FY 2024-25") and `fy-yoy` delta window added. **Freshness catch:** first pass used the annual FRT series (latest FY2024-25, -$36.3B) — Jay flagged "don't we have another year of data already?"; reverted the headline to the monthly Fiscal Monitor (`federal_budget_ytd`, FY2025-26 through Mar 2026, -$55.3B; delta -$12.1B YoY vs prior-year pace). Reinforces `feedback_always_freshest_vintage`. The unused `value_scale` field on SectionConfig remains in place (harmless). All code committed/pushed/deployed — nothing pending to ship.

### DECISION DAY 2026-06-10 — BoC held at 2.25% (fifth straight); commentary + /monetary/ live, live monitor built
- **Commentary published** (master `baeb71a`, deploy green, live-verified): `https://sibleycreek.ca/research/commentaries/boc-2026-06-10/` (Jay's byline PDF "Bank of Canada holds at 2.25%, maintains previous guidance"; take: closer to ending the hold, won't wait past September to pick a direction; watch core CPI, share >3%, med-to-long-term expectations). Newest entry → leads the splash. This was the Kit-blast link.
- **/monetary/ refreshed to the June decision** (master `9a702ae`, deploy green — note: first deploy hit a transient `actions/deploy-pages` failure with the build job GREEN; re-triggered via workflow_dispatch and it published; **pattern: build-success + deploy-step-fail = transient Pages hiccup, just re-run, don't debug content**). Take-driven refresh (NOT a mechanical cutover — monetary is policy-stance register). April's mild easing lean → the Bank's explicit two-sided **"dilemma"** framing (weak growth + inflation back toward 3%); fifth consecutive hold; plates 1-3 + lede + tile rewritten, plates 4-5 to the June-3 balance-sheet vintage (GoC bonds stepped to $146.0bn/66% on the June 1 maturity; repos range corrected to ~$15-40bn). Full 3-gate loop: fact-check caught (a) plate-3's draft "easing turn" was inverted — the CORRA path actually slopes UP into late 2026, reframed to "market still isn't pricing a near-term cut"; (b) repos-range error. Backend also fixed a real slug-drift bug (`overnight_rate_target`→`overnight_rate`) that had silently pinned the monetary tile/spread to April vintage since May 11. Hold-count card → 5 (next FAD July 15, not 29). **Follow-ups:** (1) verbatim BoC quotes still cited `derived`-with-excerpt — migrate to a `boc_opening_statement_june_2026` source card (fast-follow; fully verified, just not carded). (2) plate-2 negatives still hyphen-minus, not U+2212 (pre-existing; style flagged a canon-vs-practice discrepancy). (3) lede 76W / plate-1 78W are 1-8W over soft targets, under hard caps — style accepted.
- **BoC decision-day live monitor BUILT** (master, `pipeline/tools/boc_live_monitor.py`): one-command local dashboard (`.venv\Scripts\python.exe -m pipeline.tools.boc_live_monitor` → 127.0.0.1:8787) — CORRA-implied path + USDCAD + CGB/CGZ GoC bond futures + TSX/WTI, auto-refresh, "freeze baseline" button for since-decision deltas, per-tile latency labels. Server lives only while the terminal runs (Jay launches it himself with `! ...`). The April→June opening-statement diff was produced inline for Jay's commentary.

### MARKETS PROSE IS NOW MECHANICAL — shipped to master 2026-06-10 (merge `15a8f75`, deploy green, live-verified)
The /markets/ page text is now a deterministic FUNCTION OF THE DATA — no LLM and no human in the daily loop. Root problem fixed: prose went 4 weeks stale and FALSE ("oil still over $100" while the chart showed $92) because hand-written text can't track daily data. Now every figure renders from `data/site/panel_data/markets.json` at build time (slot-interpolated), and every qualitative claim ("above $100", "three-month high", "steepened") is a predicate-gated variant — the build picks the variant whose predicate is TRUE; a sentence with no true variant silently drops. Shipping a false claim is structurally impossible.

**Architecture (all on master):** renderer `src/lib/prose/` (`renderSectionProse("markets")`), templates `editorial/prose_templates/markets.yaml` (authored ONCE, through all 3 gates ONCE; daily renders need no review), render-dump tool `node scripts/render_prose.mjs markets`, 69 renderer tests. Page/lede/splash-tile/header all derive from the render — NO hardcoded vintage anywhere in markets sections.ts. Pipeline hardening shipped alongside: intraday-partial guard (`pipeline/fetch/yahoo.py` — never publish a Globex partial bar as a close, threshold 21:30 UTC), `fred:no-api-key` degrades gracefully instead of freezing ALL refreshes (this had silently killed the daily CI refresh 8+ runs), 105 `.meta.json` siblings now git-tracked + a gate that fails if a tracked CSV's meta is untracked (this meta gap had been poisoning panel JSON in clean checkouts → monthly fallback, source nulls), integrity gate now fails on meta-fallback signatures, GoC curve maturities co-dated to a common latest date (no false date-stamp if Valet lags one maturity), site-wide prose-vintage gate (warn). Curve chart wired to V2 (2y/5y/10y). Header reworded to descriptive register: "Where are Canadian markets trading?" (was "How are financial markets affecting Canada?" — mismatched the no-thesis register; Jay's call 2026-06-10).

**Data vintage live:** WTI 88.20 / TSX 34,411.69 / USDCAD 1.3947 (Jun 9); GoC 2y 2.87 / 5y 3.18 / 10y 3.53 (Jun 8). **Resolves** the `project_markets_page_needs_fixing` memory note (audit at `claude-ref/research/markets_audit_2026-06-09.md`; F1–F12 addressed).

**Follow-ups surfaced:** (1) **monetary** section trips the same prose-vintage warning (blurb ~39d stale vs data) — it is the next mechanical-prose cutover candidate, same playbook. (2) Pre-existing test failure on the branch (now master): `pipeline/tests/test_site_data.py::test_supporting_print_partner_share` KeyError `us-partner-share` — predates this work, belongs to whoever owns the trade-print partner-share feature; not caused by the cutover. (3) SMTP secrets still unset (optional — pipeline degrades cleanly; FRED_API_KEY already set, CI proves it).

### Labour section refreshed to May 2026 LFS — pushed 2026-06-05 (master `a3e7370`)
All 8 labour surfaces rewritten (tileLine, abstract, 6 plates) — the May print INVERTED the prior "loosening on the intensive margin" thesis (UR 6.6%, +87.8k, hours Y/Y flipped positive). Full 3-round writer + 3-gate loop; Jay reviewed every text before push; carries the correction framing (highest level this year, ~25k short of Dec 2025 — no all-time-high / shortfall-erased claims). Labour is now the splash hero ("May LFS"). Showcase PNGs re-rendered from the corrected PDF (pre-correction take was still on the splash until this push). New Tier-A card `statcan_daily_lfs_2026-05`. Data refresh: May LFS, Mar JVWS (vacancy 2.8%, spread −3.9pp), May wages (3.0% Y/Y, sharp cooling — LFS-Micro still Mar 3.1%, verified vs Valet directly), Jun 5 dailies. Pipeline fix shipped: `_http.py` TLS 1.2 cap (StatCan edge drops httpx TLS 1.3 handshakes — matches the PUMF finding) + retry now covers ConnectTimeout. **Watch:** deploy of `a3e7370` (monitor running at push time). **Follow-up idea surfaced to Jay:** once May PUMF lands, the lfs-micro replication can print a composition-adjusted wage read weeks before the BoC updates LFS-Micro — strong follow-up note to the wage plate.

### jobs-may-2026 commentary — CORRECTED 2026-06-05, live
Original overstated the level claim (said employment "back at all-time high" / shortfall "completely" made up; actual: highest level of 2026, ~25k short of the Dec 2025 record, most of the shortfall made up). Corrected PDF (`work/published/commentaries/lfs-2026-06-05-correct.pdf`, Jay's second export — first re-export still carried the all-time-high line) swapped in at `/research/commentaries/jobs-may-2026.pdf`; correction notice + updated excerpt shipped via master `bbcd301` from the `mrd-publish` worktree; deploy green; live-verified. `DataCommentary` now supports reusable `correction`/`correctedAt` fields (notice renders above the take; JSON-LD dateModified follows). **Open question:** if the subscriber blast went out with the old PDF, a follow-up note may be warranted — asked Jay, no answer yet.

### SUBSCRIBE PIPELINE — quarantine bug found + fixed, dual capture live, 5 lost subscribers recovered (2026-06-09 EOD)
Jay's friends reported no Kit follow-up email. Root cause: Kit's forms endpoint quarantines posts lacking its embed bot-token (returns 200 + {status:"quarantined", url:guard}); the old AJAX handler only checked resp.ok → showed success while Kit held every signup. **Fixes live on master:** (1) `abdcbab` handler follows the guard URL (Kit's own embed behavior); (2) `30f3c37` dual capture — subscribe forms ALSO post to the FormSubmit catcher (jay@sibleycreek.ca) via `data-backup-action`, failure shown only if both legs fail; (3) `6a55c09` flatten bracket keys for the backup leg (FormSubmit 500s on `fields[source]`). E2E verified live 2026-06-10 00:5xZ: both legs 200/success. **Recovery:** Kit API (key at `work/outreach/secrets/kit_api_key.txt`) showed the blocked attempts as `inactive` subscribers; activated via rename-husk-then-recreate (POST upsert and form-add do NOT unstick them). Jay's call 2026-06-09: activate EVERY attempted address, duplicates self-correct by unsub — final actives include sam.g@getjobber.com, toshi.okada@lankin.com, mossuh@yahoo.com AND mohsin.ghani@scotiabank.com (possible same person, both kept), mansourbarrosakho@gmail.com AND mansoursakho@gmail.com (ditto), plus jay@sibleycreek.ca (own-form test, useful for delivery checks). 19 active total. Test aliases parked as +husk / cancelled. **OPEN — Jay action:** Kit form 9515781 sends NO confirmation email (consent.enabled=false) so even successful signups land `inactive`; Jay must toggle the form's incentive/confirmation email in the Kit dashboard, OR ask Claude to add a standing API sweep that activates inactive signups (CASL-clean: form submit = express consent). Until one happens, periodically sweep inactive via the API.

### SECOND TIER-1 PRESS CITATION — Financial Post HEADLINE quote on the April trade commentary (2026-06-09)
FP story by Gigi Suhanic leads with Jay's quote in the headline ("'Biggest knock' against Canada's trade beat is that it undercuts Carney's economic pillar, says economist") + a subhead reading "'Biggest knock': Sibley Creek." Quote: "The biggest knock to this trade report is that directionally, it's moving against Prime Minister (Mark) Carney's efforts to diversify trade away from the U.S." — attributed to Jay, "chief economist at independent macroeconomic researcher Sibley Creek." NOT hyperlinked (Jay's standing call: no link-ask emails). Coverage entry shipped on trade-2026-06-09 wrapper via master `bab7592` (same DataCommentary.coverage format as the Reuters one). **Count now 2 tier-1 citations → the /about press block trigger (2-3 citations) is in range; raise with Jay when he's in site-work mode.**

### FIRST TIER-1 PRESS CITATION — Reuters quoted the May LFS commentary (2026-06-05)
Reuters jobs-day story quotes Jay by name ("chief economist at macroeconomic research firm Sibley Creek"). "In the news" coverage block shipped on the jobs-may-2026 wrapper page via master `35f4ca0` (reusable `DataCommentary.coverage` field; renders between take and PDF CTA); deploy green, live-verified. **Follow-ups RESOLVED 2026-06-09 (Jay's calls):** (1) Reuters link check done — story quotes Jay/Sibley Creek but does NOT hyperlink (verified via headed Chrome; byline Promit Mukherjee, ed. Dale Smith/Paul Simao). Jay DECLINED sending the link-ask note — his call, don't re-raise for this story. (2) Google Alerts — Jay deferred again; don't re-raise until a second tier-1 citation lands or he asks. (3) BetaKit intro — Jay: still too early; wait for a bigger story. (4) /about press block + splash press strip — unchanged, revisit at 2-3 tier-1 citations.

### BoC rule-implied shadow rate -- internal tool, v1 BUILT + post-audit hardening done, awaiting Jay's verification
**Status (2026-06-04):** Built, dry-run complete, **post-audit fixes applied**. The **ToTEM III rule-implied policy path** (TR-119 Table 2.3: rho=0.85, phi_pi=4.65, phi_gap=0.4) on April 2026 MPR projections with transparent interpolation assumptions. Renamed throughout from "reconstructs the Bank's unpublished path" to "BoC rule-implied shadow rate" -- the methodology now states explicitly this does NOT recover the Bank's internal conditioning path (judgment add-factors; MPR is conditioned on a market-implied rate path). Internal only -- NOT on the site, NOT in pipeline.build (manual quarterly trigger, usdcad pattern). First member of the eventual no-judgment Models section.

**Vintage-flexible (2026-06-04):** the tool is now vintage-flexible -- horizon (`projection_end_quarter`) and all output stamps read from the workbook, no hard-coded `2028Q4`/`2026-04`; outputs vintage-stamped (`boc_shadow_rate_<YYYY-MM>.csv` + `boc_shadow_path_<YYYY-MM>.{svg,html}`) accumulating alongside the stable current-vintage names; `make_workbook` refuses to overwrite and gains `--new-quarter` copy-forward; `run.py` globs the newest workbook. Quarterly refresh ritual documented in the methodology note (§7c). **Tests: 51 green (+10).**

**Post-audit hardening (prior pass):** (1) **Fail-closed workbook integrity** in `inputs.py` -- duplicate quarterly rows, duplicate annual years, duplicate params keys, and missing core-CPI Q4 / GDP horizon coverage all now raise naming the offending key/year (the audit's 3 reproduced failures + duplicates). (2) **Sensitivity band** (`model.run_band`) -- min/max rate across the 4 corners of {neutral_low,neutral_high} x {potential low,high}; printed as band_lo/band_hi in stdout, added as CSV columns `date,value,band_lo,band_hi`, shaded under the dashed path in the chart. (3) **Annual-average GDP cross-check** (`model.annual_average_crosscheck`) -- implied annual-avg growth from the constructed quarterly path vs MPR Table 2 published (new `gdp_annual_avg` column added to the annual sheet); WARN if |diff|>0.15pp, never fails. **Tests: 41 green (was 30; +11).**

**Artifacts:** package `pipeline/shadow_rate/` (51 tests green; vintage-flexible: horizon from `projection_end_quarter` param, vintage-stamped outputs `boc_shadow_rate_<YYYY-MM>.csv` accumulate, `make_workbook --new-quarter` copy-forward ritual, run.py picks newest workbook); punch-in workbook `work/research/shadow_rate/boc_shadow_inputs_2026Q2.xlsx` (4 sheets; annual sheet now carries `gdp_annual_avg`; **live-formula `calc` sheet** -- dense quarterly grid 2025Q4->2029Q4, white cells real Excel formulas + `(python)` engine columns + red-flagged `diff` columns, plus new note rows for the band and the cross-check; placed first, regenerated each run; source_ref provenance, `verified=FALSE`). Chart `work/research/shadow_rate/boc_shadow_path_2026-04.html` (UNVERIFIED watermark, retitled, band shaded); methodology `claude-ref/research/shadow_rate/shadow_rate_methodology_2026-04.md` (retitled; new §9 band + §10 cross-check; strengthened claim-language + inflation-concept-mismatch section); output `data/processed/boc_shadow_rate.csv` + sidecar.

**Dry-run result (post-audit, 2026-06-04):** gap anchored to BoC's published staff estimate (Valet `INDINF_OUTGAPMPR_Q`, last obs 2025Q4 = -1.0%), rolled forward to the 2026Q2 seed (= -0.85). Path drifts 2.25% -> **2.79% peak (2027Q4)** -> settles **~2.75%**, vs neutral midpoint 2.75. **Band at peak: 2.35-3.24** (±~0.44, driven by neutral ±40bp + potential). **Annual-avg cross-check: 2027 implied 1.624 vs pub 1.60 (+0.024pp PASS); 2028 implied 1.713 vs pub 1.70 (+0.013pp PASS); 2026 implied 0.972 vs 1.20 (-0.228pp WARN, flagged approximate -- 2025 seam).** Reading unchanged: the Bank's own outlook run through its own rule implies modest tightening back toward neutral; actual stance at 2.25 sits below its own framework's implied path.

~~Workbook regen pending Excel close~~ **RESOLVED 2026-06-04:** Jay closed Excel; workbook regenerated in place (`gdp_annual_avg` column + `projection_end_quarter` param added; verified=FALSE and all seeds preserved); cross-check now runs live against the real workbook.

**Param-hygiene fix (2026-06-04):** removed `inflation_converge_quarters` as a punch-in field — the t+4 inflation-lookup distance is part of the **rule's definition** (TR-119's (1/4)·Σ_{j=1..4} term), not a user input; a punched-in different value would have silently redefined the rule (the params cell had no spreadsheet dependents). Now a module constant `model.RULE_INFLATION_HORIZON_Q = 4`; dropped from the pydantic model + `make_workbook` seeding + methodology. The parser ACCEPTS the literal legacy key as a deprecated no-op (ignored with a one-line stdout warning), so both the original and Jay's cleaned v2 workbook still parse whether or not the row is deleted. **Tests: 53 green (+2: legacy key parses with warning + identical output; legacy VALUE ignored even at 8).** Calc-sheet header now reads "t+4 lookup (fixed by rule definition)". (In git via the boc-shadow-rate merge 2026-06-04 EOD.)
- **Run against Jay's cleaned v2 workbook (`--force-unverified`):** runner glob correctly picked **`boc_shadow_inputs_2026Q2_v2.xlsx`** (newest). **v2 parses CLEAN** (Jay's rearrange/clean didn't break headers/required rows); it still carries the legacy `inflation_converge_quarters` row → emits the deprecation warning, value ignored. **Path matches canonical numbers exactly: peak 2.792 @ 2027Q4, settle 2.747, band 2.064-3.430 @ 2028Q4.** **verified=FALSE** in v2 (still draft/watermarked). v2 was **open in Excel** (lock file present) → calc sheet fell back to companion `boc_shadow_output_2026Q2_v2.xlsx`; v2 input sheets untouched.

**VERIFICATION GATE PASSED (2026-06-04 EOD):** Jay verified the transcription, deleted the deprecated param row, and flipped `verified=TRUE` in v2. Real (un-watermarked) run completed against `boc_shadow_inputs_2026Q2_v2.xlsx`: canonical path (2.25 -> peak 2.792 @ 2027Q4 -> settle 2.747; band 2.064-3.430 @ 2028Q4) written to `data/processed/boc_shadow_rate.csv` + vintage copy `boc_shadow_rate_2026-04.csv`; un-watermarked chart at `work/research/shadow_rate/boc_shadow_path_2026-04.html`. **v1 is DONE.** Calc sheet embedded in v2 after Excel closed (companion file obsolete, can be deleted). **IN GIT (2026-06-04 EOD):** merged to master via branch `boc-shadow-rate` (a02c460, merge e5aa119) and PUSHED to origin; content-identical copies on `fiscal-chartbook` (through 4cfb92c) so the eventual fiscal merge is clean except this STATUS file. Workbook + charts are gitignored (disk only). Local checkout now on master.

**Backtest built (2026-06-05, informational-only):** `pipeline/shadow_rate/backtest.py` + `vintages/` (agent-transcribed MPR vintages Jul-2021 -> Jan-2026, NO verification gates per Jay -- rigor scales with surface). 18 vintages + live run; Apr-2025 excluded (two-scenario Report, no base case -> hold-rule artifact). Porcupine chart + skill metrics at `work/research/shadow_rate/backtest/boc_shadow_backtest.html`. **Skill vs random walk: h=1 0.96, h=2 0.78, h=4 0.60, h=8 0.33; dir hit 0.71.** 65 tests green. **COMMITTED + merged to master 2026-06-09** (with the in-progress market-path overlay `market_path.py`; suite 88 green).

**Next steps after verification:** market-implied path overlay (CORRA futures) for v1.1; eventual public Models page.

---

### Fiscal chartbook -- branch `fiscal-chartbook` -- SHELVED; CHARTS STILL NEED WORK (Jay 2026-06-10)
**Status:** NOT publish-ready. When Jay was asked "shall we finish the fiscal page" 2026-06-10 he pulled back: "i think the charts still needed work." This SUPERSEDES the earlier "built to spec / page is DONE" framing below — do NOT re-pitch publishing as a quick flip; it's a re-open of chart work, not a publish. Branch is now ~67 commits behind master. Next step when resumed: render the 6 plates from the branch + screenshot so Jay can point at what's off, THEN scope chart fixes. Earlier context (2026-06-04, now partly stale): page reached spec after a full-day iteration; Jay's EOD call was "shelve it, publish later." Branch at `1f477c9` (publish-flip commit already on the branch). Live `master` serves the `/fiscal/` coming-soon placeholder.

**What the page is (6 plates; story: plan -> disputed definition -> spending mechanism -> ratio agreed-flat -> carrying cost rises -> record bond program):**
1. Operating balance two-panel (plan-framing copy)
2. NEW: Budget 2025 under two definitions, two-panel ("The watchdog thinks Ottawa's definition of capital spending is too loose."; $94B annotation; same-vintage RP-2526-017-S Table 4 pair -- replaced the earlier invalid mixed-vintage SEU-vs-recast chart)
3. Rev vs spending merged lines (take inverted after fact-check caught a direction error)
4. Debt/GDP with BOTH forecast tracks (DoF flat 41.6 / PBO low-42s, June 2026 EFO) -- "the fight is not about the debt ratio"
5. NEW: Carrying cost (debt-service ratio monthly, PBO 13.1% by '31 anchor)
6. Issuance by instrument ("planned record" $612B; bills/notes/bonds footnote via new ChartbookUnit footnote slot)

All copy through 3 gates (multiple rounds) + Jay line edits; blurbs hard-cut to 40-55W; hed deck rebuilt on the subject-protagonist rule (Ottawa-as-subject once); forecast-language rule authored and CODIFIED as writing-style.md SS4.1k; explicit vintage as-of stamps on all plates; citations slot-bound (35 strict pass at last commit).

**TO PUBLISH LATER (full sequence, in order):**
1. **Freshness re-check first** (will be stale by then): PBO June 2026 EFO figures (42.5%, 13.1%, $72bn) vs any newer EFO/Fiscal Monitor/Budget; FY-currency of copy ("the fiscal year just ended" framing; FY2025-26 issuance OUTTURN may have published -- "planned record" may become a checkable actual); the PBO's PROMISED independent assessment of the operating anchor (future report per June EFO -- would supersede the May 2026 cannot-verify beat and possibly rework plate-2's land).
2. **Jay approves 3 pending source cards** (every PBO claim rests on them): `dof_vs_pbo_operating_capital_dispute` (Nov 2025 recast + Table 4 pair + "overly expansive" verbatim), `pbo_efo_june2026_debt_gdp` (June EFO year-by-year debt/GDP + DSR + per-capita), `pbo_seu_anchor_assessment_may2026` (cannot-verify). In `editorial/source_cards/_pending/fiscal/`; `npm run approve-claim` flow.
3. Overview panel flip: drop the `s.slug !== "fiscal"` filter at `src/pages/index.astro:136` + drop `noindex` in `src/pages/fiscal.astro`. Fiscal blurb/sparkline already gated + wired in sections.ts.
4. `npm run audit-diff -- --by claude --task "fiscal chartbook"` (pre-push hook requires an audit_findings entry).
5. Merge `fiscal-chartbook` -> master; verify deploy via the GitHub Actions API (NOT WebFetch).
6. Post-merge: seed Linux Playwright baselines; diagnose `build-financial-daily` master workflow (failing 2026-06-04 ~10:48, unrelated to branch).

**Known local-only artifacts (not bugs):** sandboxed local pipeline runs log statcan fetch failures + a `dof_fiscal_ytd_summary` null violation (fiscal/panel-1, monetary/panel-6 tertiary) -- CI with network is green. The 2026-06-02 `git stash@{0}` backup is superseded (branch pushed) and can be DROPPED next session.

---

### Build-Big trades-gap piece â€” launch flagship
**Status:** Pre-build. Methodology locked. Reaction sweep confirms the wedge is clean.
**Lives at:** `work/research/trades_gap/` (the working files Claude references; ask in terminal for specifics)
**Key deliverable PDFs:** `work/research/trades_gap/build_big_trades_gap_brief_v2_2026-05-26.pdf` (the brief for the economist) and the older 7-page brief PDF

**Status (2026-05-26 end-of-day):**
- Thompson briefing tomorrow morning. Agenda + handoff one-pager + pre-read email draft all ready at `work/meetings/thompson_briefing_agenda_2026-05-27.md` and `work/research/thompson_handoff_brief_2026-05-26.pdf`
- MPO project inventory done â€” 16 projects triaged, 11 Method 1, 5 Method 2, Carney-Smith is the dominant swing factor
- Wojtek validated the piece concept enthusiastically via text 2026-05-26
- Embargo Tier 1 list locked: Vieira (WSJ) / Hertzberg (Bloomberg) / Mukherjee (Reuters) / Lundy (Globe) / Suhanic (FP) â€” all 5 emails verified
- 5 cover-note templates drafted at `work/outreach/embargo_cover_notes_template_2026-05-26.md`

**Next steps:**
1. Thompson does the demand-side build (3-4 weeks from tomorrow)
2. Piece drafted as numbers materialize
3. Embargo distribution to 5 Tier 1 reporters 48-72h before publication
4. Target publication mid-to-late June, ahead of next BuildForce CMLF

---

## Operations running automatically

- **Subscriber pulls** â€” daily at 7:00 AM via Windows Task Scheduler (`SibleyCreek_PullSubscribers_Morning`). Logs at `work/outreach/recipients/scheduled_task.log`. Uses 1 of 5 daily formsubmit.co API calls (4 left for manual triggers).
- **Site rebuilds** â€” every 15 min via GitHub Actions (`.github/workflows/deploy.yml`). Daily financial-data refresh.

---

## Planned but not started

### USDCAD weekly product
**Status:** Concept captured. Not committed.
**Lives at:** `work/strategy/product/usdcad_weekly_concept.md`
**Origin:** Phil Miller (FX sales and trading at State Street) pitch.
**Shape:** Fear-and-Greed-style composite score for USDCAD; serves traders AND hedgers.
**When to revisit:** After the Build-Big trades-gap piece ships.

### MPO project tracker (potential follow-up to trades-gap)
**Status:** Identified as Wedge 1 in the Build-Big landscape map. Higher subscription value than the trades-gap piece; lower whoa.
**When:** If trades-gap launch produces sufficient attention to convert to subscriptions.

### Other potential pieces from the wedge map
- Productivity-payoff back-of-envelope ($1T crowd-in math) â€” Wedge 2
- Internal-trade flow tracker â€” Wedge 3
- CSF mandate scorecard â€” Wedge 4
- Fiscal-room model â€” Wedge 5
- Lives in: `work/research/build_big_answered_vs_open_2026-05.md`

---

## Pending operational follow-ups

### Urgent / this week
- Reporter prior-art check (Vieira, Rendell, Wall) â€” pair with "would you find this interesting" embargo soft-test
- Read 2 paywalled pieces directly: The Logic (`https://thelogic.co/news/canada-housing-shortage-nation-building-tradespeople/`) and Hill Times Crane (`https://www.hilltimes.com/2026/05/11/where-are-the-new-jobs-now-skilled-trades/503242/`)
- 10-min LinkedIn scroll on Tombe / Moffatt / BuildForce (close social-media residual)

### Near-term
- **Incorporation filed 2026-05-26** as Sibley Creek Research Inc. Waiting on Certificate of Incorporation (~1 business day). When it arrives, file ISC return within 30 days, sign first directors' resolution appointing self as officers, open business bank account, Ontario extra-provincial registration if needed. I'll surface these when the certificate lands.
- **First bi-weekly with Wojtek** â€” scheduled (Google Calendar recurring meeting, Wojtek accepted 2026-05-26). Agenda for first call drafted at `work/meetings/wojtek_bi_weekly_kickoff_2026-05-26.md` â€” 5 questions, Q1 is the warm-intro-gating question.
- **Build named "first clients" target list.** Trust collateral. Wojtek-validated path: piece reception may itself be sufficient social proof â€” confirm via Q1 of first bi-weekly. Defer building target list until that's clarified.

### Parked / awaiting trigger
- BetaKit intro via Sibin Moolasseril (post-launch milestone with real news angle)
- Kazaka Ã— Toupchinejad intro offer (wealth mgmt Ã— real estate)
- Google Alerts setup (first real citation triggers it)
- Markets page audit (slug alignment + Yahoo range + chart plates)

### Open product / strategy questions
- USDCAD product bundling: standalone or paid tier?
- USDCAD back-test outcome â†’ product positioning (trade ideas vs scorecard-only)

### Cleanup status
- 2026-05-27 pass moved root-level `chatgpt_replication/` to `claude-ref/research/usdcad/chatgpt_replication/`.
- Ignored local build/test/cache outputs were cleared outside dependency folders (`dist/`, Playwright test-results, pytest cache, repo-level `__pycache__`). `node_modules/` and `.venv/` stay installed.

---

## Where things live (for Claude reference; Jay works from terminal)

### Three top-level areas after the 2026-05-26 reorg

| Folder | What it holds | Jay opens? |
|---|---|---|
| `work/` | Jay's work: research planning, meetings, outreach, strategy, published commentaries. Gitignored. | Sometimes (PDFs, Excel, Word inside) |
| `editorial/` | AI content pipeline: blurbs, drafts, verification, source cards, published deepdive bodies. | Rarely |
| `claude-ref/` | Claude reference: wave research outputs, chart specs. | Almost never |
| `old/` | Superseded, paused, abandoned. One folder. | Never |

### Inside `work/` (more detail)

| Path | Purpose |
|---|---|
| `work/research/` | Active research pieces in planning |
| `work/meetings/` | Meeting prep + post-call captures + calendar |
| `work/outreach/recipients/` | Subscriber + reporter list (recipients.yaml) |
| `work/outreach/blast/` | Email blast log, templates |
| `work/outreach/secrets/` | API keys, SMTP config (gitignored) |
| `work/strategy/` | BD strategy, prospects |
| `work/strategy/product/` | Product roadmap concepts (USDCAD weekly, etc.) |
| `work/discovery/` | Customer discovery notes |
| `work/published/` | Shipped commentaries (.docx, .pdf, .xlsx) |

### Infrastructure (code; do not edit unless changing the site)

`src/`, `pipeline/`, `scripts/`, `data/`, `public/`, `dist/`, `tests/`, `tools/`, `design/`

---

## Workflow lifecycle for a research piece

1. **Concept / planning** â†’ `work/research/<piece-slug>/`
2. **Drafting** â†’ `editorial/drafts/`
3. **Verification (fact-check / style / surface-fit)** â†’ `editorial/verification/`
4. **Published** â†’ `editorial/published/` (deep dives) or `work/published/` (bylined commentaries)

Raw research INPUTS (PDFs, datasets) used during planning â†’ live in `claude-ref/research/` as institutional library.

---

## Claude's session ritual

**Start:** Read this file + check active piece's folder + check open follow-ups. Surface to Jay in terminal: "Here's where we are, here's what's active, here's the one or two things worth your attention today."

**Mid-session:** Track decisions. When something is resolved, delete it from follow-ups. When something new comes up, add it. Don't ask Jay to remember.

**End:** Update this file. Reflect what changed. So next-session-me can pick up cleanly.

**Background work** reports only when something needs attention.

---

## What changed in the 2026-05-26 reorg

- `business/` â†’ `work/` (with subdirs: research, meetings, outreach, strategy, discovery, published)
- `bylines/` â†’ `work/published/`
- `research/` (root) â†’ `claude-ref/research/`
- `charts/` â†’ `claude-ref/chart-specs/`
- `analyses/`, `workers/`, `_archive/` â†’ consolidated under `old/`
- `tools/` kept in place (may revive)
- 5 scripts updated to new paths (pull_subscribers.mjs, parse_subscribers.mjs, send_commentary_blast.py, scheduled_pull_subscribers.ps1, build_inflation_excel_template.py)
- `.gitignore` updated: `business/` â†’ `work/`
- Subscriber pull verified working at new paths
- Plan document at `work/reorg_plan_2026-05-26.md` if you ever want to read the full audit

## lfs-micro (2026-06-05)
- Tool COMPLETE on branch lfs-micro: BoC LFS-micro wage-growth replication (SAN 2024-23, Oaxaca-Blinder on LFS PUMF).
- Calibrated vs INDINF_LFSMICRO_M: RMSE 0.177pp full sample, 0.151pp last 18 months, corr 0.985. Spec: weighted, centered MA3, base-period reference.
- First live run 2026-06-05: May PUMF posted 8:30:40 ET (zero lag vs Daily). April 2026 reading 2.98% y/y vs BoC's published March 3.1%; May single-month 2.63%.
- 2026-06-05 PM: Jay spotted a false Dec-24-Feb-25 spike in our series. Root causes found+fixed: (1) pytest wrote a synthetic 2025-01 result into the production engine cache (test isolation bug); (2) row-misalignment in run_wls when thin-category pruning dropped rows; (3) rank-deficiency fixer returned the scaled matrix. Cache hardened: parquet fingerprints + plausibility gate (n>=20k, R2>=0.4, fail-closed). Full 125-month clean recompute done. Details: claude-ref/research/lfs_micro/calibration_report.md.
- Refresh: python -m pipeline.lfs_micro.run (seconds per new month via engine cache). Workbook: work/research/lfs_micro/lfs_micro_replication.xlsx.
- Nowcast tier DESCOPED (PUMF is same-minute as Daily); scoping banked at claude-ref/research/lfs_micro/nowcast_inputs_scoping.md.
- Unrelated: test_site_data TK-sentinel test was stale vs Jay's intentional 779d695 change (supporting prints now dropped, not TK'd, when source missing); test updated to match.
- 2026-06-05 PM (2): Codex external methodology audit -> agreed package implemented (commits c197e38/53e1d11/d49ee06/4aea6e0/8c818bd): sha256 cache fingerprints + parquet revalidation on read + calendar-gap & pair-failure fail-closed + deterministic common-column pruning; FIRMSIZE covariate ADDED (matches BoC note; fit ~unchanged at RMSE 0.180pp corr 0.986; Apr headline 2.978->3.014%); union-rule sensitivity max 0.003pp (default kept); CSV adds unsmoothed + interaction columns, May-2026 raw single-month row retained, "2016+ replication" scope label, geometric-growth relabel; --rebuild flag. History-to-2000 extension DECLINED (no nowcast value). 276 tests pass.
- 2026-06-05 PM (3): Jay spotted our series was SMOOTHER than BoC's -> confirmed BoC does not smooth (matching roughness 0.295 vs 0.293pp, no MA autocorr signature). MA3 was an artifact of calibrating on pre-fix corrupted data (outliers favored smoothing); grid was never re-run post-fix. DEFAULT_SPEC.smoothing -> "raw". Fit improved to RMSE 0.118pp, corr 0.9966, max miss 0.29pp (n=123). Newest month now carries a headline directly (no MA3 lag). LESSON: data fixes invalidate calibrations made on pre-fix data.
- Current readings (2026-05 PUMF, raw spec): Apr 2026 3.172% y/y; May 2026 2.644% y/y (BoC published Mar: 3.1%).
- 2026-06-09 FULL INDEPENDENT AUDIT (3 parallel Fable agents; reports at claude-ref/research/lfs_micro/audit_2026-06-09/): (1) PREMISE CORRECTED — BoC builds LFS-Micro on the public PUMF too (SAN 2024-23 says reproducible; master files only in robustness footnotes), so near-exact replication is achievable. (2) RESIDUAL SOLVED — BoC publishes 100*dlog (log points); we report exp(dlog)-1 (geometric pct). Same-units RMSE 0.0885pp (was 0.1178), +0.088pp bias vanishes, 3 independent signatures. Remainder = Valet 1-decimal rounding floor (0.029pp) + category-granularity sensitivity + ~0.05pp white noise. (3) CODE SOUND — adversarial audit, no blockers: WLS + Oaxaca-Blinder verified vs synthetic ground truth, all 3 past bug fixes real, metrics recomputed honestly (no off-by-one), 277/277 tests green. One MAJOR: engine cache not invalidated by methodology-code changes; 4 minors (dead tenure_bins config, stale MA3 workbook boilerplate, docstring, summary month-mismatch).
- Fix package LANDED 2026-06-09 evening (commits 4470f4f, aef460b, c8df7f5, 15d9d02 on branch; not pushed): METHODOLOGY_VERSION cache key, lp-units benchmark + same-units BoC comparisons everywhere (headline stays geometric, labeled), tenure_bins removed, MA3 boilerplate spec-conditional, summary month-guard. Full 125-month rebuild under new cache key: CSV byte-identical to pre-change (value-identity PASS). Canonical fidelity (lp-vs-lp, n=123): RMSE 0.0885pp, corr 0.9965, bias +0.037pp, max miss 0.218pp. Workbook + chart regenerated 18:10 with convention labels. Tests: 37/37 lfs_micro, full suite 410 pass (+2 pre-existing unrelated errors in pipeline/blurbs/test_fan_out.py, missing tmp_root fixture — predates branch).
- Idea shelf saved to memory (project_lfs_micro_idea_shelf): monthly early-read note, Models page, composition-story one-offs, declined history extension, descoped nowcast. Captured, NOT queued, per Jay 2026-06-09.
- 2026-06-09 EOD: Jay reviewed chart ("looks ok for now") -> MERGED to master + PROJECT PARKED. Branch lfs-micro deleted post-merge. Durable reference: this section + audit reports (claude-ref/research/lfs_micro/audit_2026-06-09/) + idea shelf in memory (project_lfs_micro_idea_shelf: monthly early-read note, Models page, composition one-offs). Refresh on a new PUMF: python -m pipeline.lfs_micro.run (seconds; cache-keyed). NOT wired into pipeline.build — manual trigger only, internal tool, nothing reader-facing.
