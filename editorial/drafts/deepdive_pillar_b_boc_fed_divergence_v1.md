# Pillar B deep dive -- BoC vs. Fed: how far can the divergence run? -- v1 draft

Author: writer (macro-research-department / Sibley Creek).
Style polish: style-editor. Chart inserts: chart-builder.
Date: 2026-05-11.
Status: v1 draft. Prose with inline chart placeholders at natural
break points. ASCII-only.

Anchors:
- Editorial canon: `editorial/dashboard_purpose.md` Section 5, Pillar B;
  Section 4.5 monetary sub-surface (units 1-4, especially unit 3 the
  BoC-Fed spread); Section 7 (voice; Mode 3 deep-dive register).
- Voice: `editorial/writing-style.md` Section 1, Section 7 Mode B,
  Section 2 (numbers and dates), Section 4 (institution names),
  Section 8 (citation discipline; no Big-Six in running prose).
- Verified anchors: `editorial/insight_base/pillar_b_boc_fed_divergence.md`
  (researcher tier table; tier conventions: CANON / INFERRED / OPEN).
  Six chart specifications (B1-B6) commissioned to chart-builder.
- Primary citations of record: BoC press release 2026-04-29; BoC Valet
  (V39079 overnight target, GoC 2y, GoC 10y); FRED (FEDFUNDS, DFEDTARU,
  DFEDTARL, DGS2); BoC CSCE (consumer 1y, 5y expectations); BoC BOS
  (firms expecting CPI above 3%); StatCan Table 18-10-0004-01 (headline
  CPI); Devereux, Dong, Tomlin, BoC WP 2015-31 (exchange-rate
  pass-through).

Six inline chart inserts are commissioned in this draft:
1. Policy-rate divergence, four decades (`/charts/pillar-b/policy-rate-divergence.svg`)
   -- Lede close.
2. The 2y curve spread at its post-2001 floor
   (`/charts/pillar-b/2y-spread-percentile.svg`) -- Section I close.
3. USDCAD has strengthened despite divergence
   (`/charts/pillar-b/usdcad-vs-2y-spread.svg`) -- Section II close.
4. Inflation expectations are moderating, not breaking
   (`/charts/pillar-b/expectations-anchor.svg`) -- Section III close.
5. Pass-through cascade (`/charts/pillar-b/passthrough-cascade.svg`)
   -- Section IV close.
6. The 2024-25 precedent (`/charts/pillar-b/precedent-2024-25.svg`)
   -- Section V close.

Voice scratch:
- Mode 3 deep-dive register. Argument-bearing; takes a side; willing
  to say where the data ends. No Big-Six citation in running prose
  -- the Devereux et al. 2015 BoC working paper is the citation of
  record for pass-through.
- The central thesis: the divergence can run further than the
  FX channel currently suggests, because the binding constraint is
  the inflation-expectations chain, not the loonie. The 2024-25
  episode is the operating precedent; 1997-98 is the contingent
  precedent that would only re-activate if CAD broke 1.45+
  decisively. Today's CAD has done the opposite.
- Gaps the researcher flagged and the writer must hedge or work
  around: 10y UST not in pipeline (work around -- the 2y carries
  the transmission argument); credit spreads not
  visible in `data/raw/` (treat the credit channel as a structural
  box, not a quantified channel); OIS path and Fed dot plot not
  wired (argue structurally around the 4-meeting forward, not
  numerically). MPR canonical "10% CAD = X pp CPI" rule of thumb is
  unsourced -- pass-through cascade in Section IV must hedge the
  CPI step.

---

## 1. Page header copy

- Title (deep-dive voice; sentence case; declarative):

  **The divergence can run further than the loonie is signalling**

- Deck (one sentence; sets the question and the answer):

  *The BoC-Fed policy spread sits at the 8th percentile of three
  decades of history and the 2y curve spread at the 5th percentile
  of two decades, but USDCAD is at the 67th and strengthening; the
  binding constraint on how long the BoC can hold at 2.25% is not
  the FX channel but the inflation-expectations chain, which is
  moderating, not breaking.*

