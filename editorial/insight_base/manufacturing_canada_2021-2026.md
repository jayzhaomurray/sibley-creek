# Canadian manufacturing 2021-2026: a five-year read

Status: internal insight base, researcher draft. Voice not polished. Sources at end.
Data cutoff: February 2026 (StatCan Table 36-10-0434-01, released April 2026).
Derivation script: `analyses/manufacturing_subsector_decomp_2026_05_12.py`.
Derived table: `data/derived/manufacturing_subsector_decomp.csv`.

## 1. Aggregate read

Canadian manufacturing real GDP in February 2026 stood at 94.0 (Dec 2019 = 100) —
i.e. roughly 6% below its pre-pandemic level six and a quarter years on. This is
the only major aggregate sector that has failed to recover. For comparison
(same Dec-2019 = 100 baseline, Feb 2026): total economy 111.3, services 113.9,
mining/oil/gas 113.4, goods-producing 105.1. Manufacturing is the outlier.

The Y/Y print has been negative for the last 14 consecutive months. Of those,
10 prints were worse than -2% and four were worse than -4% (May, June, October,
November 2025 and January 2026). Feb 2026 came in at -3.1% Y/Y. This is the
deepest sustained manufacturing contraction since the 2008-09 financial crisis;
unlike that episode, GDP at the aggregate level continued to grow.

Manufacturing employment has tracked the GDP contraction with a lag. StatCan's
February 2026 LFS showed manufacturing employment down 52,000 (-2.8%) Y/Y; the
single-month decline of -28,000 in January 2026 was concentrated in Ontario.

## 2. NAICS subsector decomposition

The slump is concentrated, not industry-wide. Of the 18 manufacturing subsectors
that StatCan reports at the 3-digit (sub-sector) level under 36-10-0434, three
subsectors account for roughly two-thirds of the cumulative drag, and three
subsectors are actually above their Dec-2019 level.

Indexed levels at Feb 2026 (Dec 2019 = 100) and contribution to the aggregate
6.3-percentage-point shortfall, ranked by drag:

| Subsector | Index | Y/Y | Contrib (pp of mfg) |
|---|---:|---:|---:|
| Paper manufacturing | 80.9 | -4.5% | -2.92 |
| Fabricated metal products | 73.7 | -4.9% | -1.00 |
| Machinery | 55.8 | -2.8% | -0.93 |
| Food | 90.7 | -0.1% | -0.71 |
| Plastics and rubber | 79.9 | -4.7% | -0.69 |
| Primary metal | 87.0 | -14.3% | -0.68 |
| Electrical equipment, appliances | 93.9 | -6.9% | -0.66 |
| Miscellaneous | 91.9 | -6.0% | -0.48 |
| Wood products | 77.6 | +6.2% | -0.45 |
| Printing | 88.1 | -10.1% | -0.28 |
| Non-metallic mineral | 81.8 | +3.1% | -0.21 |
| Furniture | 94.5 | +4.3% | -0.18 |
| Computer/electronic | 98.7 | -1.7% | -0.08 |
| Petroleum and coal products | 98.3 | +5.7% | -0.04 |
| Transportation equipment | 99.5 | +6.4% | -0.02 |
| Textile/clothing/leather | 108.4 | -0.3% | +0.27 |
| Chemicals | 107.5 | -1.6% | +0.99 |
| Beverage and tobacco | 124.1 | -1.3% | +1.80 |

Three things to register:

(a) Paper alone explains nearly half of the cumulative shortfall (-2.9pp of -6.3pp).
That decline is not a tariff story — it is a multi-decade structural decline in
print, paper, and pulp demand, accelerated by COVID and not retraced. Paper at
80.9 indexed reflects the secular path, not a 2025 shock.

(b) Machinery at 55.8 is the most spectacular collapse in the table. Machinery
output has roughly halved since 2019. The decline is gradual and multi-cause
(weak business investment, residential construction collapse, mining-equipment
cycle), not a single-shock break.

(c) The classically tariff-exposed subsectors (primary metal, fabricated metal,
transportation equipment) sit in a striking pattern. Primary metal — steel and
aluminum — is at -14.3% Y/Y, the worst single Y/Y read in the table, mostly a
2025 development reflecting U.S. Section 232 actions. Transportation equipment
(autos and aerospace) is actually +6.4% Y/Y at the latest print but flat vs Dec
2019. The aggregate manufacturing story is therefore: a long structural decline
that pre-dates Trump 2.0, layered with a sharp 2025 tariff shock on metals.

