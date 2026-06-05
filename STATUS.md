# Sibley Creek â€” operating dashboard

**Last updated:** 2026-06-04 (BoC shadow rate v1 built + post-audit hardening)
**Purpose:** I (Claude) read this at session start to load context and surface what matters to Jay in the terminal. Jay doesn't need to open this directly â€” ask me "where are we?" and I'll tell you.

---

## What's active right now

### BoC rule-implied shadow rate -- internal tool, v1 BUILT + post-audit hardening done, awaiting Jay's verification
**Status (2026-06-04):** Built, dry-run complete, **post-audit fixes applied**. The **ToTEM III rule-implied policy path** (TR-119 Table 2.3: rho=0.85, phi_pi=4.65, phi_gap=0.4) on April 2026 MPR projections with transparent interpolation assumptions. Renamed throughout from "reconstructs the Bank's unpublished path" to "BoC rule-implied shadow rate" -- the methodology now states explicitly this does NOT recover the Bank's internal conditioning path (judgment add-factors; MPR is conditioned on a market-implied rate path). Internal only -- NOT on the site, NOT in pipeline.build (manual quarterly trigger, usdcad pattern). First member of the eventual no-judgment Models section.

**Vintage-flexible (2026-06-04):** the tool is now vintage-flexible -- horizon (`projection_end_quarter`) and all output stamps read from the workbook, no hard-coded `2028Q4`/`2026-04`; outputs vintage-stamped (`boc_shadow_rate_<YYYY-MM>.csv` + `boc_shadow_path_<YYYY-MM>.{svg,html}`) accumulating alongside the stable current-vintage names; `make_workbook` refuses to overwrite and gains `--new-quarter` copy-forward; `run.py` globs the newest workbook. Quarterly refresh ritual documented in the methodology note (§7c). **Tests: 51 green (+10).**