- Date stamp: *Published 2026-05-11. Data vintage: BoC press release
  April 29, 2026 (overnight rate target held at 2.25%); BoC Valet
  daily series V39079 (overnight target), 2y GoC, 10y GoC to close
  2026-05-07; FRED FEDFUNDS, DFEDTARU/DFEDTARL midpoint, DGS2 to
  close 2026-05-07; BoC Valet FXUSDCAD to 2026-05-01; BoC CSCE Q1
  2026 (released April 2026); BoC BOS Q1 2026 (released April 2026);
  StatCan Table 18-10-0004-01, headline CPI March 2026 release;
  Devereux, Dong, Tomlin, BoC Working Paper 2015-31.*

---

## 2. Lede

> The Bank of Canada's overnight rate target sits at 2.25%, where
> it has held for six consecutive meetings since October 29, 2025.
> The Federal Reserve's effective funds rate sits at 3.625%, the
> midpoint of a 3.50 to 3.75% target range last reset by a 25 bps
> cut in December 2025. The BoC-Fed policy-rate spread is therefore
> negative 137.5 bps. In the post-1996 monthly distribution of that
> spread, today's reading sits at the 8th percentile. At the 2y
> point on the curve, GoC yields 2.94% against UST at 3.92%; the
> 98 bps gap sits at the 5th percentile of the post-2001 daily
> distribution. This is a deep-divergence episode by any sensible
> measure.
>
> The puzzle is what is not happening. The naive transmission story
> -- wider negative rate spread, weaker loonie, imported goods
> inflation, BoC capitulation -- is not playing out. USDCAD closed
> May 1 at 1.3575, the 67th percentile of the post-1990 daily
> distribution. The loonie has strengthened through the spring of
> 2026, moving from above 1.40 earlier in the cycle down to roughly
> 1.36. The BoC's own April 29 statement noted, in characteristic
> understatement, that "the Canada-US exchange rate has been
> relatively stable." The canary in the FX coal mine is not singing.
>
> A working hypothesis explains the gap. The rate-differential
> channel is one of several forces acting on USDCAD; it is not the
> only one. Through the first half of 2026, broad USD weakness
> against the major DM crosses and resilient commodity terms of
> trade have been pulling in the opposite direction with at least
> as much force. The loonie is doing what it does when commodity
> support is intact and the US dollar is leaking against majors:
> it is holding, even with the rate spread against it. The fact
> that the spread can be at the 8th percentile while the currency
> sits at the 67th is the most interesting datum in the Canadian
> macro picture today.
>
> The question this piece answers is how long that gap can persist
> and what would close it. We argue three things. First, the FX
> channel is not the binding constraint on the BoC right now -- the
> Bank itself is not flagging it, the percentile data confirms the
> Bank's read, and the 2024-25 episode demonstrated that BoC can
> tolerate a -170 bps 2y spread without capitulating. Second, the
> binding constraint is the inflation-expectations chain -- the
> consumer 1y and 5y CSCE measures and the BOS firm distribution
> -- and that chain is currently moderating toward target, not
> breaking. Third, the 2024-25 episode is the operating precedent,
> not 1997-98; the resolution then came from Fed convergence, not
> BoC capitulation, and the structural setup for a repeat is
> already in place. Section VI names what would change our mind.

![BoC overnight rate target and Fed funds effective rate, monthly, 1996 through April 2026. Spread (BoC minus Fed) plotted as bottom panel; current spread minus 137.5 bps sits at the 8th percentile of the post-1996 monthly distribution.](/charts/pillar-b/policy-rate-divergence.svg)

*BoC overnight rate target (Valet V39079) and Fed funds effective
rate (FRED FEDFUNDS), monthly. Bottom panel: BoC minus Fed, in
percentage points. January 1996 through April 2026. Annotated
episodes: 1997-98 trough at minus 2.51 pp (April 1997); 2015-17
oil-shock divergence; 2024-26 current cycle. Source: Bank of Canada,
Federal Reserve Economic Data. Vintage: 2026-04-30.*

---

## 3. Section I -- Where the divergence stands

The depth of the gap, in the historical distribution.

