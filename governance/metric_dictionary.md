# Metric Dictionary

**Status:** Approved metric set, transferred from `Knowledge/DATA_AND_KNOWLEDGE_ASSESSMENT.md` §8 per CLAUDE.md.
**Transferred:** 2026-07-17. Adding, removing, or redefining a metric requires owner approval.
**Code history:** every `schedule + variable_code` below was verified present in row 3 of its worksheet in **all eight workbooks (2018–2025)** during the 2026-07-17 read-only audit.

## Extraction rules (apply to every metric)

1. Extract by **worksheet (schedule) + variable code from row 3** — never by fixed column position.
2. Municipality key is the financial `CODE` read **as text** (leading zeros preserved): Edmonton `0098`, Calgary `0046`.
3. Per-capita denominators use **only** the population-estimates workbook (CSD codes `4811061` Edmonton, `4806016` Calgary). The population schedule inside the financial workbooks is never used — it is absent 2020–2022 and stale (1,010,899 repeated) for 2023–2025.
4. Blank cells → `missing`; explicit 0 → `reported_zero`. The two states are never merged.
5. All dollar amounts are **nominal**; no inflation adjustment is approved.
6. Every curated value carries `source_file`, `source_sheet`, `variable_code`, `year`.

## A — Growth and operating scale

| metric_id | Name | Source | Unit | Notes |
|---|---|---|---|---|
| `pop` | Population | Population estimates workbook, CSD row, year column | persons | July 1 estimate |
| `pop_growth` | Annual population growth | derived: `pop[y] / pop[y-1] − 1` | % | |
| `rev_total` | Total revenue | `C(1)-Revenue` · `01140` | $ nominal | |
| `exp_total` | Total expense | `C(1)-Revenue` · `01580` | $ nominal | gold-example input |
| `rev_per_capita` | Revenue per capita | derived: `rev_total / pop` | $ nominal / person | |
| `exp_per_capita` | Expense per capita | derived: `exp_total / pop` | $ nominal / person | gold example: 2025 = $3,265.73 |
| `net_rev_exp` | Net revenue/expense | `C(1)-Revenue` · `01590` | $ nominal | |

## B — Debt and fiscal capacity

| metric_id | Name | Source | Unit | Notes |
|---|---|---|---|---|
| `debt_total` | Total debt | `AA(1)-Debt` · `05710` | $ nominal | gold: 2025 = $4,592,150,000 |
| `debt_limit` | Debt limit | `AA(1)-Debt` · `05700` | $ nominal | regulated limit; gold: 2025 = $7,748,380,000 |
| `debt_utilization` | Debt utilization | derived: `debt_total / debt_limit` | % | gold: 2025 = 59.27% (59.2659%) |
| `debt_service_cost` | Total debt-service costs | `AA(1)-Debt` · `05730` | $ nominal | |
| `debt_service_limit` | Debt-service limit | `AA(1)-Debt` · `05720` | $ nominal | |
| `debt_service_utilization` | Debt-service utilization | derived: `debt_service_cost / debt_service_limit` | % | |
| `net_financial_assets` | Net financial assets / net debt | `A(1)-Total` · `00395` | $ nominal | negative = net debt |
| `accumulated_surplus` | Accumulated surplus | `A(1)-Total` · `00450` | $ nominal | |

## C — Tax base and revenue capacity

| metric_id | Name | Source | Unit | Notes |
|---|---|---|---|---|
| `equalized_assessment` | Equalized assessment | `EA(1)-Assessment` · `08260` | $ nominal | |
| `assessment_per_capita` | Assessment per capita | derived: `equalized_assessment / pop` | $ nominal / person | |
| `property_tax` | Property taxes and grants in place | `K(3)-Total` · `04000` | $ nominal | |
| `mill_rate_res` | Residential general municipal mill rate | `MR(3)-Mill Rate` · `10030` | mills | rate, not dollars |
| `mill_rate_nonres` | Non-residential general municipal mill rate | `MR(3)-Mill Rate` · `10034` | mills | rate, not dollars |

## D — Service and operational pressure

| metric_id | Name | Source | Unit | Notes |
|---|---|---|---|---|
| `exp_police` | Police expense | `C(1)-Revenue` · `01210` | $ nominal | functional expense |
| `exp_fire` | Fire expense | `C(1)-Revenue` · `01220` | $ nominal | |
| `exp_roads` | Roads, streets, walks, lighting expense | `C(1)-Revenue` · `01290` | $ nominal | |
| `exp_transit` | Public transit expense | `C(1)-Revenue` · `01310` | $ nominal | |
| `exp_parks_rec` | Parks and recreation expense | `C(1)-Revenue` · `01530` | $ nominal | |
| `exp_culture` | Culture expense | `C(1)-Revenue` · `01540` | $ nominal | |
| `fte_total` | Total full-time municipal positions | `ST(1)-Stat` · `05500` | positions | |
| `svc_per_capita_<fn>` | Selected service expense per capita | derived: `exp_<fn> / pop` | $ nominal / person | per function above |
| `svc_share_<fn>` | Selected service expense share | derived: `exp_<fn> / exp_total` | % | per function above |
| `fte_per_1000` | FTE per 1,000 residents | derived: `fte_total / (pop / 1000)` | per 1,000 | 2025 = 9.62 |

## Comparability status

- All Domain A–D source codes: **stable 2018–2025 (verified)** — usable for longitudinal tests.
- Peer (Calgary / Alberta cities) values for **2025 are provisional**: 306 of 332 returns received.
- Statistical schedule (`ST(1)-Stat`) changes more over time than financial schedules; only code `05500` is approved from it.

## Known-answer anchors (owner-approved 2026-07-17, G3)

| Check | Year | Expected | Tolerance |
|---|---|---|---|
| Gold: debt utilization | 2025 | 59.2659% | ±0.01 pp |
| Gold: expense per capita | 2025 | $3,265.7307 | ±$0.01 |
| Extra 1: debt utilization | 2022 | 64.11% (3,940,329,000 / 6,146,130,000) | ±0.01 pp |
| Extra 2: FTE per 1,000 | 2025 | 9.6237 (11,917 / 1,238.295k) | ±0.001 |
