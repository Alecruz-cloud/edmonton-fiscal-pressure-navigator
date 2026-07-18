# Data and Knowledge Assessment

**Project:** Edmonton Municipal Financial Decision Support App  
**Course:** MMA 616 – Managing Intelligence  
**Status:** Draft v0.1  
**Assessment date:** July 16, 2026

## 1. Purpose of this assessment

This document determines whether the available data can support a useful, testable, and governable agentic application focused on the City of Edmonton. It defines the Knowledge Stock that should be curated before the Living Spec (`CLAUDE.md`) is written.

The proposed application should not be a generic municipal dashboard. Its purpose is to help a municipal finance or strategy leader identify which financial pressures in Edmonton deserve priority review before a budget or capital-planning cycle, using historical evidence and carefully bounded comparisons.

## 2. Source inventory

### Source A: Municipal Financial and Statistical Data

Eight annual Excel workbooks were provided:

| Financial year | Worksheets | Valid municipal financial returns | Edmonton present |
|---:|---:|---:|:---:|
| 2018 | 42 | 342 | Yes |
| 2019 | 42 | 339 | Yes |
| 2020 | 42 | 336 | Yes |
| 2021 | 42 | 334 | Yes |
| 2022 | 43 | 332 | Yes |
| 2023 | 49 | 329 | Yes |
| 2024 | 50 | 327 | Yes |
| 2025 | 51 | 306 | Yes |

**Important:** the 2025 workbook explicitly reports **306 of 332** Financial Information Returns. Edmonton is included, but 2025 peer benchmarking may be incomplete for municipalities that had not yet reported.

### Source B: Alberta Census Subdivision Population Estimates

One Excel workbook contains:

- 464 rows;
- Census Subdivision identifiers;
- municipal area name and type;
- annual population estimates from 2016 through 2025;
- Edmonton population estimates for every year in the project period.

Edmonton population in the population source:

| Year | Population |
|---:|---:|
| 2018 | 1,002,920 |
| 2019 | 1,026,499 |
| 2020 | 1,046,556 |
| 2021 | 1,050,945 |
| 2022 | 1,073,454 |
| 2023 | 1,127,183 |
| 2024 | 1,197,770 |
| 2025 | 1,238,295 |

### Source C: StatCan 2021 Census cartographic boundary file — census subdivisions *(added 2026-07-17, owner-approved)*

`data/raw/lcsd000b21a_e.zip` (148.8 MB, Statistics Canada, downloaded 2026-07-17,
EPSG:3347). Approved for one purpose only: deriving the Alberta provincial outline and
the 19 reporting-city centroids for the dashboard's context map
(`pipeline/build_geo.py`). It is never a source of financial or population values, and
its addition changes no metric, threshold, or signal. City matching to the financial
codes is governed by the extended crosswalk (`governance/municipality_crosswalk.csv`,
sign-off in `governance/crosswalk_signoff.md`) with geo-only scope for the 17 non-focus
cities.

## 3. Recommended analytical focus

### Primary municipality

The application should be centred on **Edmonton**, using municipal code **0098** in the financial workbooks.

### Benchmarking hierarchy

Edmonton has no close population peer among most Alberta municipalities. Therefore, the app should not present all cities as equally comparable.

Use three explicit comparison lenses:

1. **Edmonton historical trend** – the primary and most defensible benchmark.
2. **Calgary scale peer** – the closest Alberta comparison in municipal scale and complexity.
3. **Alberta city context** – median or distribution across reporting cities, clearly labelled as context rather than a direct peer comparison.

Optional secondary reference cities may include Red Deer, Lethbridge, and Grande Prairie, but the application must state that their scale and service responsibilities differ materially from Edmonton.

## 4. Unit of analysis and keys

### Financial data

The annual financial workbooks use a repeatable structure:

- `YEAR`
- `STATUS`
- `CODE`
- `MUNICIPALITY`
- one or more financial/statistical variables

The most reliable municipality key is:

- financial municipality code: `0098` for Edmonton;
- year;
- schedule;
- variable code from row 3 of each worksheet.

Variable codes should be used as the primary metric identifiers because column positions and some labels change over time.

### Population data

Population records use:

- Census Division;
- Census Subdivision code;
- Area Name;
- Type;
- annual population columns.

Edmonton's Census Subdivision code is **4811061**.

### Required crosswalk

Create a maintained municipality crosswalk with:

- `financial_municipality_code`
- `financial_name_raw`
- `financial_status`
- `name_normalized`
- `census_subdivision_code`
- `population_name_raw`
- `population_type`
- `match_method`
- `match_status`
- `review_note`

For Edmonton, the crosswalk is straightforward:

| Financial code | Financial name | CSD code | Population name | Match status |
|---|---|---:|---|---|
| 0098 | EDMONTON | 4811061 | Edmonton3 * | Confirmed |

## 5. Structural assessment

### Stable core

Forty worksheets are common across all eight financial years. Several high-value schedules have stable variable-code structures across the complete period, including:

- `AA(1)-Debt`
- `EA(1)-Assessment`
- `MR(1)-Tax Levy`

These are strong candidates for the MVP.

### Schema drift

The workbook structure expands from 42 worksheets in 2018 to 51 in 2025. Examples include:

- salary and benefit schedules added from 2023;
- assessment detail added to the mill-rate section from 2023;
- new asset and remeasurement schedules in later years;
- variable additions or replacements in financial position, functional revenue/expense, tax, and statistical schedules.

The ingestion process must therefore map by **schedule + variable code**, not by fixed column position.

### Reporting coverage drift

The count of valid Financial Information Returns declines from 342 in 2018 to 306 in 2025. This does not prevent an Edmonton-focused analysis, because Edmonton is present in every year, but it affects peer medians and rankings.

Every benchmark output should display:

- reporting year;
- number of peer municipalities included;
- whether the year is complete or provisional;
- any municipalities excluded because of missing data.

## 6. Data quality findings

### 6.1 Population source conflict

The financial workbooks contain a population schedule only in some years. It is absent in 2020–2022, and Edmonton's population value is repeated as **1,010,899** in the 2023, 2024, and 2025 financial workbooks.

The separate population-estimates workbook provides updated values of:

- 1,127,183 in 2023;
- 1,197,770 in 2024;
- 1,238,295 in 2025.

**Decision:** use the separate population-estimates workbook as the authoritative population source for all per-capita calculations. Do not mix it with the financial workbook population field.

### 6.2 Municipality-name inconsistencies

Examples include:

- trailing spaces in financial names;
- uppercase financial names versus title-case population names;
- footnote numbers and asterisks in population names;
- reordered legal names such as “Municipality of” or “County of”;
- ambiguous names such as Cold Lake, which can refer to a city or a reserve;
- Lloydminster, which requires special handling because the city spans Alberta and Saskatchewan.

**Decision:** never join the complete sources using raw municipality name alone. Use a crosswalk and municipal type. For the Edmonton MVP, lock the confirmed codes directly.

### 6.3 Variable-code changes

Some schedules add or replace codes across years. For example:

- financial position adds new variables in later years;
- functional revenue/expense adds categories from 2023;
- revenue/expense by type replaces some transfer categories in 2023;
- statistical measures change more substantially over time.

**Decision:** each selected metric must have a documented code history and comparability rule. A metric should be excluded from longitudinal analysis when its meaning changes materially.

### 6.4 Nominal-dollar limitation

Financial amounts are nominal. Growth in revenue or expense cannot automatically be interpreted as real growth in fiscal capacity or service cost.

**Decision for MVP:**

- label dollar values as nominal;
- prioritize ratios, shares, utilization rates, and per-capita measures;
- do not claim that nominal cost growth represents efficiency deterioration;
- treat an inflation index as an optional future Knowledge Stock addition rather than silently adjusting values.

### 6.5 Zero versus missing

The source contains both zeroes and blanks. These must not be treated as equivalent without a variable-specific rule.

**Decision:** preserve raw values and add a validation status:

- `reported_value`
- `reported_zero`
- `missing`
- `not_applicable`
- `structurally_unavailable`

## 7. Proposed curated Knowledge Stock

### 7.1 Raw layer

Store the nine source workbooks unchanged under a read-only `data/raw/` directory.

### 7.2 Standardized long-form financial table

Recommended schema:

| Field | Description |
|---|---|
| `financial_year` | Reporting year |
| `municipality_code` | Alberta municipal code |
| `municipality_name_raw` | Original municipality label |
| `municipality_name` | Normalized display name |
| `municipality_status` | City, town, village, etc. |
| `schedule` | Workbook schedule name |
| `variable_code` | Stable source variable code |
| `variable_name` | Source variable label |
| `value` | Numeric or categorical source value |
| `source_file` | Original workbook |
| `source_sheet` | Original worksheet |
| `quality_status` | Reported, missing, not applicable, etc. |

### 7.3 Standardized population table

Recommended schema:

| Field | Description |
|---|---|
| `year` | Population-estimate year |
| `census_subdivision_code` | Census Subdivision identifier |
| `municipality_name_raw` | Original area name |
| `municipality_name` | Normalized display name |
| `municipality_type` | Source municipal type |
| `population` | July 1 population estimate |
| `source_file` | Original workbook |

### 7.4 Municipality crosswalk

Maintain the crosswalk as a first-class governed asset. Do not bury manual matching rules inside transformation code.

### 7.5 Metric mart

Create one narrow decision-ready table containing only the approved metrics for Edmonton and approved benchmarks.

Recommended grain:

`year × municipality × metric`

Recommended fields:

- `year`
- `municipality_code`
- `municipality_name`
- `metric_id`
- `metric_name`
- `metric_domain`
- `raw_value`
- `normalized_value`
- `unit`
- `source_schedule`
- `source_variable_code`
- `comparability_status`
- `data_quality_note`

## 8. Recommended MVP metric set

The first version should use a small, interpretable set rather than every available variable.

### A. Growth and operating scale

| Metric | Source |
|---|---|
| Population | Population estimates |
| Annual population growth | Derived |
| Total revenue | `C(1)-Revenue`, code `01140` |
| Total expense | `C(1)-Revenue`, code `01580` |
| Revenue per capita | Derived |
| Expense per capita | Derived |
| Net revenue/expense | `C(1)-Revenue`, code `01590` |

### B. Debt and fiscal capacity

| Metric | Source |
|---|---|
| Total debt | `AA(1)-Debt`, code `05710` |
| Debt limit | `AA(1)-Debt`, code `05700` |
| Debt utilization | Derived: total debt / debt limit |
| Total debt-service costs | `AA(1)-Debt`, code `05730` |
| Debt-service limit | `AA(1)-Debt`, code `05720` |
| Debt-service utilization | Derived |
| Net financial assets / net debt | `A(1)-Total`, code `00395` |
| Accumulated surplus | `A(1)-Total`, code `00450` |

### C. Tax base and revenue capacity

| Metric | Source |
|---|---|
| Equalized assessment | `EA(1)-Assessment`, code `08260` |
| Assessment per capita | Derived |
| Property taxes and grants in place | `K(3)-Total`, code `04000` |
| Residential general municipal mill rate | `MR(3)-Mill Rate`, code `10030` |
| Non-residential general municipal mill rate | `MR(3)-Mill Rate`, code `10034` |

### D. Service and operational pressure

Use selected functional expenses from `C(1)-Revenue`, preferably:

- police: `01210`;
- fire: `01220`;
- roads, streets, walks and lighting: `01290`;
- public transit: `01310`;
- parks and recreation: `01530`;
- culture: `01540`;
- total full-time municipal positions: `ST(1)-Stat`, code `05500`.

Derived measures may include:

- selected service expense per capita;
- selected service expense as a share of total expense;
- FTE per 1,000 residents.

## 9. Preliminary Edmonton feasibility signals

These are preliminary observations used only to test whether the data can support the proposed app. They are not yet policy conclusions.

From 2018 to 2025:

- population increased from 1,002,920 to 1,238,295, approximately **23.5%**;
- nominal total expense increased approximately **33.5%**;
- nominal expense per capita increased approximately **8.1%**;
- total debt increased approximately **50.8%**;
- debt per capita increased approximately **22.1%**;
- debt utilization increased from approximately **54.5%** to **59.3%**, after reaching approximately **64.1%** in 2022;
- FTE per 1,000 residents declined from approximately **10.20** to **9.62**.