**Post-audit hardening (prior pass):** (1) **Fail-closed workbook integrity** in `inputs.py` -- duplicate quarterly rows, duplicate annual years, duplicate params keys, and missing core-CPI Q4 / GDP horizon coverage all now raise naming the offending key/year (the audit's 3 reproduced failures + duplicates). (2) **Sensitivity band** (`model.run_band`) -- min/max rate across the 4 corners of {neutral_low,neutral_high} x {potential low,high}; printed as band_lo/band_hi in stdout, added as CSV columns `date,value,band_lo,band_hi`, shaded under the dashed path in the chart. (3) **Annual-average GDP cross-check** (`model.annual_average_crosscheck`) -- implied annual-avg growth from the constructed quarterly path vs MPR Table 2 published (new `gdp_annual_avg` column added to the annual sheet); WARN if |diff|>0.15pp, never fails. **Tests: 41 green (was 30; +11).**

**Artifacts:** package `pipeline/shadow_rate/` (51 tests green; vintage-flexible: horizon from `projection_end_quarter` param, vintage-stamped outputs `boc_shadow_rate_<YYYY-MM>.csv` accumulate, `make_workbook --new-quarter` copy-forward ritual, run.py picks newest workbook); punch-in workbook `work/research/shadow_rate/boc_shadow_inputs_2026Q2.xlsx` (4 sheets; annual sheet now carries `gdp_annual_avg`; **live-formula `calc` sheet** -- dense quarterly grid 2025Q4->2029Q4, white cells real Excel formulas + `(python)` engine columns + red-flagged `diff` columns, plus new note rows for the band and the cross-check; placed first, regenerated each run; source_ref provenance, `verified=FALSE`). Chart `work/research/shadow_rate/boc_shadow_path_2026-04.html` (UNVERIFIED watermark, retitled, band shaded); methodology `claude-ref/research/shadow_rate/shadow_rate_methodology_2026-04.md` (retitled; new §9 band + §10 cross-check; strengthened claim-language + inflation-concept-mismatch section); output `data/processed/boc_shadow_rate.csv` + sidecar.

**Dry-run result (post-audit, 2026-06-04):** gap anchored to BoC's published staff estimate (Valet `INDINF_OUTGAPMPR_Q`, last obs 2025Q4 = -1.0%), rolled forward to the 2026Q2 seed (= -0.85). Path drifts 2.25% -> **2.79% peak (2027Q4)** -> settles **~2.75%**, vs neutral midpoint 2.75. **Band at peak: 2.35-3.24** (±~0.44, driven by neutral ±40bp + potential). **Annual-avg cross-check: 2027 implied 1.624 vs pub 1.60 (+0.024pp PASS); 2028 implied 1.713 vs pub 1.70 (+0.013pp PASS); 2026 implied 0.972 vs 1.20 (-0.228pp WARN, flagged approximate -- 2025 seam).** Reading unchanged: the Bank's own outlook run through its own rule implies modest tightening back toward neutral; actual stance at 2.25 sits below its own framework's implied path.

~~Workbook regen pending Excel close~~ **RESOLVED 2026-06-04:** Jay closed Excel; workbook regenerated in place (`gdp_annual_avg` column + `projection_end_quarter` param added; verified=FALSE and all seeds preserved); cross-check now runs live against the real workbook.

**Param-hygiene fix (2026-06-04):** removed `inflation_converge_quarters` as a punch-in field — the t+4 inflation-lookup distance is part of the **rule's definition** (TR-119's (1/4)·Σ_{j=1..4} term), not a user input; a punched-in different value would have silently redefined the rule (the params cell had no spreadsheet dependents). Now a module constant `model.RULE_INFLATION_HORIZON_Q = 4`; dropped from the pydantic model + `make_workbook` seeding + methodology. The parser ACCEPTS the literal legacy key as a deprecated no-op (ignored with a one-line stdout warning), so both the original and Jay's cleaned v2 workbook still parse whether or not the row is deleted. **Tests: 53 green (+2: legacy key parses with warning + identical output; legacy VALUE ignored even at 8).** Calc-sheet header now reads "t+4 lookup (fixed by rule definition)". NOT committed to git.
- **Run against Jay's cleaned v2 workbook (`--force-unverified`):** runner glob correctly picked **`boc_shadow_inputs_2026Q2_v2.xlsx`** (newest). **v2 parses CLEAN** (Jay's rearrange/clean didn't break headers/required rows); it still carries the legacy `inflation_converge_quarters` row → emits the deprecation warning, value ignored. **Path matches canonical numbers exactly: peak 2.792 @ 2027Q4, settle 2.747, band 2.064-3.430 @ 2028Q4.** **verified=FALSE** in v2 (still draft/watermarked). v2 was **open in Excel** (lock file present) → calc sheet fell back to companion `boc_shadow_output_2026Q2_v2.xlsx`; v2 input sheets untouched.

**Blocking Jay (the verification gate):**
1. ~~Replace PLACEHOLDER output-gap range~~ **RESOLVED** by the anchor + roll-forward design (anchor 2025Q4 = -1.0, auto-filled from `data/raw/output_gap_mpr.csv`).
2. Verify the Table 2/3 transcription against the MPR (seeded from Jay's screenshots) -- now including the annual-average GDP row (1.2/1.6/1.7).
3. Flip `verified=TRUE`, re-run `python -m pipeline.shadow_rate.run` -> un-watermarked artifact.
Confirmed already: MPR date Apr 29 2026; neutral range 2.25-3.25 (unchanged per MPR appendix). NOT committed to git yet.

**Next steps after verification:** market-implied path overlay (CORRA futures) for v1.1; historical backfill with own estimates (later); eventual public Models page.

---

### Fiscal chartbook -- branch `fiscal-chartbook` -- BUILT TO SPEC, SHELVED 2026-06-04
**Status:** Page is DONE after a full-day iteration cycle with Jay (2026-06-04). Jay's EOD decision: "shelve it for now. we'll publish the page at a later date." Branch pushed to origin at `572d695`. Live `master` still serves the `/fiscal/` coming-soon placeholder. Do NOT merge until Jay says publish.

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