## 3. What people inside the industry are saying

### CEOs

Swamy Kotagiri (Magna International, April 2025): called the proposed Trump
tariff regime "untenable" for suppliers, guided 2025 revenue down to $38.6-40.2bn
from $43bn in 2024, and likened the disruption to 2008-09 and the chip shortage.
Repeatedly emphasized policy certainty as the binding constraint, not the tariff
level per se.

Michael Garcia (Algoma Steel, Sept 2025): publicly asked PM Carney to "immediately
engage" with the Trump administration after the 50% Section 232 rate was set;
Algoma withdrew from October-December 2025 U.S. supply contracts. Q3 FY2025
posted a net loss of C$485mn including roughly C$90mn in tariff costs and a
C$500mn+ writedown; Algoma accelerated its EAF transition "basically a year early"
in response.

Éric Martel (Bombardier, Feb 2026): contrast case. Bombardier closed 2025 with
revenue up 10% to $9.55bn, 157 aircraft deliveries, and a $17.5bn backlog (a
decade high). Defense crossed $1bn in revenue ahead of plan. Business aviation
is not the manufacturing-sector story.

### Manufacturers' associations

Dennis Darby (CME): the dominant industry voice on the tariff threat. In January
2025 he wrote to the Prime Minister and party leaders warning of "immediate and
severe risk to thousands of businesses." On Budget 2025, he welcomed accelerated
investment expensing but argued "deeper tax and regulatory reforms are still
needed." CME's posture throughout 2025-26 has been defensive, not strategic-pivot
mode.

Flavio Volpe (APMA): the highest-profile auto industry voice. Quoted in February
2025 that "at 25%, absolutely nobody in our business is profitable by a long shot."
Testified to USTR in CUSMA renegotiation hearings in December 2025 leaning on
U.S. Census trade-flow data to argue integration. Strategy: keep the integration
narrative loud in U.S. media markets. Volpe is also notable for not adopting the
"manufacturing is dying" framing — his line is the integration is mutual, the
costs land on Americans too.

### Equity analysts

Less well-captured in public sources. Sell-side framing accessible via earnings
transcripts and price-target moves: Magna saw a wave of price-target cuts in
April 2025 after the Q1 guidance cut, with consensus moving to a "wait for tariff
clarity" stance. Algoma's net loss and writedowns in Q3 FY2025 prompted further
downgrades. The cross-cutting analyst framing has been bimodal: (i) cyclical
trough story (autos, machinery) — wait for the rate cycle and demand recovery,
or (ii) structural impairment story (steel, aluminum) — the cross-border business
model is broken and won't be restored.

### Economists

Tiff Macklem (BoC, multiple 2025-26 speeches): the consistent line is that
"US trade actions are having severe effects on targeted sectors including
autos, steel, aluminum and lumber" and that the Canadian economy is undergoing
"profound structural transformation." Macklem has explicitly argued further rate
cuts "risk doing more harm than good" — i.e. the BoC reads the manufacturing
slump as supply-side and structural, not a demand problem to fix with policy
rates. February 2026 speech "Structural change—Canada at a crossroads" is the
key text.

Trevor Tombe (Calgary): frames Canada as in a "productivity crisis" — output per
worker essentially flatlined for a decade. On tariffs, his argument is that the
uncertainty channel matters more than the headline rate: "supply chains will be
built to reduce exposure to sudden policy shifts, which means more redundancy,
higher costs, and lower productivity." Quantified the potential job loss at
~600,000 in early-2025 scenarios.

Mike Moffatt (Smart Prosperity): emphasizes the misallocation channel — housing
costs preventing labour mobility into higher-productivity work. Less directly on
the manufacturing decline but speaks to why a recovery, when demand returns,
might not regain prior productivity levels.

Bank chief economists (aggregated, no individual citations): consensus has
moved through 2025 toward a structural framing, with most shops describing the
manufacturing slump as "tariffs accelerating pre-existing trends" rather than a
clean cyclical shock.

## 4. Specific cases

