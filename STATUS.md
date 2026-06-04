# Sibley Creek â€” operating dashboard

**Last updated:** 2026-06-04 (BoC shadow rate v1 built)
**Purpose:** I (Claude) read this at session start to load context and surface what matters to Jay in the terminal. Jay doesn't need to open this directly â€” ask me "where are we?" and I'll tell you.

---

## What's active right now

### BoC Shadow Policy Rate -- internal tool, v1 BUILT, awaiting Jay's verification
**Status (2026-06-04):** Built and dry-run complete. Reconstructs the Bank's unpublished rule-implied rate path: ToTEM III policy rule (TR-119 Table 2.3: rho=0.85, phi_pi=4.65, phi_gap=0.4) applied to April 2026 MPR projections. Internal only -- NOT on the site, NOT in pipeline.build (manual quarterly trigger, usdcad pattern). First member of the eventual no-judgment Models section.

**Artifacts:** package `pipeline/shadow_rate/` (28 tests green); punch-in workbook `work/research/shadow_rate/boc_shadow_inputs_2026Q2.xlsx` (4 sheets: a **live-formula `calc` sheet** — dense quarterly grid 2025Q4→2029Q4 whose white cells are real Excel formulas referencing the input sheets, paired with `(python)` engine-value columns and red-flagged `diff` columns for the audit handshake — placed first, regenerated on every run alongside the 3 input sheets; source_ref provenance, `verified=FALSE`). Replaced the old values-only `output` sheet (Jay: static values give no ability to audit). Chart `work/research/shadow_rate/boc_shadow_path_2026-04.html` (UNVERIFIED watermark); methodology `claude-ref/research/shadow_rate/shadow_rate_methodology_2026-04.md` (§7b updated); output `data/processed/boc_shadow_rate.csv` + sidecar.

**Dry-run result (anchor design, 2026-06-04):** output gap now anchored to BoC's published staff estimate (Valet `INDINF_OUTGAPMPR_Q`, last obs 2025Q4 = -1.0%) and rolled forward by the gap identity to the 2026Q2 seed (= -0.85). Path drifts 2.25% -> ~2.76% peak (2027Q4) -> settles ~2.70%, vs neutral midpoint 2.75 -- slightly lower than the prior placeholder run (more excess supply). Reading unchanged: the Bank's own outlook run through its own rule implies modest tightening back toward neutral; actual stance at 2.25 sits below its own framework's implied path.

**Blocking Jay (the verification gate):**
1. ~~Replace PLACEHOLDER output-gap range~~ **RESOLVED** by the anchor + roll-forward design: the gap is now fully mechanical from the Bank's published staff estimate (anchor 2025Q4 = -1.0, auto-filled from `data/raw/output_gap_mpr.csv`; Valet refetch on 2026-06-04 found no newer obs). No PDF text needed.
2. Verify the Table 2/3 transcription against the MPR (seeded from Jay's screenshots).
3. Flip `verified=TRUE`, re-run `python -m pipeline.shadow_rate.run` -> un-watermarked artifact.
Confirmed already: MPR date Apr 29 2026; neutral range 2.25-3.25 (unchanged per MPR appendix). NOT committed to git yet.

**Next steps after verification:** market-implied path overlay (CORRA futures) for v1.1; historical backfill with own estimates (later); eventual public Models page.

---

### Fiscal chartbook -- branch `fiscal-chartbook` (NOT live yet)
**Status (2026-06-02 EOD):** Built and saved on branch `fiscal-chartbook` (commit 607b4ae). Live `master` still serves the `/fiscal/` coming-soon placeholder -- do NOT push to master until Jay confirms. Jay: "probably push tomorrow."

**Done:** 4-plate fiscal section -- (1) budget balance operating-vs-capital [two-panel], (2) revenues vs expenses %GDP [merged lines], (3) federal debt %GDP [40yr], (4) gross issuance flow bills/notes/bonds [stacked]. Grey-tint bar language (no hatch), end-year round-number date axes, dashed-divider forecast convention, NO prose inside SVGs (small-mult panels use short subject labels). Reader copy passed all 3 gates and is placed. Pipeline: `pipeline/fetch/frt_fiscal_series.py` static module + panel_data specs; `fiscal.json` materialized.

**To finish before pushing tomorrow:**
1. Regenerate the 12 `frt_*.csv` (NOT on disk -- only in `git stash@{0}` + regenerable by running `frt_fiscal_series.py`). Run the pipeline to re-materialize.
2. Final full-page visual review with Jay.
3. (Optional, offered) Build a prose-in-SVG build guard -- fail build on sentence-length `<text>` in chart SVGs (closes the gap the leakage gate misses).
4. (Bigger follow-up) Conform the bespoke fiscal plates to the shared `_shared/PanelLiveChart.astro` structure -- root cause of the recurring chart drift this session.
5. Codex audit before push: the pre-PUSH hook blocks substantial-file pushes without an `editorial/audit_findings/` entry. Run `npm run audit-diff -- --by claude --task "fiscal chartbook"` (or `--no-verify` if Jay approves).
6. Merge `fiscal-chartbook` -> master = deploys live.

**Backups / incident:** Full session state also sits in `git stash@{0}` -- keep it until the branch is confirmed/pushed, then drop. Today an agent ran `git stash` mid-task and reverted the working tree; recovered via surgical `git checkout stash@{0} -- <files>`. Lesson (now in memory): main Claude runs git ops directly, never via subagents.

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
