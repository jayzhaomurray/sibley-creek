# Methodology

Sibley Creek is a tracker of Canadian macro built on primary Canadian
sources, refreshed on the cadences those sources publish on. This
page describes where the data come from, how often they update, how
revisions move through, and the editorial rules the publication runs
on.

## Data sources

The live tracker pulls from seven primary sources today.

**Statistics Canada** is the spine. Consumer prices (headline plus
the BoC's core-trim and core-median measures, with sub-aggregates),
the Labour Force Survey (employment, unemployment, participation,
wages), monthly GDP by industry (Table 36-10-0434), quarterly GDP by
expenditure (Table 36-10-0104), merchandise trade, housing starts,
and CMA-level population all come directly from StatCan's WDS
endpoint by vector ID. **The Bank of Canada** supplies the overnight
rate target, GoC benchmark yields from 2y to 30y, the USDCAD spot
rate, CORRA, the BoC's commodity price indices, the Canadian Survey
of Consumer Expectations, the Business Outlook Survey, and the
output gap series from the MPR. **FRED** provides US comparators --
2y and 10y Treasury yields, the fed funds target, the VIX, US IG and
HY corporate spreads, WTI, and Brent. **Yahoo Finance** supplies
daily closes on the TSX Composite, the S&P 500, and front-month
COMEX gold. **CREA** delivers the MLS HPI national plus six CMA
aggregates. **The Department of Finance**'s monthly Fiscal Monitor
provides the federal budgetary balance, revenues, expenses, and
debt-service costs. **The Canadian Bankers Association**'s monthly
mortgage-arrears file is wired as a proxy for the broader stock view
while CMHC's RMIR series is out of pipeline.

OSFI Bank Financial Data and the CMHC arrears and Rental Market
Survey series are named in the source roster but not yet wired; both
are scheduled for a later wave. The Parliamentary Budget Officer's
Economic and Fiscal Outlook and BIS peer central-bank rates are also
in queue. This page updates when those sources land.

## Cadence

Each section refreshes on the release calendar of its primary
trigger. CPI lands mid-month, roughly two weeks after the reference
month, and the Inflation chartbook rebuilds on that print. LFS lands
the first Friday of the month and drives Labour. Monthly GDP by
industry runs roughly 60 days behind reference and drives the GDP
section's monthly view; quarterly GDP by expenditure refreshes the
expenditure cuts and the current account. Trade releases monthly with
about a 30-day lag. The Fiscal Monitor releases monthly with about a
two-month lag. Markets refreshes daily on yields, FX, and commodity
prices; a weekly synthesis sits on top.

Policy is event-driven. The BoC's eight fixed announcement dates in
2026 are Jan 28, Mar 18, Apr 29, Jun 10, Jul 15, Sep 2, Oct 28, and
Dec 9, with the Monetary Policy Report alongside the January, April,
July, and October decisions. The Summary of Deliberations follows
two weeks after each decision; the Financial System Review lands in
May and November. The Federal Budget (Feb-Mar) and the Fall Economic
Statement (Nov-Dec) drive the fiscal slate.

## Vintage and revisions

StatCan and the BoC revise their own data. Monthly series typically
revise the prior one to three observations on each release; LFS
revises the prior month; GDP often revises the prior two quarters.
The site shows the latest vintage as-is and lets the next pipeline
build flow revisions through. Prior published commentary attached to
a chart is not silently restated. The chart at the top of a
chartbook unit reflects the current vintage; the paragraph beneath
it is the read-of-the-day for the release it shipped on.

CREA back-revises roughly the prior three months as late-closing
sales report in. The federal Public Accounts release each December
restates the prior fiscal year for the Fiscal Monitor. The CPI
basket updates on a roughly five-year cycle; the current basket
applies through about 2029. Cross-basket price levels are not
strictly comparable, but year-over-year changes are, because
StatCan chains the index across baskets.

A tile that shows a gap is a real gap. When a primary series CSV is
missing or malformed and the loader cannot fill the row with real
data, the site leaves the gap visible rather than fill it with a
stale or fabricated number. As sources wire in, the placeholders
clear.

## Voice rules that shape the methodology

Sibley Creek cites primary Canadian institutions in running prose:
Statistics Canada, the Bank of Canada, OSFI, CMHC, the Department of
Finance, the PBO, provincial finance ministries, C.D. Howe's
Business Cycle Council, the IMF Article IV Canada report, and the
OECD Economic Survey of Canada. The Big-Six bank economics desks are
read daily as competitors; they are not cited in running prose as
authority.

When market consensus is the natural comparator on a print -- the
Bloomberg or Reuters median, or an aggregated forecaster median
where the paid feed is unavailable -- it enters as a derived number
attached to a comparison, not as a quoted view. When market
consensus is genuinely unavailable, the BoC's most recent MPR
central projection is the fallback anchor, named directly and
dated. Every constructed series carries a methodology note one
click away.

## The auto-blurb pipeline

A second mode of the publication is the short interpretation
paragraph that fires on a fresh data print. The pipeline drafts a
release-context note from verified primary-source claims, re-fetches
each cited URL to confirm the claim verbatim, drafts the
two-to-four-sentence blurb, fact-checks against the verified cards,
and polishes voice. Human editorial review gates publish in every
case. The pipeline is built and awaiting its first live run; it
turns on across Inflation, Labour, and Policy over the course of
2026. The data-fetch side of Mode 2 is the path that fully automates;
the human review gate stays.