Ford Oakville — EV transition collapse. In July 2024, Ford pushed the planned
electric three-row SUV launch at Oakville from 2025 to 2027 and pivoted the plant
to F-Series Super Duty production starting 2026. The retooling pause kept the
plant largely cold through 2024-25. Demonstrates the EV-transition-cost vector
of the slump: capex commitments made on 2023 demand projections; production
gaps materialized when those projections failed.

Stellantis Brampton — indefinite pause. February 2025, Stellantis announced
an "eight-week operational pause" on next-gen Jeep Compass retooling at Brampton.
That pause has now extended past March 2026 with no firm restart. In October
2025 Stellantis confirmed Compass production would shift to Belvidere, Illinois,
with N.A. assembly starting late 2027. Approximately 3,000 unionized workers
affected. Demonstrates how policy uncertainty (Trump tariff threats from late
2024 forward) converts directly into deferred and ultimately relocated production.

Algoma Steel — 50% S232 and EAF acceleration. June 2025, U.S. tariffs on
Canadian steel doubled from 25% to 50%. Algoma withdrew from U.S. spot
contracts in October, took a $500mn+ writedown, and accelerated the EAF
conversion. CEO publicly stated U.S. viability is in question. The clearest
single-firm case of the "cross-border business model broken" narrative.

Aluminerie Bécancour / Rio Tinto Canada — export redirection. The 50%
Section 232 rate that hit aluminum on the same June 2025 date triggered a rapid
export reorientation away from the U.S. Aluminerie Alouette moved European
sales from 4% to 57% of production within months. Rio Tinto Aluminium
absorbed ~$300mn in gross tariff costs in H1 2025. The aluminum sector's
adjustment was faster than steel's because of more diversified existing customer
relationships.

Honda Alliston — withdrawn investment. The $15bn EV-and-battery investment
announced in 2024 was paused for two years in May 2025, then reported indefinitely
halted in May 2026. Cited: slow EV demand (Canadian ZEV sales down 36% in 2025
to 170k, <9% of total), Trump elimination of EV tax credits, and Honda's broader
global EV retrenchment. This is the strongest counter to the "EV-transition will
rebuild Canadian auto manufacturing" thesis prevalent in 2023.

## 5. The cross-cutting narrative

What is the slump? Ranked by contribution to the cumulative gap:

1. **Structural decline in legacy subsectors** (paper, printing, some food) —
   pre-dates 2020. Accounts for roughly 4 of the 6 percentage points of shortfall.
   Not policy-fixable in the short run.
2. **Tariff shock on metals** (primary metal, fabricated metal) — concentrated in
   2025, the most acute and visible piece. Y/Y prints in primary metal are the
   table's worst.
3. **EV-transition transition cost** (transportation equipment, electrical
   equipment) — plant downtime during retooling, then deferred or cancelled
   retooling as EV demand softened. The aggregate transportation equipment level
   is roughly flat vs Dec 2019, but the path was a deep COVID trough then a
   strong recovery, now stalled.
4. **Productivity / competitiveness** — the slow-burn backdrop. Machinery at
   55.8 indexed reflects 15 years of weak business investment, not a single shock.

Where insider voices converge: this is partly a tariff story and partly something
older. Macklem, Tombe, Volpe, and Darby all explicitly frame the moment as
acceleration of pre-existing structural weakness, not a clean exogenous shock.

Where they diverge: on policy response. CME/APMA push for industrial-policy
support (expensing, sector-specific aid). The BoC and academic economists push
for structural reforms (internal trade barriers, regulation, productivity-enabling
capex). The single-firm CEO voices are more tactical — they want certainty above
all, then carve-outs.

If we have to pick one line: the Canadian manufacturing recession is real but
narrower than the aggregate suggests — paper, fabricated metal, machinery, and
food do most of the work — and it is best understood as a tariff shock layered
on top of a 15-year productivity stagnation, with the 2024-25 EV transition
adding a third drag in transportation equipment.

## Sources

Data:
- StatCan Table 36-10-0434-01, GDP by industry, monthly. https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610043401
- StatCan, "Manufacturing labour in 2025: Losses down the line amid trade headwinds." https://www.statcan.gc.ca/o1/en/plus/9099-manufacturing-labour-2025-losses-down-line-amid-trade-headwinds
- StatCan, "Recent employment trends in industries dependent on U.S. demand." https://www150.statcan.gc.ca/n1/pub/36-28-0001/2025012/article/00003-eng.htm
- StatCan Daily, Monthly Survey of Manufacturing, releases through Feb 2026.