> Three rate spreads carry the divergence story. The policy-rate
> spread is the headline: BoC at 2.25% against Fed funds effective
> at 3.625%, for a gap of negative 137.5 percentage points. In the
> post-1996 monthly distribution -- the longest period for which
> both targets are continuously comparable -- this reading sits at
> the 8th percentile. The all-time minimum was negative 2.51 pp in
> April 1997, in a different regime that resolved with a 100 bps
> BoC intermeeting hike on August 27, 1998 when USDCAD broke 1.50.
> The all-time maximum was positive 2.03 pp in June 2003. Today is
> deep but not unprecedented.
>
> The 2y curve spread is the sharper read of market-implied policy
> divergence. GoC 2y yields 2.94% against UST 2y at 3.92%, a gap of
> negative 98 bps to close May 7, 2026. In the post-2001 daily
> distribution this reading sits at the 5th percentile. The
> all-time minimum was negative 170 bps on February 3, 2025 -- a
> level reached during the 2024-25 episode that this piece argues
> is the operating precedent. Today is near the historical floor,
> roughly 70 bps off it; that is not the same as being at it. The
> all-time maximum on the same series was positive 226 bps on April
> 1, 2003.
>
> The 10y leg is the gap in the data. GoC 10y is at 3.53%; the 10y
> UST series is not currently in the project's data pipeline. The
> 10y-10y spread cannot be quoted from primary sources we have
> fetched, and we decline to estimate it. What can be said: the
> GoC 10y-2y slope sits at positive 59 bps, modestly steep,
> consistent with a normal-cycle term structure. With the BoC at
> 2.25% and the 10y at 3.53%, the long end is pricing a meaningful
> term premium and an expected reversion of policy back toward
> neutral. That observation matters for Section II's discussion of
> what would force a change in posture.
>
> Two readings follow. First, in plain terms, this is a deep
> divergence by historical standards but not without precedent --
> 1997 ran wider on the policy spread, and the 2y curve gap ran
> sharper in February 2025. Second, the percentile framing matters
> because the prior cycle's resolution -- the Fed catching up to
> the BoC, not the BoC reversing -- is a fact about what the
> distribution can do, not just a fact about what it has done.

![2y GoC minus 2y UST, daily, January 2001 through May 2026. Latest value minus 98 bps. Horizontal dashes at the post-2001 5th, 50th, and 95th percentiles. Trough of minus 170 bps on February 3, 2025 annotated.](/charts/pillar-b/2y-spread-percentile.svg)

*2y GoC yield minus 2y UST yield, in percentage points. Daily, on
common-trading-day calendar. January 2001 through May 7, 2026.
Source: Bank of Canada Valet (2y GoC); FRED DGS2 (2y UST). Vintage:
2026-05-07.*

---

## 4. Section II -- Why the FX channel is not binding

The transmission story that is not playing out, and why.

> The textbook story is mechanical. Wider negative rate spread,
> capital outflow pressure, weaker loonie, higher Canadian-dollar
> price of imported goods, lift in headline CPI, BoC forced to
> back off because the import-price channel is doing its work
> against the target. This is not happening. The data say so, and
> the BoC says so.
>
> USDCAD closed May 1 at 1.3575, the 67th percentile of the
> post-1990 daily distribution. The loonie has strengthened through
> the first four months of 2026, moving from above 1.40 in
> mid-cycle down to roughly 1.36. Over the same period the
> BoC-Fed policy spread widened. The two series are moving in
> opposite directions to what the textbook would predict. The
> BoC's April 29 statement notes the exchange rate has been
> "relatively stable" -- a statement the Bank would not make if
> it considered FX a binding constraint on policy. We take the
> Bank at its word; the data corroborate it.
>
> The mechanical explanation for the decoupling is that the
> rate-differential channel is one input into USDCAD, not the only
> input. Two other channels are dominating it through spring 2026.
> The first is broad USD weakness against the major DM crosses;
> the DXY has been on the back foot through Q1 and into Q2, and
> when the dollar is leaking against majors broadly, the loonie
> tends to participate even when the bilateral rate differential
> argues against it. The second is commodity terms of trade. WTI
> has been firm through Q1 and into Q2 2026; Canada's terms-of-trade
> position has been supportive. With both channels pulling in the
> same direction against the rate-differential channel, the net
> on USDCAD has been a strengthening currency.
>
> The pass-through arithmetic confirms that today's setup is not
> a CPI threat. Devereux, Dong, and Tomlin in BoC Working Paper
> 2015-31 estimate that a 1% Canadian-dollar depreciation lifts
> Canadian import prices by 0.59% on average, with apparel
> pass-through at roughly 82% and vegetables at roughly 21%; goods
> invoiced in US dollars show substantially higher pass-through
> than goods invoiced in Canadian dollars. The link from import
> prices to headline CPI is a separate step the BoC has cited
> across MPR cycles as a rule of thumb but does not publish in a
> single canonical box, and we decline to assert a precise CPI
> coefficient on it. The structural fact is that for the
> pass-through loop to bind on CPI, the currency move must be
> material in size and durable in time. Today's CAD is broadly
> flat year-to-date. The loop is dormant.
>
> One subtler observation. The FX channel can be not binding
> today and still be the channel that binds tomorrow. The
> threshold is not the spread level; it is the CAD level. The 1998
> precedent involved USDCAD breaking 1.50 to force an intermeeting
> hike. The 2024-25 precedent saw USDCAD touch 1.45-plus without
> forcing a BoC back-off. Today's 1.36 sits well inside the range
> in which the BoC has historically been willing to tolerate a
> wide negative spread. Section VI names the level at which the
> calculation would change.

