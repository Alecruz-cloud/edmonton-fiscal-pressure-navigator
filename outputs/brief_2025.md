# Edmonton Fiscal Pressure Review Brief — 2025

**APPROVED for publication — project owner (Alejandro Cruz), 2026-07-18.** Drafted by the
municipal-finance-analyst capability from validated outputs only; approval recorded per the
governance rule that publishing a brief requires human sign-off.

## 1. Purpose and period

This brief supports pre-budget review prioritization for the City of Edmonton. It flags the financial pressure areas that most warrant deeper management analysis; it does not assess overall financial health. Evidence covers reporting years 2018–2025, with Edmonton's own history as the primary benchmark. **2025 coverage notice:** 306 of 332 Alberta financial information returns received — all 2025 peer comparisons are provisional. Signals evaluate nominal dollar figures; an owner-approved constant-2025$ CPI display context (StatCan 18-10-0005-01, All-items Alberta; approved 2026-07-18) is available in the drill-down and never feeds a test. Signals were generated under pressure rules **v1.2** (approved 2026-07-17), `governance/pressure_rules.md`; 22 metrics were evaluated.

## 2. Top signals (three surfaced; truncation disclosed below)

**Signal 1 — Parks & recreation expense per capita: High review priority.**
$295.97 per resident in 2025 (nominal), the most adverse value in the 2018–2025 history (2018: $278.34; 2020 low: $199.68). Triggered tests: **EH-1** (2025 is the 8-year historical maximum, exceeding the prior high of $286.21 in 2024); **EH-2** (+20.70% over 2022's $245.20, against a 10.0% threshold); **PP-1** (parks & recreation expense grew 39.24% over three years while population grew 15.36% — a 23.88 pp adverse gap against a 5.0 pp threshold). Supporting context only (**CX-1**, provisional): versus Calgary's 2025 value of $179.36, an adverse gap of 65.02% (relative to the comparator) against a 15% threshold. Per-capita spending in this function has moved ahead of both its own history and population growth — the widest test exceedances in this run.

**Signal 2 — Non-residential general municipal mill rate: High review priority.**
24.22 mills in 2025, the highest of the eight years on record (2018: 17.44). Triggered tests: **EH-1** (2025 exceeds the prior high of 22.66 in 2024); **EH-2** (+14.92% over 2022's 21.08, against a 10.0% threshold). Supporting context only (**CX-1**, provisional): versus Calgary's 2025 rate of 17.97, an adverse gap of 34.77% (relative to the comparator) against a 15% threshold; and versus the Alberta reporting-city median of 13.4191 mills — computed **excluding Edmonton** per rules v1.2 (n=18: Airdrie, Beaumont, Brooks, Calgary, Camrose, Fort Saskatchewan, Grande Prairie, Lacombe, Leduc, Lethbridge, Lloydminster, Medicine Hat, Red Deer, Spruce Grove, St. Albert, Wetaskiwin, Chestermere, Cold Lake) — an adverse gap of 80.51% (relative to the comparator) against a 15% threshold. The rate has risen in six of the last seven years and its recent movement exceeded the documented threshold.

**Signal 3 — Police expense per capita: High review priority.**
$509.96 per resident in 2025 (nominal), the highest in the 2018–2025 history (2018: $443.20). Triggered tests: **EH-1** (2025 exceeds the prior high of $490.56 in 2024); **PP-1** (police expense grew 24.67% over three years versus 15.36% population growth — a 9.32 pp adverse gap against a 5.0 pp threshold). EH-2 did not trigger (+8.08% over three years, below the 10.0% threshold). Supporting context only (**CX-1**, provisional): versus Calgary's 2025 value of $428.21, an adverse gap of 19.09% (relative to the comparator) against a 15% threshold. Growth outpaced population, though the 3-year percentage movement alone stayed under threshold.

**Truncated signals — 10 additional flagged signals not shown, per the three-signal limit (name and status):** `fte_per_1000` (**High review priority**); `mill_rate_res` (Watch); `exp_fire_per_capita` (Watch); `exp_transit_per_capita` (Watch); `assessment_per_capita` (Watch); `exp_per_capita` (Watch); `debt_service_utilization` (Watch); `debt_utilization` (Watch); `exp_culture_per_capita` (Watch); `exp_roads_per_capita` (Watch). Full test evidence for each is retained in `data/curated/signals.json`. Nine further metrics were not flagged (including `rev_per_capita`, `net_financial_assets`, and `accumulated_surplus`), with their full test evidence also published.

## 3. Evidence and source traces

All values come from the validated outputs `data/curated/signals.json` and `data/curated/metric_mart.json`; every curated value carries its source file, worksheet (schedule), variable code, and year. Extraction uses schedule + variable code (never column position); Edmonton's financial code is `0098`. Traces for the signals above:

- *Parks & recreation expense per capita* — derived `exp_parks_rec / pop`; numerator: annual `_financial_year.xlsx` workbooks, sheet `C(1)-Revenue`, code `01530`; denominator: `population-estimates-ab-census-subdivision-municipal-2016-to-current.xlsx`, CSD `4811061` (the only approved population source).
- *Non-residential mill rate* — annual `_financial_year.xlsx` workbooks, sheet `MR(3)-Mill Rate`, code `10034`. Alberta median rows in the mart name every included municipality and are computed excluding the subject (rules v1.2).
- *Police expense per capita* — derived `exp_police / pop`; numerator: sheet `C(1)-Revenue`, code `01210`; denominator as above.

Edmonton's own 2018–2025 history is the primary benchmark. Calgary (code `0046`) and Alberta reporting-city figures are supporting context only and can never create a high-priority signal.

## 4. Limitations

- Signal tests evaluate **nominal** dollars (rules v1.2). Real-dollar interpretation is supported only through the owner-approved constant-2025$ CPI display context (StatCan 18-10-0005-01, All-items Alberta, base 2025; approved 2026-07-18) shown in the drill-down — for example, Edmonton's 2018 expense per capita of $3,020.55 nominal is $3,699.43 in 2025 dollars, so the nominal 8.1% rise over 2018–2025 is a decline in real terms. Nominal test triggers are not evidence of real cost growth.
- **No forecasting.** With eight annual observations per metric, a predictive model would be statistically indefensible. A governed path exists — a longer approved return history, an owner-approved method with mandatory uncertainty reporting, and its own review gate — and remains future work outside this brief.
- 2025 peer comparisons are **provisional** (306 of 332 returns received). Alberta reporting-city medians **exclude Edmonton** (the subject is never part of its own comparator, rules v1.2) and name the included municipalities (2025: n=18).
- Findings are **descriptive**: no causal claims, no forecasts, no assessment of financial health, and no aggregation of signals into a score.
- Thresholds, tie-break rules, and comparator composition are documented analytical heuristics in `governance/pressure_rules.md` (v1.2, approved 2026-07-17), not City policy.

## 5. Follow-up questions for management

1. What drove the 39.24% three-year growth in parks & recreation expense — new facilities, service expansion, contract costs, or reporting changes — and is the pace expected to persist?
2. Which components of the non-residential mill-rate increase reflect deliberate rate decisions versus assessment-base movement, and how does this interact with the `assessment_per_capita` Watch flag and the provisional gaps versus Calgary and the Edmonton-excluded Alberta median?
3. What portions of police expense growth are settlement-driven, headcount-driven, or one-time, and how does the Calgary gap change once 2025 peer reporting is complete?
4. Should the truncated High review priority signal (`fte_per_1000`) be pulled into the next review cycle alongside these three?
5. Are any 2025 values affected by reporting or schedule changes that would alter comparability before conclusions are drawn?

This brief does not make policy recommendations. It flags areas for further analysis and management attention.
