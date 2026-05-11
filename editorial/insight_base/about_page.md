# About page: insight base

Owner: researcher. For writer use only -- this file is fact scaffold, not
prose. Every load-bearing claim a writer puts on /about/ should trace
back to a row in this file. Hedging cues (CANON vs INFERRED vs OPEN)
tell the writer what is safe to state directly vs what needs softening
or omission.

Tier definitions:
- **CANON** -- documented in a committed project file (editorial/,
  design/, src/, pipeline/, data/SOURCES.md). The writer can state
  directly without hedging.
- **INFERRED FROM SESSION CONTEXT** -- supplied in the present task
  brief or other ephemeral session messages from the user, not in a
  committed canon doc. The writer should either (a) hedge the claim,
  (b) omit, or (c) escalate to the editorial-director for canonization
  before publish.
- **OPEN** -- writer needs a decision from the editorial-director
  before drafting.

Anchors read for this file:
- `editorial/dashboard_purpose.md` (foundation)
- `editorial/writing-style.md` (voice canon)
- `design/sleeping-giant-mark.md` (brand identity / geographic anchor)
- `editorial/auto_blurb_process.md` (Mode 2 architecture)
- `src/data/sections.ts` (current section list)
- `data/SOURCES.md` (pipeline source roster)

---

## 1. What Sibley Creek is (the publication's editorial position)

**CANON**

- Sibley Creek is "a standing, opinionated read of the Canadian macro
  picture, organized as a small set of sections that mirror how a
  Canadian institutional desk actually frames the economy, and
  refreshed on cadences that match how those sections actually move."
  (`editorial/dashboard_purpose.md` Section 1.)
- It is a **tri-modal product**: (1) live tracker (daily-refresh
  data); (2) automated event blurbs (LLM-generated interpretation
  paragraphs on data prints, human-reviewed before publish); (3)
  ad-hoc deep-dive research (human-led long-form pieces on eight
  pillars). The three modes share one set of sections, one voice, one
  canon. (`editorial/dashboard_purpose.md` Section 1 and Section 3;
  also reinforced in the 2026-05-11 changelog entry that canonicalized
  the tri-modal architecture.)
- The subject is Canada. Foreign macro (the Fed, US growth, Chinese
  demand, global oil) enters only as a transmission channel into
  Canada. ("Canada is the subject... so what for Canada."
  `editorial/dashboard_purpose.md` Section 1.)
- The publication exists "to help a reader who already knows the
  basics form a sharper view of Canada than the median Big-Six
  economics note." (`editorial/dashboard_purpose.md` Section 1.)

## 2. What Sibley Creek is NOT (writer can use for differentiation)