![Top panel: USDCAD daily, January 2024 through May 2026. Bottom panel: 2y GoC-UST spread daily, same window. The two series are moving in opposite directions through Q1 and Q2 of 2026.](/charts/pillar-b/usdcad-vs-2y-spread.svg)

*Top: USDCAD spot rate (BoC Valet FXUSDCAD), daily. Bottom: 2y
GoC-UST spread, in percentage points, daily. January 2, 2024
through May 1, 2026 (FX), May 7, 2026 (spread). Source: Bank of
Canada Valet; FRED. Vintage: 2026-05-07.*

---

## 5. Section III -- What is binding instead

The inflation-expectations chain, which the BoC actually reacts to.

> The Bank's reaction function in this cycle has not been keyed to
> the bilateral rate spread or the FX level. It has been keyed to
> the inflation-expectations chain: the CSCE consumer 1y and 5y
> series, the BOS distribution of firms expecting CPI above 3%,
> and the headline CPI print itself. As long as those move in the
> right direction, the Bank has runway to hold at 2.25% and tolerate
> the spread. They are moving in the right direction.
>
> CSCE consumer 1y inflation expectations sat at 3.98% in Q1 2026,
> down from 4.10% in Q4 2025 and 4.0% in Q3 2025. CSCE consumer
> 5y expectations sat at 3.02% in Q1 2026, down from 3.09% in Q4
> 2025 and 3.67% in Q3 2025. The 5y measure has moved more than 60
> bps over two quarters and is now within touching distance of a
> 2-handle reading. The BOS share of firms expecting CPI above 3%
> sat at 11% in Q1 2026, down from 16% in Q4 2025 and 18% in Q3
> 2025. All three of these series are moderating; none are
> breaking. The composition of the move is consumer-led and
> firm-confirmed, the configuration that makes the BoC most
> confident an expectations process is genuinely re-anchoring.
>
> Headline CPI cooperates with the read. The latest StatCan print
> placed headline CPI Y/Y at 2.32% in March 2026. The BoC's April
> 29 statement projects CPI rising to "about 3%" in April on a
> gasoline base effect, then declining back toward 2% by early
> 2027. The April print is the first watchpoint of this Pillar's
> forward path. If April lands at or below the Bank's "about 3%"
> guide and the subsequent prints decline, the expectations
> framework holds. If April prints materially above 3% and the
> decline does not arrive on schedule, that is the first test.
>
> The chain matters because of how the BoC's reaction function is
> actually structured. The Bank does not target the rate spread.
> The Bank does not target USDCAD. The Bank targets headline CPI
> at 2% over the medium term, with attention to whether
> expectations are anchored at that level. When expectations are
> anchored and CPI is on a path to 2%, the Bank can absorb a wide
> negative rate spread without the bilateral macroeconomics forcing
> its hand -- because the channel the spread would otherwise bind
> through (FX-to-import-prices-to-CPI) requires expectations to
> de-anchor for the second-round effects to matter. As long as the
> 5y CSCE keeps moving toward 2%, the BoC has runway.
>
> One nuance the data demands. "Moderating, not breaking" is a
> read on the trend, not a claim that the chain is invulnerable.
> The 5y CSCE at 3.02% is still above the 2% target; the consumer
> 1y at 3.98% is materially above it. A re-acceleration in either
> series, particularly the 5y, would change the calculation
> faster than a CAD move of comparable apparent severity. The
> binding constraint on the BoC is the expectations chain because
> the expectations chain feeds back into the CPI path; the FX
> channel only matters insofar as it would force expectations to
> re-anchor higher. Today it is not doing that.