These signals demonstrate that the data can support a focused question about whether Edmonton's financial and operational capacity is keeping pace with rapid population growth. The app must explain the evidence without treating any single change as proof of good or poor performance.

## 10. Decision the Knowledge Stock can support

A defensible decision statement is:

> Before a municipal budget or capital-planning review, identify the two or three Edmonton financial pressure areas that warrant deeper management attention, based on historical change, fiscal-capacity ratios, per-capita measures, and bounded comparison evidence.

The data can support prioritization for review. It cannot, by itself, determine whether Edmonton should raise taxes, reduce a service, borrow more, or change a capital project.

## 11. Governance boundary

The application may:

- identify unusual changes;
- calculate ratios and per-capita measures;
- compare Edmonton with defined reference groups;
- explain which metrics triggered a flag;
- produce a concise review brief with source traceability;
- state uncertainty and data limitations.

The application must not:

- label Edmonton financially healthy or unhealthy from one composite score;
- recommend tax increases, service reductions, layoffs, or borrowing decisions;
- imply causation from descriptive trends;
- rank municipalities without disclosing peer-selection and reporting coverage;
- hide missing data or provisional-year limitations;
- treat nominal growth as real growth without an inflation adjustment;
- replace professional financial review or Council accountability.

## 12. Recommended application concept

### Working concept

**Edmonton Fiscal Pressure Navigator**

A decision-support application for a municipal finance or corporate-strategy leader. It detects and explains Edmonton's most material financial pressure signals, shows the historical evidence, compares them with a clearly defined reference group, and creates a short management review brief.

### Why this concept fits the data

- Edmonton has complete financial coverage for 2018–2025.
- Population estimates are available for the same period.
- Stable source codes support reproducible calculations.
- Ratios and per-capita metrics reduce some scale distortion.
- Functional-expense fields make the output more actionable than a high-level balance-sheet dashboard.
- The app can be evaluated using known-answer calculations and user stories.

## 13. Knowledge acceptance criteria

The Knowledge Stock is ready for the Living Spec and build only when all of the following are true:

1. All eight financial workbooks ingest without manual annual edits.
2. Variable extraction is based on schedule and variable code, not column position.
3. Edmonton code `0098` is present for every year from 2018 to 2025.
4. Edmonton CSD code `4811061` is matched and documented.
5. Population calculations use only the external population-estimates source.
6. Every MVP metric has a documented formula, source schedule, code, unit, and comparability status.
7. Missing and zero values remain distinguishable.
8. Peer outputs show included municipality count and provisional-year warnings.
9. Known-answer tests reproduce at least three certified Edmonton calculations.
10. Raw files remain unchanged and every curated value is traceable to its source workbook, sheet, year, and variable code.

## 14. Candidate known-answer tests

The following 2025 Edmonton calculations can serve as initial gold checks after independent confirmation during the build:

- Population: **1,238,295**.
- Total debt: **$4,592,150,000**.
- Debt limit: **$7,748,380,000**.
- Debt utilization: approximately **59.27%**.
- Total expense: **$4,043,938,000**.
- Nominal expense per capita: approximately **$3,265.73**.

The final `CLAUDE.md` should select one primary gold example and require source traceability in the output.

## 15. Open decisions before writing the final CLAUDE.md

The data assessment supports proceeding. The Living Spec should resolve these product decisions explicitly:

1. Final primary user: Edmonton municipal finance manager, corporate strategy manager, or budget director.
2. Exact recurring decision moment: budget preparation, quarterly review, or capital-planning review.
3. Whether the main output is a ranked pressure list, an issue brief, or both.
4. Whether Calgary is always shown or selected by the user.
5. Maximum number of metrics included in the MVP.
6. Whether service-function analysis is limited to five high-value functions.
7. How the app defines a “material pressure” without creating a misleading composite score.

## 16. Assessment conclusion

The two datasets are suitable for an MMA 616 agentic project focused on Edmonton. They provide sufficient time coverage, financial depth, population context, stable identifiers, and known-answer opportunities.

The primary technical risk is not lack of data. It is incorrect harmonization, misleading peer comparisons, and overconfident interpretation. The Knowledge Stock should therefore be narrow, code-based, traceable, and governed before the application logic is built.