**CANON** (`editorial/dashboard_purpose.md` Section 1 "What this is
NOT" and Section 8 "Out of scope"):

- Not a data terminal (does not compete with StatCan, BoC Valet, or
  TradingEconomics).
- Not a news aggregator.
- Not a forecast factory.
- Not a trade-idea service.
- Not a US-macro publication with a maple-leaf wrapper.
- Not a magazine (no editions, volumes, issues, monthly cover, or
  editorial hero on the homepage).
- No retail-investor 101 (the reader is assumed to know what the BoC
  overnight rate is and how mortgage renewal works).
- No individual equities, no crypto, no FX trade calls, no commodities
  desk, no live-blogs.
- EN-only at launch; FR is a v2+ decision, resolved by Jan 2027.

## 3. Audience (writer can use to set register, NOT to list on /about/)

**CANON** (`editorial/dashboard_purpose.md` Section 2):

- P1: Bay Street allocator (primary, dominant persona). Gravitational
  centre is CPP Investments' Total Fund Management group and OTPP's
  economics and asset-mix team. Broader P1 includes BCI, PSP, CDPQ,
  IMCO, AIMCo, HOOPP, OMERS, and Toronto-based asset managers.
- P2: Policy-adjacent analyst (BoC research, DoF, PBO, provincial
  finance, OSFI, CMHC, C.D. Howe, IRPP, MLI, university research
  centres).
- P3: Serious Canadian independent investor.
- Explicitly NOT for: retail day-traders, journalists looking for a
  quote, students looking for textbook explanations, crypto-curious,
  housing doomers / permabulls, global-generalist readers.

Writer note: the /about/ page should communicate this register
**implicitly through the voice of the page itself**, not by listing
target readers. Naming CPP / OTPP by name on the public about page is
the kind of move that reads as overreach. Decision: omit named
institutions from /about/ unless editorial-director approves
otherwise.

## 4. Geographic identity (Sleeping Giant / Sibley Peninsula)

**CANON** (`design/sleeping-giant-mark.md` Sections 1-3; reinforced
in `editorial/dashboard_purpose.md` opening):

- The publication is named after **Sibley Creek**, on the **Sibley
  Peninsula** in **Sleeping Giant Provincial Park**, Silver Islet
  area, Lake Superior.
- The name signals the publication's posture: "Canadian,
  geographically specific, quietly durable, indifferent to fashion."
  (`editorial/dashboard_purpose.md` Section 1.)
- The Sleeping Giant landform is a "formation of mesas and sills" --
  flat-topped diabase plateaus separated by erosion notches; reads as
  a reclining figure (head, throat, chin, Adam's apple, body, knees,
  foot) horizontally. (`design/sleeping-giant-mark.md` Section 1, 3.)
- The brand mark is a single continuous SVG silhouette with a red dot
  at the foot terminus. The mark is the off-site brand signal:
  favicon, OG card, masthead. (`design/sleeping-giant-mark.md`
  Section 1, 5.)
- Canonical Thunder Bay vantage has the head on the RIGHT (Thunder
  Bay sits west of the peninsula). The brand mark is **flipped
  horizontally** so the red dot lands at the rightmost terminus,
  matching the chart latest-print dot convention. This is brand-system
  consistency, not cartography. (`design/sleeping-giant-mark.md`
  Section 2.)

Writer guidance: on the /about/ page the place anchor is editorial
gold -- it is a one-paragraph story that earns Sibley Creek its
non-generic name. Recommended elements: name (Sibley Creek on the
Sibley Peninsula); geography (Sleeping Giant Provincial Park,
Lake Superior); why this name (the posture line from canon: Canadian,
geographically specific, quietly durable, indifferent to fashion).
Do NOT lecture the reader on the geology; the mark earns the place.

## 5. The seven sections (current scope)

**CANON** (`src/data/sections.ts` and `editorial/dashboard_purpose.md`
Section 4):

The site currently has **seven** sections. The headline question for
each is owned by editorial-director and lives in
`src/data/sections.ts`:

1. **GDP** -- Is the Canadian economy at potential, growing, or
   contracting?
2. **Inflation** -- Is the 2% target being met, and on what measures
   and what breadth?
3. **Labour** -- How tight is the labour market, and is per-capita
   output recovering? (Demographics is folded into Labour;
   `editorial/dashboard_purpose.md` Section 4 rationale.)
4. **Housing** -- (`headlineQuestion` per `src/data/sections.ts`: "Is
   the rate-sensitive sector amplifying or dampening policy, and is
   supply arriving where population is settling?" per
   `editorial/dashboard_purpose.md` Section 4.4.)
5. **Policy** -- What is the policy stance, and is it consistent with
   the cycle? (Covers both monetary and fiscal; an eight-unit page,
   four monetary + four fiscal; `editorial/dashboard_purpose.md`
   Section 4.5.)
6. **Markets** -- What external winds are pushing on Canadian
   inflation, growth, and the CAD? (Renamed from "Financial" 2026-05-11
   per `editorial/dashboard_purpose.md` changelog.)
7. **Trade** -- Is Canada's external position structurally shifting
   under US repricing?

Writer note: the section names and headline questions are canon. The
two-line tile description (`kicker` in sections.ts) is canon too.
The /about/ page can list the seven sections by name; it should NOT
re-author the kicker or the headline question.

## 6. Voice / editorial method (for the /about/ register)

**CANON** (`editorial/dashboard_purpose.md` Section 7;
`editorial/writing-style.md` Section 1):

- **Cite primary sources.** StatCan, BoC, OSFI, CMHC, DoF, PBO,
  provincial finance ministries, C.D. Howe Business Cycle Council,
  IRPP, BIS, IMF Article IV Canada, OECD Economic Surveys.
- **Big-Six bank economics desks are competitors, not sources.** We
  read RBC, TD, BMO, Scotia, CIBC, NBC daily. We measure ourselves
  against them. We do not cite them in running prose.
- **Skeptical of consensus, not contrarian for sport.**
- **Comfortable saying we do not know.** Hedging is bad; calibrated
  uncertainty is good.
- **Numerate, not number-spammy.**
- **Plain English, technical where it must be.**
- **No breathlessness, no doom, no hype.**
- **Canadian English** (labour, centre, programme).
- **Show your work** -- methodology one click away on constructed
  charts.

Reference style desks named in `editorial/writing-style.md`: Financial
Times, The Economist, Globe and Mail Report on Business, Canadian
Press. The BoC's MPR is named as the local exemplar for declarative
numerate prose.

Writer guidance: the /about/ page voice should embody this canon, not
recite it. A short statement like "We cite Statistics Canada, the Bank
of Canada, OSFI, CMHC, the Department of Finance, the PBO, and the
provinces -- not bank morning notes" is in-canon and earns the
methodology distinction the publication runs on.

## 7. Who runs Sibley Creek (the author)

**INFERRED FROM SESSION CONTEXT (not in canon as of 2026-05-11):**

- Author is reportedly an ex-Bloomberg economics editor. (Source: user
  task brief for this session, 2026-05-11. NOT documented in any
  committed editorial/ or design/ canon doc. The deploy.yml workflow
  references a GitHub account `jayzhaomurray` but the deploy account
  is infrastructure, not a byline.)
- Distribution graph: LinkedIn 2-3k followers concentrated in
  econ-journalism / sell-side / policy. (Source: user task brief
  only.)

**Writer guidance.** The author identity has not been canonized in
any committed doc. Options for the writer:

1. **Hedge or omit**: write a publication-voiced /about/ that does not
   name the author or background. Sibley Creek can plausibly speak as
   a publication. Many institutional shops do this (FT Alphaville,
   Liberty Street Economics).
2. **Disclose with author canonized first**: route to
   editorial-director for an author-bio canon doc
   (e.g. `editorial/author_bio.md`) before drafting the named
   version. The bio sentence, the LinkedIn URL, and the prior-role
   phrasing should all be locked in canon before they appear on the
   live site.
3. **Do NOT** lift "ex-Bloomberg economics editor" verbatim into draft
   prose without canonization -- session-context facts that
   misattribute a prior employer create real reputational and
   employment-law risk and are exactly the type of fact that needs to
   be written once, by the author, with intent.

Recommended path: option 1 for the initial about-page ship (publication
voice, no named author bio), with option 2 dispatched in parallel so a
named bio can land in a v2 of the about page once the canon doc
exists.

## 8. Distribution / how readers find Sibley Creek

**INFERRED FROM SESSION CONTEXT (not in canon):**

- LinkedIn 2-3k followers concentrated in econ-journalism /
  sell-side / policy. (Source: user task brief, 2026-05-11.)

**OPEN.** The /about/ page typically does not enumerate distribution
channels in detail. If the writer wants a "where to find us" line, it
should reference what is actually live (the site itself,
`https://sibleycreek.ca`) and any other channel the
editorial-director has canonized. RSS, newsletter signup, LinkedIn
handle, etc., are open questions -- defer to editorial-director.

## 9. The Sleeping Giant mark (visual element on /about/)

**CANON** (`design/sleeping-giant-mark.md`):

- The canonical mark component is
  `src/components/brand/SleepingGiantMark.astro`.
- Two variants: `inline` (1.5px stroke, 3px dot, 120px wide) and `og`
  (2px stroke, 4px dot, 480-600px wide). The /about/ page is a
  candidate for the `og` variant given it is a brand-context page
  (Section 5.3 names the 404 hero as a comparable "rare page where
  the mark stands alone").
- Color discipline: pure ink `#000000` line, pure MTA red `#E63946`
  dot. No tints, no fills, no shadows, no frames.

Writer guidance: the /about/ page is a natural surface for the mark
at hero scale. Coordinate with art-director / frontend-designer on
exact placement when wiring; this insight base ratifies the canon
constraints, not the specific layout call.

## 10. Open questions for the writer

- **Author bio canonization** (see Section 7). Decision needed from
  editorial-director: name the author with bio, or ship
  publication-voiced /about/ for v1.
- **Author photo / portrait** -- not in scope here; defer to
  art-director if a named-bio path is chosen.
- **Contact / correspondence channel** -- the site currently has no
  /contact/ or email surface. If /about/ ends with a "reach us" line,
  the channel needs to be canonized first.
- **Mention of distribution channels** (LinkedIn, newsletter, RSS).
  Defer to editorial-director.
- **Audience naming on the public page.** Canon names CPP / OTPP as
  the gravitational centre of P1. Strong recommendation: do NOT name
  them on /about/. The publication's voice should attract that reader;
  naming them on the about page reads as overreach and as a violation
  of the editorial register the canon itself sets ("we do not
  recommend positions, tickers, or sizes"; the equivalent here is "we
  do not name our hoped-for readers").

---

End of about-page insight base. Researcher will update this file as
canon evolves.