![CSCE consumer 1y and 5y inflation expectations (left axis, percent), and BOS share of firms expecting CPI above 3% (right axis, percent). Quarterly, Q1 2021 through Q1 2026.](/charts/pillar-b/expectations-anchor.svg)

*BoC Canadian Survey of Consumer Expectations: 1-year-ahead and
5-year-ahead inflation expectations, left axis. BoC Business
Outlook Survey: share of firms expecting CPI above 3%, right axis.
Quarterly, Q1 2021 through Q1 2026. Source: Bank of Canada CSCE
and BOS Q1 2026 releases. Vintage: 2026-04.*

---

## 6. Section IV -- The pass-through cascade, sized

A structural sketch of what a CAD move would do if one happened.

> The size question deserves an answer even when today's CAD says
> the loop is not active. Suppose, contrary to the current
> direction, USDCAD moved 10% weaker over twelve months and held
> there -- a sustained move from roughly 1.36 to roughly 1.50, the
> 1998 trigger level. The arithmetic from primary BoC research,
> not from market commentary, runs as follows.
>
> Step one: a 1% CAD depreciation lifts import prices by 0.59%, per
> Devereux, Dong, and Tomlin in BoC Working Paper 2015-31. A 10%
> depreciation, holding the linear approximation, lifts the
> import-price basket by roughly 5.9%. The pass-through is
> heterogeneous across the basket: apparel is at roughly 82% and
> vegetables at roughly 21%, with goods invoiced in US dollars
> showing systematically higher pass-through than goods invoiced
> in Canadian dollars. The 0.59 average is a meaningful number
> but it is an average.
>
> Step two: the import-price lift translates into a goods-CPI lift
> proportional to the imported share of the goods basket. The
> Canadian CPI basket is roughly 47% goods and 53% services in
> the 2024 weighting; the imported share of the goods sub-basket
> is concentrated in clothing, vehicles, recreation, and household
> furnishings. The exact basket-weighted imported share at the CPI
> goods level is not quoted here; the methodology note for Chart
> B5 names the StatCan source. A reasonable working range for the
> imported-goods share of the goods basket is between 25 and 35%,
> implying a goods-CPI lift of roughly 1.5 to 2.0 percentage
> points off a 5.9% import-price move.
>
> Step three: the headline CPI lift is the goods-share weighted
> read of step two, plus modest indirect effects through services
> with imported inputs. The BoC has cited across MPR cycles a rule
> of thumb that a 10% sustained CAD depreciation lifts headline
> CPI by roughly 0.5 to 0.7 percentage points over two years, of
> which roughly half lands in year one. This rule of thumb is
> consistent with the bottom-up arithmetic above but we have not
> located a single MPR box that states it canonically; we report
> it as a structural ballpark from the Bank's analytical
> tradition, not as a citable coefficient.
>
> The structural sketch matters because it sizes the channel. A
> 10% sustained CAD depreciation -- which would require USDCAD to
> break 1.50 and hold -- adds 0.5 to 0.7 pp to headline CPI over
> two years. That is material against a 2% target but it is not
> catastrophic, and the BoC has typically responded to a CAD move
> of that size with a posture adjustment, not a panic. The 1998
> precedent involved exactly such a move and produced a 100 bps
> intermeeting hike. Today's CAD is well shy of that threshold
> and moving in the opposite direction. The pass-through cascade
> is a contingent risk, not a binding one.

![Pass-through cascade: a 10% CAD depreciation translates through Devereux et al. (0.59 import-price pass-through) to a roughly 5.9% lift in the import-price basket, through the imported share of the CPI goods basket to a 1.5 to 2.0 pp lift in goods CPI, and through the goods share of the headline basket to roughly 0.5 to 0.7 pp lift in headline CPI over two years.](/charts/pillar-b/passthrough-cascade.svg)

