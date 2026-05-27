# Sibley Creek â€” operating dashboard

**Last updated:** 2026-05-27 (post-reorg cleanup pass)
**Purpose:** I (Claude) read this at session start to load context and surface what matters to Jay in the terminal. Jay doesn't need to open this directly â€” ask me "where are we?" and I'll tell you.

---

## What's active right now

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