CEOs and earnings:
- Magna Q1/Q4 2025 earnings, Kotagiri commentary. https://www.detroitnews.com/story/business/autos/2025/04/15/magna-ceo-swamy-kotagiri-tariffs-trump/83096064007/
- Algoma Steel Q3/Q4 FY2025 transcripts, Globe and Mail reporting. https://www.theglobeandmail.com/business/article-algoma-steel-50-per-cent-tariffs-threaten-viability/
- Bombardier full-year 2025 results. https://bombardier.com/en/media/news/bombardier-exceeds-all-2025-guidance-metrics-successfully-completes-its-turnaround-plan

Associations:
- CME, Dennis Darby statements on tariff threat (Jan 2025) and Budget 2025. https://cme-mec.ca/blog/statement-from-dennis-darby-president-ceo-canadian-manufacturers-exporters-on-the-potential-imposition-of-u-s-tariff-threat/
- APMA, Flavio Volpe CUSMA testimony (Dec 2025). https://www.apma.ca/post/canadian-auto-parts-makers-relieved-by-tariff-pause

Economists:
- BoC, Macklem speech "Structural change—Canada at a crossroads," Feb 2026. https://www.bankofcanada.ca/2026/02/structural-change-canada-at-a-crossroads/
- BoC, Macklem speech "Tariffs, structural change and monetary policy," Feb 2025. https://www.bankofcanada.ca/2025/02/tariffs-structural-change-and-monetary-policy/
- BoC, Macklem speech "Time to roll up our sleeves," Sept 2025. https://www.bankofcanada.ca/2025/09/time-to-roll-up-our-sleeves/
- Trevor Tombe, "How bad will Trump's tariffs be for Canada," The Hub, Feb 2025. https://thehub.ca/2025/02/02/trevor-tombe-how-bad-will-trumps-tariffs-be-for-canada-here-are-the-most-important-numbers/
- Trevor Tombe, CPA Ontario interview on trade, tariffs and competitiveness. https://www.cpaontario.ca/insights/blog/trade-tariffs-competitiveness

Specific cases:
- Ford Oakville EV delay, CBC, April 2024. https://www.cbc.ca/news/canada/toronto/ford-delay-oakville-ev-plant-1.7163251
- Ford Oakville Super Duty pivot, July 2024. https://www.cbc.ca/news/canada/toronto/ford-motor-co-pickups-oakville-1.7267756
- Stellantis Brampton pause, Detroit News, Feb 2025. https://www.detroitnews.com/story/business/autos/chrysler/2025/02/20/stellantis-pauses-work-on-next-gen-jeep-compass-at-canadian-plant/79325015007/
- Stellantis Brampton extension, The Pointer, March 2026. https://thepointer.com/article/2026-03-12/stellantis-repeats-commitment-to-reopening-brampton-plant-then-lays-off-20-staff
- NextStar / Stellantis-LG dispute resolution, July 2023. https://www.detroitnews.com/story/business/autos/chrysler/2023/07/05/construction-resumes-stellantis-battery-module-plant-windsor-halt/70385492007/
- Aluminum tariff impact, Globe and Mail. https://www.theglobeandmail.com/business/article-aluminum-tariffs-canada-reaction/
- Honda Alliston EV pause, BNN Bloomberg, May 2026. https://www.bnnbloomberg.ca/business/company-news/2026/05/06/honda-halts-plan-to-build-15b-ev-plant-in-canada-report/

Caveats and gaps:
- The 18-subsector decomposition uses StatCan's 3-digit groupings as published in
  36-10-0434, which combines textile/clothing/leather (NAICS 313-316) into one
  series. This is more aggregated than the 21-subsector view available in the
  Monthly Survey of Manufacturing (16-10-0048). Future work could substitute the
  nominal sales table for finer cuts in the apparel/textile space.
- We did not pull sell-side equity research directly (paywalled); analyst framing
  is reconstructed from earnings-call transcripts and price-target reporting.
- Provincial cross-cut (StatCan 14-10-0064) was not pulled — Ontario is clearly
  bearing most of the auto and steel drag; Quebec the aluminum drag. Worth a
  follow-up if the writer wants the regional angle.