*Schematic horizontal-bar cascade. Sources: Devereux, Dong, Tomlin
(BoC Working Paper 2015-31) for the import-price pass-through
coefficient; Statistics Canada CPI basket weights (Table
18-10-0007-01, 2024 vintage) for the goods share; structural
ballpark for the headline-CPI step consistent with BoC MPR
tradition (not a citable single-source number). Vintage:
2026-05-11.*

---

## 7. Section V -- The 2024-25 precedent, and why it is the operating one

The historical anchor: how the last episode resolved, and what it tells us.

> The Canadian dataset has four post-1996 episodes of substantially
> negative BoC-Fed policy spreads. The 1996-98 episode bottomed at
> negative 2.51 pp in April 1997 and resolved with a BoC capitulation
> -- a 100 bps intermeeting hike on August 27, 1998 when USDCAD broke
> 1.50. The 2015-17 episode followed the BoC's January and July 2015
> oil-shock cuts; the spread reached roughly negative 75 to 100 bps,
> CAD weakened to about 1.45 without forcing a back-off, and the
> divergence resolved through Fed pauses in 2016. The 2024-25 episode
> is the one that matters for today's setup.
>
> The 2024-25 episode is the right structural analogue for three
> reasons. First, the BoC was again ahead of the Fed on cuts: BoC's
> first cut landed in June 2024, three months before the Fed's first
> cut in September 2024. The BoC kept cutting; the 2y GoC-UST spread
> reached its post-2001 minimum of negative 170 bps on February 3,
> 2025. Second, USDCAD touched 1.45-plus intraday in late Q1 2025
> without forcing a BoC reversal -- a direct test of the threshold
> question and a result that updated the historical operating range.
> Third, and decisively, the resolution came from Fed convergence,
> not from BoC capitulation. The Fed cut into late 2025; the BoC's
> own final cut in this cycle brought the overnight target to 2.25%
> on October 29, 2025; the 2y spread closed from minus 170 bps to
> roughly the minus 98 bps reading today. The BoC did not reverse.
> The Fed caught up.
>
> The structural reason that episode resolved that way is the same
> structural reason today's episode is likely to resolve the same
> way. Canadian inflation expectations were anchored throughout, the
> Bank's reaction function gave it runway to absorb the spread, and
> the FX move was uncomfortable but not catastrophic. Fed policy was
> set independently of Canadian conditions, and the Fed cut when US
> conditions warranted, not when Canadian conditions did. The
> mechanic of "the BoC waits for the Fed to converge" is a feature
> of two independent central banks running their own reaction
> functions in cycles that are not synchronized.
>
> The 1997-98 analogue is contingent, not active. It would
> re-activate if and only if CAD broke 1.45-plus and held, which it
> has not. The structural setup that produced the August 1998
> intermeeting hike -- USDCAD breaking 1.50, expectations under
> pressure, a Bank reaction function more directly weighted to FX
> stability than today's -- is not today's setup. The 2024-25
> precedent is closer in every dimension that matters: policy
> framework, expectations posture, CAD range, and the structure of
> the resolution.
>
> One implication for the forward path. If the 2024-25 precedent
> holds, the binding sequence in 2026 is not "BoC capitulates to
> close the spread"; it is "the Fed eventually cuts and the spread
> compresses passively." The next meeting of the FOMC is the
> active variable; the next BoC meeting on June 10 is, on the
> Bank's signalled path, more likely a hold than a cut. The spread
> will widen further only if the Fed cuts and the BoC holds, or
> the BoC cuts again while the Fed holds. The Fed's path is the
> swing factor.

![BoC overnight rate, Fed funds effective rate (left axis, percent), and USDCAD (right axis, FX), January 2024 through May 2026. Annotations: BoC first cut June 2024; Fed first cut September 2024; BoC 2.25% reached October 29, 2025; Fed convergence into December 2025.](/charts/pillar-b/precedent-2024-25.svg)

*BoC overnight rate target (Valet V39079) and Fed funds effective
rate (FRED FEDFUNDS), left axis. USDCAD spot (BoC Valet FXUSDCAD),
right axis. Monthly for rates, daily resampled for FX. January 2024
through May 7, 2026. Source: Bank of Canada Valet; Federal Reserve
Economic Data. Vintage: 2026-05-07.*

