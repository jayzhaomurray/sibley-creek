# Build-Big trades-gap project inventory

**For:** Sibley Creek economist (Thompson)
**Compiled:** 2026-05-26
**Purpose:** starting demand-side inventory for the trades-gap piece. Every project the federal Major Projects Office (MPO) has referred is listed below, with the data Thompson needs to begin Method 1 (published workforce) or Method 2 (analog-plus-scaling) estimation per the brief.

---

## Summary

**Project counts.** The MPO live page reports 21 referrals to date: 15 nation-building projects + 6 transformative strategies, $126B+ combined investment ([MPO main page](https://www.canada.ca/en/privy-council/major-projects-office.html), as quoted in search). The transformative strategies are framework strategies, not single construction projects, so for demand-side modelling Thompson should focus on the 15 named projects + the Carney-Smith pipeline (expected referral July 1, 2026). Of those 16 projects:

- **Method 1 (published workforce numbers available, full or partial):** 11 projects — LNG Canada Phase 2, Darlington SMR, Contrecoeur Terminal, McIlvenna Bay (already in commissioning), Red Chris Expansion, Ksi Lisims LNG (with associated PRGT pipeline), Canada Nickel Crawford, Matawinie Graphite, Sisson Tungsten, Mackenzie Valley Highway, Grays Bay Road & Port, plus Alto HSR if it counts as a project rather than a strategy.
- **Method 2 (analog needed):** 5-6 projects — North Coast Transmission Line (partial figures only; needs Site C transmission + Hydro One analogs), Iqaluit Nukkiksautiit (no published workforce), Taltson Hydro Expansion (no published workforce; Site C scaled down), Arctic Economic & Security Corridor (no published workforce; Mackenzie Valley analog), and the Carney-Smith west-coast pipeline (no proponent committed; TMX is the canonical analog).

**Geographic distribution** (primary province for construction labour demand):
- **BC:** 5 — LNG Canada Phase 2, Red Chris, Ksi Lisims LNG + PRGT pipeline, North Coast Transmission, Carney-Smith pipeline (BC terminus + ROW segment).
- **AB:** 1 + Carney-Smith pipeline (origin/ROW) — note Pathways CCS is referenced in the brief but is not currently MPO-referred.
- **ON:** 3 — Darlington SMR, Canada Nickel Crawford, Alto HSR (partially).
- **QC:** 2 — Contrecoeur Terminal, Matawinie Graphite, plus Alto HSR (partially).
- **SK:** 1 — McIlvenna Bay (effectively out of new-construction scope; in commissioning).
- **NB:** 1 — Sisson Tungsten.
- **Atlantic (NS/NB/NL/PE):** 1 — Wind West (transformative strategy only).
- **Northern (NU/NT):** 4 — Iqaluit Nukkiksautiit, Mackenzie Valley Highway, Grays Bay Road & Port, Arctic Economic & Security Corridor, Taltson Hydro.
- **MB:** 1 — Port of Churchill Plus (transformative strategy).

**Highest-confidence projects (top 5, full or near-full published workforce data):**
1. **Darlington SMR** — OPG publishes 700 new hires Phase-1; 18,000 jobs/year fleet construction average; trades named (iron workers, millwrights, boilermakers).
2. **Contrecoeur Terminal** — federal EA + Port of Montreal disclosure; 4,000 construction jobs (direct + indirect); 7-year build window.
3. **Red Chris Expansion** — Newmont disclosure: 1,800 peak construction; 1,500 operational.
4. **Canada Nickel Crawford** — Canada Nickel feasibility study: 2,000 construction jobs; 1,300 operational; 2026 ground-break.
5. **Matawinie Graphite** — NMG ground-breaking May 19, 2026; ~1,000 jobs across construction + operations; 31-month build window.

**Highest-uncertainty projects (analog approach most strained):**
1. **Carney-Smith west-coast pipeline** — no proponent committed; TMX is the analog but the route geography (Rockies + coastal BC) is different. TMX coefficient ~58 person-years/km; if Carney-Smith is ~1,150 km Edmonton-to-Kitimat (placeholder), that scales to ~67K person-years — same magnitude as TMX. But construction-cost-per-km will likely be higher (rougher terrain, new ROW, Indigenous accommodation). Flag transparently.
2. **Iqaluit Nukkiksautiit** — no proponent-disclosed workforce. Site C (~7 person-years/MW main civils) is the analog, but Site C is southern, road-accessible, and benefits from BC Hydro's institutional depth. Scaling 7 × (15-30 MW) gives 105-210 person-years — clearly an underestimate. Northern projects have a "remoteness multiplier" that the literature has not cleanly quantified. Flag.
3. **Taltson Hydro Expansion** — same northern multiplier; Site C base, scaled to +60 MW.
4. **Arctic Economic & Security Corridor** — proponent partnership being formed; no published workforce; Mackenzie Valley Highway is the closest analog but at a smaller per-km scale.
5. **North Coast Transmission Line** — CleanEnergyGrid US figure (~17 jobs/km) is the only quantitative anchor; ~445 km × 17 = ~7,500 jobs-years across phases is the ballpark, but the US figure is not Canadian.

**Off the critical path (small or non-construction-incremental):**
- **McIlvenna Bay** — already 88% complete (Jan 2026 reporting); commercial production mid-2026; construction labour demand is mostly behind us. Counted as Method 1 for completeness but contributes near-zero to 2026-2029 peak-concurrence math.
- **Sisson Tungsten** — 500 construction jobs is small relative to LNG/SMR/pipeline magnitudes; financing still uncertain (US DoD + Government of Canada funding for engineering studies May 2026, not yet construction).
- **Iqaluit Nukkiksautiit** — 100-200 person-years estimate is meaningful in NU context but does not meaningfully move the national gap.
- **Taltson Hydro** — same: small magnitude in national-gap context (though structurally important for NT economy).
- **Port of Churchill Plus** — currently a market-sounding study ($248,600 federal commitment for the study); no project-level construction capex committed in 2026.
- **Northwest Critical Conservation Corridor** — strategic framework; the projects under it (Red Chris, Ksi Lisims) are already itemized separately.
- **Wind West Atlantic** — transformative strategy only; no specific projects within construction scope for the 2026-2029 window.
- **Alto HSR** — first segment Ottawa-Montreal construction starts 2029, peak workforce demand 2030+. Outside the brief's 2027-2029 peak-concurrence window for primary analysis but worth tracking for the 2030+ tail.

---

## Main inventory table

| Project name | Tranche | Province | Proponent | Scale | Capex estimate | EA status | EA filing URL | Published workforce numbers? | Method | If Method 2, suggested analog | Scaling unit | Construction schedule (start / peak / demob) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **LNG Canada Phase 2** | Sept 11 | BC | LNG Canada (Shell + PetroChina + Mitsubishi + KOGAS + PetroChina, operated by Shell) | +14 MTPA (total 28 MTPA) | ~$33B private capital quoted; no firm public number | EA from Phase 1 covers Phase 2 footprint; BC EAO; FID expected end-2026 | [BC Energy Regulator LNG Canada page](https://www.bc-er.ca/what-we-regulate/major-projects/lng-canada/) | Partial — Phase 1 cumulative 35,000+ workers over lifecycle; peak 7,500-9,400; Phase 2 will use modular fabrication (Phase 1 approach) | 1 (with analog support for time-phasing) | LNG Canada Phase 1 as direct analog | per MTPA | FID end-2026; construction 2027-2031 if sanctioned; peak likely 2028-2029 | Modular fabrication compresses on-site labour. Asian LNG market softening may slip FID. |
| **Darlington New Nuclear (4 SMR units)** | Sept 11 | ON | Ontario Power Generation (OPG) | 1,200 MW (4 × 300 MW BWRX-300) | $20.9B fleet (2024 dollars); $6.1B first unit + $1.6B common infra | CNSC construction licence granted May 2025; IAAC EA completed prior | [CNSC SMR project page](https://www.opg.com/projects-services/projects/nuclear/smr/darlington-smr/) | Yes — 700 new hires Phase 1; trades named (iron workers, millwrights, boilermakers); fleet construction average ~18,000 jobs/yr | 1 | n/a | per MW | First unit in service end-2030; subsequent units staggered through ~2035 | Highest-confidence trade-mix disclosure of any MPO project. Vogtle is comparable analog if needed for time-phasing detail. |
| **Contrecoeur Container Terminal** | Sept 11 | QC | Montreal Port Authority (Government of Canada land) | 675-m dock, 2 berths, 1.15M containers/yr capacity | ~$950M EA estimate; $1.16B CIB financing committed April 2026 | IAAC approved (EA #80116); Carney ground-break Apr 9, 2026 | [IAAC project 80116](https://iaac-aeic.gc.ca/050/evaluations/proj/80116) | Yes — ~4,000 construction jobs (direct + indirect); thousands of operational | 1 | n/a | per berth / $-capex | Site prep 2026; major construction 2026-2030; operations 2030 | Already broken ground. Verify 4,000 figure split between direct on-site vs indirect supply chain — Thompson should use direct on-site for trades-gap math. |
| **McIlvenna Bay Foran Copper Mine** | Sept 11 | SK | Foran Mining Corporation | 4,200 tpd ore; ~$1B capex | $1B+ disclosed | Provincial approval received; wet commissioning Feb 14, 2026 | [MPO project page](https://www.canada.ca/en/privy-council/major-projects-office/projects/national/mcilvenna.html) (listed); [Foran McIlvenna page](https://foranmining.com/projects/mcilvenna-bay-project/) | Yes — peak ~800 (Oct 2025); ~400 full-time operations | 1 (effectively complete) | n/a | per tpd / per $-capex | 88% complete Jan 2026; commercial production mid-2026 | EFFECTIVELY OFF THE CRITICAL PATH for 2026-2029 peak concurrence — already in commissioning. Useful as a Method-1 datapoint for the broader critical-minerals analog set. |
| **Red Chris Mine Expansion** | Sept 11 | BC | Newcrest Red Chris Mining (Newmont subsidiary); Tahltan Nation IBA | ~13 Mtpa ore processing (block cave underground) | $2.6B (Newmont disclosure) | EA in progress (BC EAO + IAAC); fast-tracked under 1P1P provincial process | [Newmont Red Chris project page](https://operations.newmont.com/canada/red-chris-canada) | Yes — 1,800 peak construction; 1,500 operational | 1 | n/a | per Mtpa / per $-capex | Construction start TBD pending block cave approval; ~15-year combined construction + production extension | Block cave construction methodology differs from open-pit — verify trade-mix coefficient (heavier on tunnelling, drilling specialists). |
| **Ksi Lisims LNG (+ Prince Rupert Gas Transmission pipeline)** | Nov 13 | BC | Western LNG + Rockies LNG + Nisga'a Nation joint venture (LNG); Nisga'a Nation + Western LNG (PRGT) | LNG: 12 MTPA (FLNG, 2 units); PRGT: 750-800 km, 42-inch | LNG ~$9.9B base ($11.8B if power barges); PRGT ~$10B (combined ~$30B headline) | LNG: BC EAO certificate granted 2025 ([BC release](https://news.gov.bc.ca/releases/2025ENV0032-000878)); PRGT: EA certificate valid (EAO June 2025 ruling); construction notice issued Aug 2024 | [BC EAO Ksi Lisims project page](https://projects.eao.gov.bc.ca/p/60edc23bc69c5e0023a12539/project-details) | Partial — LNG: 800 peak construction; 250 permanent. PRGT: not separately disclosed | 1 (LNG) + 2 (PRGT) | PRGT analog: TMX coefficient (~58 person-years/km for oil; gas pipelines typically lower — Coastal GasLink ~6,000 peak over 670 km is the closer Canadian gas analog) | per MTPA (LNG); per km (pipeline) | LNG: construction 2026-2029; operational 2029. PRGT: FID early 2026; construction underway since 2024 | PRGT is a gas pipeline; coefficient lower than TMX-class oil. Cedar LNG is a useful adjacent reference (500 peak construction at $4.7B / smaller MTPA). |
| **Canada Nickel Crawford Project** | Nov 13 | ON | Canada Nickel Company | Open-pit nickel-cobalt; large reserve (world's #2 nickel reserve area) | $3.5B total (both phases); $1.9B phase 1 | IAAC draft Impact Assessment Report published May 11, 2026; public comment period to June 10, 2026 ([IAAC project 83857](https://iaac-aeic.gc.ca/050/evaluations/proj/83857?culture=en-CA)) | [IAAC project 83857](https://iaac-aeic.gc.ca/050/evaluations/proj/83857?culture=en-CA) | Yes — ~2,000 construction jobs; ~1,300 operational | 1 | n/a | per $-capex / per tonne capacity | Construction start late 2026 / early 2027; Q4 2028 first production target | Federal loan up to $500M reportedly under negotiation. Trade mix not disclosed — use Foran McIlvenna mix as proxy (mining: heavy-duty mechanics, equipment operators, electricians, pipefitters, miners, welders). |
| **Matawinie Graphite Mine** | Nov 13 | QC | Nouveau Monde Graphite (NMG) | 106,000 tpa graphite (open-pit) | ~$2B (project); $459M EDC + CIB financing; $113M Canada Growth Fund | Provincial EA approved; ground-broken May 19, 2026 ([PM release](https://www.pm.gc.ca/en/news/news-releases/2026/05/19/prime-minister-carney-breaks-ground-nouveau-monde-graphites-matawinie)) | NMG Matawinie project page: [nmg.com/matawinie-mine](https://nmg.com/matawinie-mine/) | Yes — ~1,000+ jobs across construction + operations; 300+ ongoing once operational | 1 | n/a | per tpa / per $-capex | Construction Q2 2026 - end 2028 (31 months); commercial production end-2028 | "Mine of the Future" branding includes all-electric mining fleet — trades mix tilts toward electricians, instrumentation. |
| **Sisson Tungsten Mine** | Nov 13 | NB | Northcliff Resources (88.5%) + Sisson Partnership | Tungsten-molybdenum open-pit; 27-year mine life | ~$579M | Provincial + federal EA approved 2017; engineering/feasibility refresh underway with US DoD $20.7M + GoC $8.2M (May 2026) | [Northcliff Sisson overview](https://www.northcliffresources.com/sissonprojectoverview) | Yes — ~500 construction; ~300 operational | 1 | n/a | per $-capex | Construction decision pending feasibility refresh (likely 2027 start if sanctioned); ~3-yr build | Smallest of the named mining projects. Trade-mix not separately disclosed; use generic mining/metallurgical coefficient. |
| **Iqaluit Nukkiksautiit Hydro** | Nov 13 | NU | Nunavut Nukkiksautiit Corporation (100% Inuit-owned) | 15-30 MW hydroelectric (Kuugaluk River) | ~$500M (2017 estimate; updated figure pending) | EA stage; federal $6M committed for project development (Jan 2026); MPO support for data collection | [Project page MPO](https://www.canada.ca/en/privy-council/major-projects-office/projects/national/nukkiksautiit.html); [NNC site](https://www.nunavutcleanenergy.ca/news) | No — proponent has not disclosed workforce numbers | 2 | Site C (~7 person-years/MW main civils) PLUS northern-remoteness multiplier (no published value — flag as +30-60% adjustment); also reference Inuvik diesel-to-hydro studies | per MW | Operational by 2033; construction window ~2028-2032 | Northern construction premium is real but unquantified in literature. Flag. |
| **North Coast Transmission Line (NCTL)** | Nov 13 | BC | BC Hydro | ~445 km total (Phase 1: 170 km Prince George-Glenannan; Phase 2: 130 km + 145 km segments) at 500 kV | Part of $4.7B BC Hydro North capex; $139.5M CIB early-works loan | BC EAO (NCTL listed at BCER); BC Hydro pre-construction phase | [BCER NCTL page](https://www.bc-er.ca/what-we-regulate/transmission-lines/north-coast-transmission-line-nctl/); [BC Hydro NCTL page](https://www.bchydro.com/energy-in-bc/projects/north-coast-bc-electrification.html) | Partial — "thousands" stated; no project-specific peak | 2 | CleanEnergyGrid US figure ~17 jobs/km × 445 km = ~7,500 jobs-equivalent (US benchmark, flag); also Hydro One Bruce-to-Milton as adjacent Canadian reference | per km × kV | Construction Phase 1 starts summer 2026; Phase 1 ops fall 2030; Phase 2 ops mid-2032 | Trade mix: ironworkers, linemen, heavy-equipment operators, surveyors — same as US transmission analogs. BC Hydro 10-yr $36B capital plan is the funding context. |
| **Mackenzie Valley Highway** | Mar 12 | NT | NWT Government + Indigenous communities | 800 km road | $1.5B+ (federal "$100M+" initial commitment; full project TBD) | EA expected to complete 2026-2027; 6.7 km section completed 2024 | [MPO project page](https://www.canada.ca/en/privy-council/major-projects-office/projects/national/mackenzie.html); [NWT MVH page](https://www.inf.gov.nt.ca/en/MVH) | Yes — Globe and Mail cites preliminary estimate ~14,000 construction jobs potential; 95 already employed on completed section | 1 (with caveat: estimate is preliminary) | Inuvik-Tuktoyaktuk Highway (recently completed) as supporting analog | per km | Final decision expected 2028; major construction 2028-2034; Carney's "this summer" framing refers to enabling works | Northern remoteness premium real. Workforce mix tilts toward heavy-equipment operators, labourers, less specialized trades. |
| **Grays Bay Road and Port** | Mar 12 | NU | West Kitikmeot Resources Corp. (Inuit-owned) | 230 km road; deepwater port + airfield | $1.2B | EA status not specifically stated (pre-MPO referral preparation) | (Listed on MPO main projects page; no separate IAAC URL surfaced) | Yes — 670 construction jobs; 390 operations/maintenance | 1 | n/a | per km / per $-capex | Construction start target 2029; ~5-year build | Smaller in workforce magnitude than Mackenzie Valley. Northern remoteness same caveat. |
| **Arctic Economic and Security Corridor (NWT segment)** | Mar 12 | NT | Tlicho Government + Yellowknives Dene First Nation + NWT Government partnership | ~400 km all-season road through Slave Geological Province | TBD; cost estimate under development | EA in design phase; regulatory framework being determined | (No dedicated public EA URL yet) | No — workforce not disclosed | 2 | Mackenzie Valley Highway per-km ratio (preliminary 14K jobs / 800 km = 17.5 jobs-equivalent/km), then × 400 km = ~7,000 jobs-equivalent; flag as proportional analog | per km | Regulatory reviews and funding through 2028 | Same northern-remoteness caveat. Indigenous-led governance may shift labour-sourcing approach (local hire targets). |
| **Taltson Hydro Expansion** | Mar 12 | NT | NWT Government + First Nations and Métis governments | +60 MW (doubling existing 18 MW system) | $2-3B (2025 NWT forecast) | Preconstruction and consultation phase | (Federal page listed under MPO main; no project-specific IAAC URL surfaced) | No — proponent has not disclosed construction workforce | 2 | Site C scaled to small size — 7 person-years/MW × 60 MW = 420 person-years main civils; PLUS northern multiplier | per MW | Timeline not finalized | Northern-remoteness premium especially relevant given site access (winter road only in part). |
| **Carney-Smith west-coast oil pipeline** | Carney-Smith (separate; expected MPO referral July 1, 2026) | AB / BC (primary AB origin; ROW through BC; coastal terminus TBD) | TBD — no proponent committed; gov-to-gov implementation agreement May 15, 2026; Enbridge "warming up" per industry reporting | 1M+ barrels/day; length ~1,150-1,300 km (Edmonton-area to Pacific) | TBD — no public capex estimate; TMX cost $34B over ~1,150 km suggests $35-50B range | No EA filed yet — pipeline to be designated national interest by Oct 1, 2026 if process holds | (None yet — pre-application stage) | No — proponent not committed; no project documents | 2 | **TMX as canonical analog: 67,423 person-years over ~1,150 km = 58.6 person-years/km.** Coastal GasLink for gas-pipeline contrast (~6,000 peak / 670 km over construction period 2019-2023) | per km | Construction start target Sep 1, 2027; 4-6 yr build window plausible | **Highest-uncertainty single project in the inventory.** Bill C-48 west-coast tanker ban legal mechanism unresolved. Pathways CCS pairing structurally tied. Indigenous-equity participation expected but not yet specified. |

---

## Transformative strategies (NOT individual construction projects — track but do not aggregate into demand)

| Strategy | Tranche | Notes for Thompson |
|---|---|---|
| **Northwest Critical Conservation Corridor** | Nov 13 | Framework strategy covering BC + Yukon Golden Triangle. Specific projects (Red Chris, Ksi Lisims) already in the main inventory. Don't double-count. |
| **Port of Churchill Plus** | Sept 11 | Manitoba; currently a market-sounding study ($248,600 federal); no construction-phase capex yet. Track for future tranches. |
| **Alto High-Speed Rail** | Sept 11 | Toronto-Quebec City 1,000 km HSR; construction starts 2029 (Ottawa-Montreal segment first); 51,000 jobs over 10 years quoted. Outside the 2026-2029 peak-concurrence window for the primary headline but worth a sidebar. |
| **Wind West Atlantic Energy** | (referred but date not confirmed in search; transformative strategy tier) | 60+ GW offshore wind potential; first phase 5,000 MW could produce 24 TWh/yr. No FID, no specific projects yet. Outside scope unless Thompson finds a specific Atlantic offshore-wind project that has FID. |
| **Critical Minerals Strategy** | (umbrella strategy) | $2B Critical Minerals Sovereign Fund + $1.5B First and Last Mile Fund. Specific mining projects under it (Matawinie, Crawford, McIlvenna, Sisson) already in the main inventory. |
| **Arctic Economic and Security Corridor** | Mar 12 | Now broken out into four specific projects (Mackenzie Valley Hwy, Grays Bay R&P, NWT corridor segment, Taltson). Counted as four projects in main inventory. |

---

## Per-project detailed notes

### LNG Canada Phase 2

Phase 1 (~14 MTPA) achieved first cargo June 2025 at ~$40B CAD cumulative spend ([LNG Canada construction page](https://www.lngcanada.ca/what-we-do/construction/)). Peak construction workforce was 7,500-9,400 depending on shift-roll counting; cumulative ~35,000+ workers over the lifecycle. Trade categories named in Phase 1 disclosures: pipe welders ("more than 380"), pipefitters, electricians, heavy-equipment operators.

Phase 2 is structurally similar but uses modular fabrication for major equipment — same approach as Phase 1, which compresses peak on-site labour relative to stick-built. The proponent has flagged FID expectation by end-2026 ([BOE Report May 14, 2026](https://boereport.com/2026/05/14/lng-canada-to-make-decision-on-phase-2-expansion-by-end-of-year-canada-minister-says/)). Asian LNG market is softening post-2027 amid US LNG glut, which is a meaningful FID risk.

**Method-1 anchor:** apply Phase 1 ratios scaled to +14 MTPA capacity. Caveat: marine construction tied to Berth 1 demolition and quay wall + dredging extends to 2028 separate from process-train construction. Thompson should pull the Fluor Phase-1 case study + LNG Canada workforce page for trade-mix detail (Phase 1 was Fluor / JGC EPC).

### Darlington New Nuclear (4 SMR units)

Highest-confidence project in the inventory for trade-mix disclosure. OPG has explicitly named the first-cohort trades: iron workers, millwrights, boilermakers ([ANS Nuclear Newswire](https://www.ans.org/news/2025-05-12/article-7014/opg-gets-final-permission-to-construct-first-north-american-smr/)). The 18,000 jobs/yr "fleet construction average" figure includes indirect — Thompson should disaggregate direct on-site vs supply chain before using it.

BWRX-300 is designed for factory-assembly of major modules. On-site construction labour intensity is intentionally lower than CANDU refurbishment (Pickering 5-8, Bruce C). The Vogtle analog (US, conventional AP1000, much higher labour intensity) is a poor fit. Better analog if needed for time-phasing: the original Darlington construction (1981-1993) at much higher worker counts, scaled down for SMR-fleet design.

CNSC construction licence granted May 8, 2025 ([ANS](https://www.ans.org/news/2025-05-12/article-7014/opg-gets-final-permission-to-construct-first-north-american-smr/)). Tunnel boring machine "Harriett Brooks" being assembled early 2026. First unit in service end-2030; subsequent units staggered through ~2035.

### Contrecoeur Container Terminal

EA #80116 approved by IAAC ([project page](https://iaac-aeic.gc.ca/050/evaluations/proj/80116)). Carney announced ground-break April 9, 2026, with $1.16B CIB financing commitment ([MRO Magazine](https://www.mromagazine.com/2026/04/11/construction-begins-on-contrecoeur-container-terminal-expansion-at-port-of-montreal/)). Site prep underway; major construction activity 2026-2030; operations target 2030.

The Port of Montreal Authority disclosed ~4,000 jobs during construction (direct + indirect). Thompson should ask Port of Montreal IR or use a port-construction direct-share rule (~50-60% direct typical) to get the on-site labour estimate. Trade mix is heavy on civil/marine — pile drivers, ironworkers (rebar + dock structure), heavy-equipment operators, electricians. Use the Vancouver Port expansions as adjacent reference if needed.

### McIlvenna Bay Foran Copper Mine

Effectively in commissioning. Wet commissioning began February 14, 2026 ([Foran October 2025 update](https://foranmining.com/news-media/foran-news-releases/foran-advances-development-at-mcilvenna-bay-in-october-2025/)). Commercial production target mid-2026. Construction workforce peaked at ~800 (Oct 2025); operational steady-state ~400.

For Thompson: this is the closest "complete dataset" Canadian critical-minerals construction reference. Useful as the labour-intensity coefficient for Crawford and Sisson trade-mix proxies. Trades named in Foran hiring: heavy-duty mechanics, equipment operators, electricians, miners, pipefitters, underground truck operators, welders.

**Important:** McIlvenna Bay's construction labour is mostly behind us; this project contributes essentially nothing to 2026-2029 peak-concurrence math. Track for completeness, exclude from peak-window aggregation.

### Red Chris Mine Expansion

Operated by Newcrest Red Chris Mining (Newmont subsidiary). $2.6B capex disclosed by Newmont. The transition is from open-pit to block-cave underground — a structurally different mining method, with heavier reliance on tunnelling specialists, ventilation engineers, geotechnical trades.

Workforce: 1,800 peak construction; 1,500 operational. Tahltan Nation IBA in place ([Tahltan information package](https://tahltan.org/red-chris-block-cave-information-package/)).

EA status: BC EAO + IAAC review process; provincial 1P1P fast-tracking applies. Block cave construction methodology means typical mining labour-mix coefficients overstate equipment-operator share and understate tunnelling/drilling specialist share. Thompson should flag this when comparing to McIlvenna Bay (open-pit).

### Ksi Lisims LNG + Prince Rupert Gas Transmission

Ksi Lisims LNG: 12 MTPA floating LNG (FLNG), two units at Pearse Island. Joint venture of Western LNG (US) + Rockies LNG (Canadian producers consortium) + Nisga'a Nation. Capex $9.9B base / $11.8B with power barges ([Offshore-Technology](https://www.offshore-technology.com/projects/ksi-lisims-lng-project-british-columbia-canada/)). Peak construction 800; permanent 250. BC EAO certificate granted late 2025.

PRGT pipeline: 750-800 km, 42-inch, owned by Nisga'a Nation + Western LNG since 2024. ~$10B capex. EAO certificate kept valid June 2025; construction notice issued Aug 2024; FID early 2026. Pipeline trade-mix is welder-heavy (~20-25% welders + welder-helpers by industry rule; Coastal GasLink had "more than 380 pipe welders" cumulative as a Canadian gas-pipeline reference).

For Thompson: combine Ksi Lisims LNG (Method 1) + PRGT (Method 2, with Coastal GasLink as the gas-pipeline analog at ~6,000 peak over 670 km). Note PRGT construction is already underway (started Aug 2024) — labour demand is partially already in BuildForce's 2025 vintage if BuildForce caught it.

### Canada Nickel Crawford

42 km north of Timmins. World's #2 nickel reserve. $3.5B total capex; $1.9B Phase 1. Construction jobs 2,000; operational 1,300. IAAC draft Impact Assessment Report published May 11, 2026, with public comment period to June 10, 2026 ([IAAC project 83857](https://iaac-aeic.gc.ca/050/evaluations/proj/83857?culture=en-CA)).

Federal loan of up to $500M reportedly under negotiation ([MINING.com](https://www.mining.com/canada-nickel-may-net-368m-government-loan-for-giant-crawford-project-in-ontario/)). Ground-break target end-2026; first production target Q4 2028.

Trade mix not separately disclosed; use Foran McIlvenna mix as proxy (heavy-duty mechanics, equipment operators, electricians, miners, pipefitters, welders), adjusted for nickel processing vs copper-zinc differences (nickel processing typically uses more chemical-engineering / instrumentation trades on the mill side).

### Matawinie Graphite Mine

NMG construction officially launched May 19, 2026 ([PM ground-break](https://www.pm.gc.ca/en/news/news-releases/2026/05/19/prime-minister-carney-breaks-ground-nouveau-monde-graphites-matawinie)). $459M EDC + CIB financing package; $113M Canada Growth Fund commitment. Total ~$2B project value.

106,000 tpa graphite output. "Mine of the Future" branding — all-electric mining fleet — tilts trade mix toward electricians and instrumentation. Construction + commissioning 31 months → commercial production end-2028.

1,000+ jobs across construction + operations; 300+ ongoing once operational ([businesswire ground-break release](https://www.businesswire.com/news/home/20260519206180/en/Nouveau-Monde-Graphite-Officially-Launches-Construction-of-the-Matawinie-Mining-Project-With-a-Ground-Breaking-Ceremony)). Linked to the Bécancour Battery Materials Plant (downstream processing — separate project, not on the MPO list as a discrete referral).

### Sisson Tungsten Mine

Northcliff Resources operator (88.5% interest); Sisson Partnership entity. Tungsten-molybdenum; 27-year mine life; $579M capex. Federal + provincial EA approved 2017 — this is the oldest EA filing in the inventory.

500 construction jobs; 300 operational. May 2026: US DoD $20.7M + GoC $8.2M committed for engineering and updated feasibility studies — meaning construction financing is NOT yet committed. Realistic construction start: 2027 if sanctioned.

Smallest of the named mining projects. Trade-mix not separately disclosed; use generic mining coefficient.

### Iqaluit Nukkiksautiit Hydro

Nunavut Nukkiksautiit Corporation (NNC), 100% Inuit-owned. 15-30 MW; ~$500M (2017 estimate). EA in progress. Federal $6M for project development (Jan 2026). Operational by 2033.

**No proponent-disclosed workforce.** Method 2 mandatory. Site C analog (~7 person-years/MW main civils) gives 105-210 person-years — but this clearly under-states actual demand because the Site C coefficient is from a road-accessible southern BC location with deep institutional capacity. Northern construction premium (logistics, fly-in/fly-out staffing, winter-road windows, fuel logistics) is real but not cleanly quantified in published literature.

Thompson should flag this as a +30-60% adjustment band on the Site C coefficient and document the choice transparently. The Inuvik-area diesel-to-renewables studies (smaller-scale precedents) are the closest northern reference.

### North Coast Transmission Line (NCTL)

BC Hydro, ~445 km total at 500 kV. Phase 1 (170 km Prince George-Glenannan) construction starts summer 2026; in service fall 2030. Phase 2 (130 + 145 km segments) in service mid-2032. $139.5M CIB early-works loan; part of BC Hydro's $4.7B North capex.

Disclosure says "thousands" of construction jobs without project-specific peak. **Method 2.** Best Canadian transmission reference: Hydro One Bruce-to-Milton 500 kV line (post-completion); US literature (CleanEnergyGrid) cites ~17 jobs/km for major builds. 445 km × 17 = ~7,500 jobs-equivalent total, but US figures don't translate 1:1 (Canadian labour costs higher; rougher terrain adjustments).

Trade mix: ironworkers (tower construction), linemen, heavy-equipment operators, surveyors. BC Hydro's institutional preference for local hire is well-documented from the Site C precedent.

### Mackenzie Valley Highway

800 km road; $1.5B+. NWT Government + Indigenous communities. EA expected 2026-2027; final decision 2028; 6.7 km section already completed 2024 (95 employed on that section).

Globe and Mail cites "preliminary estimate suggests 14,000+ construction jobs potential" ([Globe](https://www.theglobeandmail.com/business/article-a-list-of-carneys-major-projects-centred-on-the-north/)) — Thompson should treat this as a planning estimate, not a verified peak. 14,000 jobs over 800 km = 17.5 jobs-equivalent/km, which is roughly comparable to US transmission line per-km coefficients — suspiciously round. Verify against the actual NWT government source before using.

Trade mix tilts heavy-equipment operator + labourer; less specialty trades than nuclear/LNG/pipeline. Northern remoteness premium applies (same caveat as Iqaluit).

### Grays Bay Road and Port

230 km all-season road + deepwater port + airfield. $1.2B. West Kitikmeot Resources Corp. (Inuit-owned). Construction start 2029; 5-year build.

670 construction jobs; 390 operations/maintenance ([Globe G&M](https://www.theglobeandmail.com/business/article-a-list-of-carneys-major-projects-centred-on-the-north/)). Smaller-magnitude workforce.

EA status: not specifically detailed in search results. Thompson should check the IAAC public registry for Grays Bay Road and Port Project. Northern remoteness same caveat.

### Arctic Economic and Security Corridor (NWT segment)

~400 km all-season road through Slave Geological Province. Tlicho Government + Yellowknives Dene First Nation + NWT Government partnership. EA in design; framework being determined. No published capex; no published workforce.

**Method 2.** Use Mackenzie Valley Highway per-km ratio scaled to 400 km. If MVH is 14K jobs / 800 km = 17.5 jobs-equivalent/km, then ~7,000 jobs-equivalent. Same northern-remoteness caveats. Indigenous-led governance may shift labour-sourcing patterns (local-hire targets, training-incorporated builds).

### Taltson Hydro Expansion

+60 MW (doubling existing 18 MW base). NWT Government + First Nations and Métis governments. $2-3B (2025 NWT forecast). Preconstruction and consultation phase; timeline not finalized.

**Method 2.** Site C coefficient (~7 person-years/MW main civils) × 60 MW = 420 person-years main civils. Apply northern multiplier (+30-60%) → 550-670 person-years. Modest magnitude in national-gap context.

### Carney-Smith west-coast pipeline

**This is the highest-uncertainty single project in the inventory and likely the single largest single-project workforce demand if it proceeds.**

May 15, 2026 Carney-Smith Implementation Agreement ([CBC](https://www.cbc.ca/news/politics/carney-smith-energy-announcement-mou-9.7200652)). Alberta to submit application to MPO by July 1, 2026; designation target Oct 1, 2026; construction start as early as Sept 1, 2027. 1M+ bpd capacity targeting Asian markets. ~1,150-1,300 km route (Edmonton-area to Pacific terminus; route + terminus not yet confirmed).

**No proponent committed.** Enbridge "warming up" per industry reporting ([EnergyNow May 2026](https://energynow.ca/2026/05/warming-up-enbridge-warms-up-to-new-alberta-to-b-c-oil-pipeline-after-carbon-compromise/)). CIBC analysts have called the 2027 construction-start timeline "best-case scenario" ([CBC](https://www.cbc.ca/news/canada/edmonton/alberta-west-coast-pipeline-9.7204537)).

**Method 2.** TMX is the canonical analog: 67,423 person-years over ~1,150 km = 58.6 person-years/km ([TMX EY report](https://docs.transmountain.com/EY-Report_TMEP_EN.pdf); Conference Board reference cited at 58,037 person-years). Scaling linearly to 1,150-1,300 km gives 67-76K person-years. Apply a +10-20% terrain adjustment if route is genuinely rougher than TMX (which itself was extensively brownfield-twinned).

**Regulatory complications:**
- Bill C-48 (BC tanker ban north of Vancouver Island) restricts crude tanker traffic — legal mechanism to override/amend not resolved.
- Pathways Alliance CCS pairing is structurally tied to the political case; Pathways "backpedalling" per May 2026 reporting ([National Observer](https://www.nationalobserver.com/2026/05/20/news/flagship-20-billion-plus-carbon-capture-megaproject-lowered-goals-ottawa-alberta-oilsands-deal)) weakens the package.
- Indigenous consultation: 14 First Nations have active court challenges to Bill C-5 and Ontario Bill 5; west-coast pipeline route Indigenous engagement entirely pending.

Trade mix: from TMX disclosure, "operating engineers, labourers, plumbers, pipefitters, teamsters"; "up to ~20% apprentices" by company admission. Pipeline-class workforce is welder/pipefitter-heavy (~20-25% of total).

---

## Notes on what NOT to count

Pathways Alliance CCS is referenced in the brief but is **not currently MPO-referred** as a standalone project. It is referenced under the Carney-Smith Implementation Agreement as a paired commitment. The 100,000 jobs / $16.5B GDP figure for Pathways is a proponent claim of unknown methodology and should not be treated as verified per the methodology note ([skilled_trades_gap_methodology_2026-05.md](skilled_trades_gap_methodology_2026-05.md)). Thompson can layer it in separately if Pathways reaches FID, but it should not be in the primary MPO-portfolio aggregate.

Pickering 5-8 and Bruce C nuclear refurbishment are referenced in the brief's working doc but are **not on the MPO referred list as of May 2026.** These are Ontario provincial projects with their own approval tracks. Pickering's 37,000 total-jobs figure is press-release sum; Bruce C's 18,900 over construction is also press-release. Both are Ontario-Crown projects and would be in BuildForce's "Major Projects" submodule already. Thompson should keep them outside the MPO-portfolio aggregate, citation-flag them, and use BuildForce baseline reconciliation to handle them.

Cedar LNG is referenced in passing in the methodology doc but is **a BC provincial-flagged project, NOT MPO-referred.** It is Haisla-Nation-led FLNG at Kitimat; ~$4.7B; ~500 peak construction; completion 2028. Already under construction. Same handling as Pickering/Bruce — flag, exclude from MPO aggregate, reconcile via BuildForce baseline.

---

## What Thompson should do first

1. Open IAAC Canadian Impact Assessment Registry ([iaac-aeic.gc.ca](https://iaac-aeic.gc.ca/)) and pull the EA project records for each of the 11 Method-1 projects. Capture trade-mix detail beyond what's in this table.
2. Email LNG Canada IR for the Phase-1 trade-mix breakdown if not in public Fluor case study — they have it.
3. Email OPG / Ontario Power Generation Communications for the Darlington SMR Phase-1 trade-mix breakdown (700 new hires, by trade).
4. Pull the Foran McIlvenna hiring page for the live trades list — it is the cleanest contemporary Canadian critical-minerals trade-mix anchor.
5. Verify the Globe's "14,000+ construction jobs" Mackenzie Valley figure against the NWT government / Department of Infrastructure source ([inf.gov.nt.ca/en/MVH](https://www.inf.gov.nt.ca/en/MVH)).
6. For the Carney-Smith pipeline: pull the TMX EY Economic Impact Assessment ([EY-TMEP](https://docs.transmountain.com/EY-Report_TMEP_EN.pdf)) and the Trans Mountain "Economic Benefits: Jobs & Procurement" brochure for the canonical analog coefficient.

---

## Source endnotes (primary)

- MPO main page: https://www.canada.ca/en/privy-council/major-projects-office.html
- MPO projects list: https://www.canada.ca/en/privy-council/major-projects-office/projects/national.html (returns HTTP 403 to WebFetch; navigable in browser)
- First tranche (Sept 11, 2025): https://www.pm.gc.ca/en/news/news-releases/2025/09/11/prime-minister-carney-announces-first-projects-be-reviewed-new
- Second tranche (Nov 13, 2025): https://www.pm.gc.ca/en/news/news-releases/2025/11/13/prime-minister-carney-announces-second-tranche-nation-building-projects
- Northern tranche (Mar 12, 2026): https://www.pm.gc.ca/en/news/news-releases/2026/03/12/prime-minister-carney-announces-ambitious-new-plan-defend-build-and
- Carney-Smith Implementation Agreement (May 15, 2026): https://www.cbc.ca/news/politics/carney-smith-energy-announcement-mou-9.7200652
- Blakes second-tranche bulletin: https://www.blakes.com/insights/second-tranche-of-projects-referred-to-canada-s-major-projects-office/
- BLG MPO bulletin: https://www.blg.com/en/insights/2025/12/fast-tracking-canadas-future-recent-projects-announced-by-the-major-projects-office
- Globe and Mail northern tranche: https://www.theglobeandmail.com/business/article-a-list-of-carneys-major-projects-centred-on-the-north/

(Project-specific URLs are embedded inline in the table and detailed notes.)