---

## 8. Section VI -- What would change our mind

Falsification triggers. The call is contingent; here is what would invalidate it.

> The thesis -- that the divergence can run further because the
> binding constraint is the expectations chain, not the FX channel
> -- has named falsification triggers. Each is monitorable from
> primary sources.
>
> **If USDCAD breaks 1.45 and holds for a full quarter, then the
> FX channel re-activates as the binding constraint.** The 2024-25
> episode established that intraday 1.45-plus does not force a
> BoC back-off; a sustained quarter at or above that level would.
> The 1998 precedent involved 1.50, but the 1990s Bank reaction
> function was more directly weighted to FX stability than
> today's. We anchor the trigger at 1.45 for the current framework.
> Today's USDCAD is at 1.3575; the trigger is roughly 7% weaker
> than current.
>
> **If CSCE 5y consumer expectations re-accelerate to 3.5%-plus,
> then the expectations anchor is in question and the BoC's runway
> shortens materially.** The 5y measure was at 3.67% in Q3 2025
> and has moderated to 3.02% in Q1 2026. A reversal above 3.5% in
> Q2 or Q3 2026 would mark an expectations process that has
> stopped re-anchoring. The Q2 release in July 2026 is the next
> watchpoint.
>
> **If headline CPI prints above 3% in April 2026 and the May or
> June print fails to decline, then the BoC's own forward path is
> falsified.** The April 29 statement explicitly projects CPI
> rising to "about 3%" in April on a gasoline base effect then
> declining. April is the test of the base-effect framing; May and
> June are the test of the decline. A failure to decline would
> indicate either broader inflation pressure than the gasoline
> story explains or a stickier services component, both of which
> would shorten the BoC's runway to hold.
>
> **If 10y GoC yields rise to 4% or above on imported US-Treasury
> beta, then the long end tightens financial conditions enough to
> offset the BoC's stance.** The 10y currently sits at 3.53%, so
> the threshold is roughly 50 bps of headroom. A rise of that
> magnitude driven by US term-premium pricing rather than Canadian
> fundamentals would produce a perverse outcome in which BoC
> easing is undone by long-end repricing. This is the contingent
> trigger we have the thinnest direct data on -- the 10y UST is
> not currently in the project's pipeline, and a clean BoC
> staff-paper source on Canadian imported term premium is among
> the open research items. We flag it because the structural
> logic is clear even where the precise series is not yet wired.
>
> **If credit conditions tighten sharply -- Canadian IG / HY
> spreads widening 50 bps-plus, bank-funding spreads widening, or
> mortgage-GoC spreads widening -- then the credit channel binds
> even if the FX and expectations channels do not.** This trigger
> is the gap in this draft. Project data does not currently wire
> Canadian credit-spread series cleanly enough to quantify; US IG
> and HY OAS are listed in our sources but not yet visible as a
> Canadian-conditions proxy. We flag the trigger structurally and
> commit to quantifying it for v2 of this Pillar.
>
> The base case, with these triggers named: the BoC holds at
> 2.25% through 2026 and the spread compresses passively as the
> Fed cuts; the 2024-25 precedent reruns, in shape if not in
> sequence. The binding variable is the Fed's path, not the
> Bank's.

---

## 9. Section VII -- The call and the watchpoint

> **The call.** The BoC-Fed divergence can run further than today's
> FX market is signalling. The policy spread at minus 137.5 bps
> and the 2y spread at minus 98 bps are deep by historical
> standards, but the channel through which depth would translate
> into BoC capitulation -- a CAD-driven repricing of inflation
> expectations -- is not active. Inflation expectations are
> moderating, not breaking. The 2024-25 precedent shows the Bank
> can absorb a wider 2y spread than today's without reversing, and
> can wait for Fed convergence rather than capitulate. We expect
> exactly that pattern through 2026: BoC holds at 2.25%, the Fed
> cuts when US conditions warrant, the spread compresses passively.
>
> **The watchpoint.** The single piece of data that would update
> this call fastest is the Q2 2026 CSCE 5y consumer expectations
> print, released July 2026. The 5y has moved from 3.67% in Q3
> 2025 to 3.02% in Q1 2026; a Q2 print below 2.75% confirms the
> re-anchoring and extends the BoC's runway; a Q2 print back above
> 3.25% breaks the chain and forces the call into question.
> Secondary watchpoints: the April 2026 headline CPI print
> (released mid-May) and the June 10, 2026 BoC decision. USDCAD
> at 1.45-plus would be a tertiary trigger, but the leading
> indicator we are watching most closely is the expectations
> chain, not the currency.

---

## 10. Citations and data vintage

Primary citations of record, in order of appearance:

- Bank of Canada press release, "Bank of Canada maintains policy
  rate, continues normalization of its balance sheet," April 29,
  2026. https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/
- Bank of Canada Valet, series V39079 (overnight rate target),
  daily through close 2026-05-07.
- Bank of Canada Valet, 2-year and 10-year Government of Canada
  benchmark yields, daily through close 2026-05-07.
- Federal Reserve Economic Data (FRED), series FEDFUNDS (effective
  federal funds rate, monthly), DFEDTARU and DFEDTARL (Fed funds
  target range, daily midpoint computed by author), DGS2 (2-year
  US Treasury constant-maturity yield, daily), through close
  2026-05-07.
- Bank of Canada Valet, series FXUSDCAD (Canada-US exchange rate,
  noon spot), daily through 2026-05-01.
- Bank of Canada, Canadian Survey of Consumer Expectations, Q1
  2026 release (April 2026). 1-year-ahead and 5-year-ahead
  inflation expectations.
- Bank of Canada, Business Outlook Survey, Q1 2026 release (April
  2026). Distribution of firms' CPI expectations.
- Statistics Canada, Table 18-10-0004-01, Consumer Price Index,
  monthly, March 2026 release.
- Statistics Canada, Table 18-10-0007-01, CPI basket weights, 2024
  vintage.
- Devereux, M.B., Dong, W., and Tomlin, B., "Exchange Rate
  Pass-Through, Currency of Invoicing and Market Share," Bank of
  Canada Working Paper 2015-31, August 2015.
  https://www.bankofcanada.ca/wp-content/uploads/2015/08/wp2015-31.pdf
- Bank of Canada April 2026 Monetary Policy Report (April 29,
  2026 release). CPI projection and conditional forward guidance.

Data vintage stamps:
- Policy and curve series: through close 2026-05-07.
- USDCAD: through 2026-05-01.
- Expectations and BOS: Q1 2026 (April 2026 release).
- Headline CPI: March 2026 print (released April 2026).

Constructed series and computations (run inline by the researcher;
methodology note one click away in `editorial/insight_base/pillar_b_boc_fed_divergence.md`):
- BoC-Fed policy-rate spread: V39079 (monthly close) minus FEDFUNDS,
  post-1996 distribution, percentile rank of latest reading.
- 2y GoC-UST spread: 2y GoC (BoC Valet) minus DGS2 (FRED), daily
  common-trading-day calendar, post-2001 distribution, percentile
  rank.
- USDCAD percentile: FXUSDCAD daily, post-1990 distribution,
  percentile rank of latest reading.

Open research items flagged in this draft for v2:
- 10y UST series not currently in the project pipeline; the 10y
  leg of the curve divergence is referenced structurally but not
  quoted as a precise spread number. Backend-engineer to wire
  FRED DGS10.
- Canadian credit-spread series (IG, HY, bank-funding,
  mortgage-GoC) not visible in `data/raw/`; the credit channel
  in Section VI is structural, not quantified. Researcher to
  resolve.
- OIS-implied BoC path and Fed dot-plot data not wired; Section V
  argues structurally around the 4-meeting forward, not
  numerically.
- BoC MPR canonical "10% CAD = X pp CPI" rule of thumb is referenced
  as a structural ballpark in Section IV; locating a single MPR box
  or staff-paper source for the precise coefficient is an open
  research item before v2.
- StatCan basket-weighted imported share of the goods sub-basket
  is referenced in Section IV with a 25 to 35% working range
  rather than a precise figure; pulling Table 18-10-0007-01 for
  the exact share is an open research item.

---

End of v1 draft. Next: style-editor voice pass; fact-checker pass
against insight base; chart-builder commission of B1-B6.
