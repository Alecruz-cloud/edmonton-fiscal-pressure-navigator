# Evaluation — Baseline (2026-07-17)

Method per `CLAUDE.md`: test the outputs, not the code. Each case records expected output,
actual output, pass/fail, evidence, failure home, correction, and result after revision.
Automated cases live in `tests/` (pytest) and the two skill code checks; narrative cases
are reviewed by the project owner, never scored by another model.

**Result: 8/8 baseline cases pass after one correction. 32 automated tests green.**

## Baseline test set

### 1. Gold example (Edmonton 2025)
- **Expected:** population 1,238,295; total debt $4,592,150,000; debt limit $7,748,380,000; utilization 59.27% (±0.01 pp); total expense $4,043,938,000; expense per capita $3,265.73 (±$0.01); full source trace; population from the estimates workbook only.
- **Actual:** utilization 59.265937%; per capita $3,265.7307; all six values reproduced with traces (see dashboard drill-down gold panel).
- **PASS** — evidence: `tests/test_known_answers.py` (7 tests) + `validate_mart.py` anchors.

### 2. Two additional known answers (different domains, owner-approved G3)
- **Expected:** 2022 debt utilization 64.11% (±0.01 pp); 2025 FTE per 1,000 = 9.6237 (±0.001).
- **Actual:** 64.11% and 9.623716.
- **PASS** — evidence: `test_extra_debt_utilization_2022`, `test_extra_fte_per_1000_2025`.

### 3. Missing-versus-zero case
- **Expected:** blanks stay `missing`, zeros stay `reported_zero`, never merged; the one genuine blank (Granum 0135, 2021 equalized assessment) surfaces as `missing`; 2025 debt schedule keeps 1,015 reported / 209 zeros.
- **Actual (first run):** **FAIL** — the test itself expected 4 missing values in 2025 `AA(1)-Debt`; the pipeline reported 0.
- **Evidence:** the 4 blanks sit on the workbook's footer row ("306 out of 332"), not on municipality returns; the pipeline was right, the audit note was wrong.
- **Failure home:** **Knowledge** (incorrect audit note), not Deliverables.
- **Correction:** test rewritten against verified truth; Granum case added as the genuine-missing anchor.
- **After revision:** **PASS** (`test_missing_and_zero_are_distinct_states`, `test_genuine_missing_value_preserved`).

### 4. Provisional peer-coverage case
- **Expected:** 2025 peer outputs labelled provisional; coverage 306 of 332 disclosed; included-municipality count shown on every median.
- **Actual:** meta + every AB_CITIES_MEDIAN 2025 row carries `provisional_peer_year`; medians disclose n; dashboard and brief repeat the notice.
- **PASS** — evidence: `test_2025_peer_rows_labelled_provisional`, `test_peer_rows_disclose_included_count`, `test_2025_coverage_is_306`.

### 5. Case that must NOT generate a high-priority signal
- **Expected:** `debt_utilization` 2025 triggers only the cross-sectional test (CX-1) → must be Watch, never High (cross-sectional alone cannot create High). `rev_per_capita` triggers nothing → Not flagged.
- **Actual:** Watch and Not flagged respectively.
- **PASS** — evidence: `test_context_comparison_never_creates_high`, `test_known_no_flag_case`, plus `check_signals.py` structural gate.

### 6. Narrative check for causation or policy advice
- **Expected:** no "caused/because/recommend/healthy/unhealthy/forecast" in signal explanations or the brief; the no-policy statement present verbatim.
- **Actual:** automated ban-list green (`test_explanations_use_descriptive_language`, `check_signals.py`); `outputs/brief_2025.md` reviewed by the owner (see triage below).
- **PASS (automated) + owner review (narrative)**.

### 7. Source-trace completeness
- **Expected:** every mart row carries source_file, schedule, variable code, quality status; every derived row carries its formula.
- **Actual:** 672/672 rows complete.
- **PASS** — evidence: `test_every_mart_row_has_full_source_trace`, `test_every_derived_row_shows_formula`.

### 8. Cold run of User Story 1
- **Expected:** a budget manager arriving cold sees ≤3 signals with the reason each was flagged, and can verify any number from the screen.
- **Actual:** Executive Review shows 3 signals with status, explanation, triggered tests with values, and trace stamps; "Open evidence →" lands on the metric's formula + trend + trace. Two UI defects surfaced during this run (CX-1 raw-JSON rendering; wrong status chip on truncated metrics) — both **Deliverables**, both fixed and re-verified same session. The independent critic replays this story in fresh context (findings triaged below).
- **PASS after corrections** — evidence: `outputs/run_log.md` Run 4; browser verification.

## Before → after

| Reading | Before | After revision |
|---|---|---|
| Automated tests | 19 pass / 1 fail (case 3) | **32 pass / 0 fail** |
| UI defects open | 2 (case 8) | **0** |
| Skill gates | untested | verified to block on tampered gold value (exit 1) and pass on rebuild |

## Independent critic — findings and owner triage

Critic ran 2026-07-17 in fresh context (no build history, no run log). It independently
recomputed the gold example and all three published signals from `data/raw/` — **every
number matched within tolerance** — and confirmed the language discipline held everywhere
(no causal, policy, health, or score language found). Findings below; every verdict is
the owner's.

Owner triage 2026-07-17 (all verdicts by Alejandro; fixes verified same session):

| # | Finding (short) | Home | Verdict | Resolution |
|---|---|---|---|---|
| 1 | Truncated High signal (`fte_per_1000`) has no inspectable test evidence in the drill-down, though the exec view claims it does | Deliverables | **Accept** | Engine now exports full evidence for truncated signals; drill-down renders it (verified: EH-1/EH-2/PP-1 rows visible). New test `test_truncated_signals_carry_full_evidence`. |
| 2 | Third exec slot between two exactly-tied High signals decided by dict insertion order — undocumented tie-break | Governance / Skills | **Accept** | Rules v1.1 adds documented steps 4 (largest other-test exceedance) and 5 (alphabetical); engine implements them. Police (PP-1 exceedance 1.86) outranks FTE (1.12) by rule, not by accident. New test `test_tiebreak_is_documented_rule_not_dict_order`. |
| 3 | Dashboard brief tab lists truncated metrics without statuses — a brief reader can't see a 4th High exists | Deliverables | **Accept** | Brief now shows "(High review priority)" etc. per truncated metric (verified in browser). |
| 4 | pressure_rules.md truncation wording assumes only Watch signals overflow | Governance / Living Spec | **Accept** | v1.1 rewords disclosure to cover any status; explicitly notes a High can overflow. |
| 5 | `structurally_unavailable` state promised in CLAUDE.md is unreachable dead vocabulary | Skills / Living Spec | **Accept** (implement) | Per-capita AB-city medians (uncomputable without unapproved population joins) are now explicit mart rows with that state (80 rows); dashboard displays it. New test `test_structurally_unavailable_state_is_real`. |
| 6 | `classify()` misses the "incomplete evidence" Watch branch; latent 2-nonhistorical-triggers → Not flagged gap | Skills / Governance | **Accept** | classify() now: any core trigger short of High → Watch; incomplete-evidence branch implemented. Current signal set unchanged (verified). |
| 7 | Calgary context rendered for every metric, incl. classes with no approved comparison rule | Deliverables / Governance | **Accept** (restrict) | v1.1 names the approved classes (utilization, per-capita, mill rates); engine exports the list; drill-down hides peer series elsewhere and states "comparison not approved as valid" (verified on net_financial_assets). |
| 8 | No supporting comparison on the mill-rate signal; mill-rate median computed but unused | Governance (low) | **Accept** | v1.1 extends CX-1 to mill rates at 15% relative; mill_rate_nonres now carries its labelled CX-1. New test `test_mill_rate_signal_has_supporting_comparison`. |
| 9 | Latent `explain()` NameError path; coverage note hardcoded rather than derived | Skills (minor) | **Accept** | Defaults bound; coverage note derived from the computed count + workbook footer. |

**After reading (round 1):** pipeline rebuilt under v1.1 → same three signals (parks/rec, non-res mill rate, police), now with the mill-rate CX-1 attached; **37/37 automated tests pass** (5 new regression tests covering the accepted findings); both skill gates green; all four UI fixes verified live in the browser.

## Critic re-run (after reading) — round 2 findings and owner triage

The same critic brief ran again in fresh context against the v1.1 build. **Everything fixed in
round 1 held under attack**: truncated signals fully verifiable, tie-break documented and
implemented (hand-checked ordering), truncated statuses disclosed in exec and brief, peer
context restricted to approved classes, `structurally_unavailable` real. It again recomputed
the gold example, both extra anchors, all signal arithmetic, all medians, and coverage from
raw — **every number matched**. It found no Living Spec and no Knowledge findings.

New findings and owner verdicts (all by Alejandro, 2026-07-17):

| # | Finding (short) | Home | Verdict | Resolution |
|---|---|---|---|---|
| 1 | Brief misstated Calgary comparisons as "X% below Edmonton" (wrong base) | Deliverables | **Resolved before triage** | A timing race: the critic read the v1.0-era brief while the analyst was regenerating it. The current brief states gaps exactly as the evidence file frames them ("adverse gap of X% against a 15% threshold") — verified on disk. Phrasing rule added to the analyst's standing instructions. |
| 2 | Brief cited rules v1.0 while signals ran under v1.1 | Deliverables | **Resolved before triage** | Same race; current brief cites the active rules version — verified. |
| 3 | CX-1-only Watch signals carried a self-contradictory explanation ("none of the approved tests triggered") | Skills | **Accept** | `explain()` now names the supporting comparison as the trigger; verified live on debt_utilization. New test `test_cx_only_watch_explanations_name_the_trigger`. |
| 4 | "Not flagged" verdicts had no inspectable evidence anywhere | Deliverables | **Accept** | All 22 evaluated metrics now publish full test evidence; drill-down renders the test table for not-flagged metrics (verified on rev_per_capita). New test `test_not_flagged_verdicts_carry_full_evidence` + skill-gate check. |
| 5 | AB-cities median included Edmonton itself (mill_rate_res "peer" WAS Edmonton's own value); included cities never named | Governance | **Accept — rules v1.2** | Subject excluded from its own comparator (n=19→18-19 by metric); every median row names the included municipalities. mill_rate_res median moved 7.6254 → 7.5567, matching the critic's recomputation; no signal status changed. New test `test_median_excludes_subject_and_names_cities`. |
| 6 | Rules' Watch wording lagged the implemented rule; dead branch in classify() | Governance (minor) | **Accept** | v1.2 aligns the wording ("one or more tests triggered without meeting High"); dead branch removed. |
| 7 | Latent: `reported_zero` silently dropped from signal histories (zero collapsed into missing at the signal layer) | Skills | **Accept** | `series()`/`seriesOf()` now include reported zeros; unit test `test_series_includes_reported_zero` proves zero ≠ gap. No current output affected (all focus rows are reported_value). |
| 8 | Stale hardcoded claims: coverage banner, "21 tests" chip, v1.0 docstring | Deliverables (minor) | **Accept** | Banner renders `coverage_note` from data; chip no longer hand-counts; docstrings updated. |

**After reading (round 2):** rules v1.2 approved and applied → same three signals; medians
recomputed excluding the subject; **41/41 automated tests pass** (4 new regression tests);
both skill gates green (now also enforcing not-flagged evidence); all fixes verified live
in the browser. Brief regenerated under v1.2 by the analyst subagent, pending owner
approval as the publishing gate.

## Evaluation summary — full before → after

| Reading | Baseline | After round 1 | After round 2 |
|---|---|---|---|
| Automated tests | 19 pass / 1 fail | 37 pass | **41 pass / 0 fail** |
| Critic findings open | 9 (round 1) | 8 new (round 2; 2 already resolved by regeneration race) | **0 accepted findings open** |
| Rules version | 1.0 | 1.1 | **1.2** (every change owner-approved with change control) |
| Verifiable outcomes | flagged only | flagged + truncated | **all 22 evaluated metrics, every verdict** |

**What held (critic's independent verification):** gold example exact (59.265937% / $3,265.730702);
all three signal histories match to 4 dp; Calgary comparators match; every High has ≥2 tests
incl. ≥1 historical; CX-1 supporting-only + provisional everywhere; debt_utilization correctly
Watch; coverage 306 verified against raw; missing≠zero held at the Granum edge case;
data.js consistent with curated JSON; both skill gates exit 0.

## Addendum — 2026-07-17 context-map iteration (display-only)

Owner-approved changes after a structured comparison with the group project: 5-view
dashboard (verdict board, small-multiples explorer, Alberta context map, on-screen
methodology), `PRODUCT.md`, StatCan 2021 CSD boundary source (148.8 MB, read-only in
`data/raw/`), crosswalk 2 → 19 rows (`confirmed_geo_only` scope, signed off in
`governance/crosswalk_signoff.md`).

| Reading | After round 2 | After map iteration |
|---|---|---|
| Automated tests | 41 pass / 0 fail | **51 pass / 0 fail** (10 new geo tests) |
| Rules version | 1.2 | **1.2 unchanged** — no new test, threshold, or signal |
| Verifiable outcomes | all 22 verdicts | + map per-city values **reproduce the mart medians** (guard + test) |

New evidence anchors: the geo pipeline hard-fails unless Edmonton 2025 debt utilization
reproduces the gold example (±0.01 pp) and every metric-year median over its embedded
per-city values equals the mart's published median (±1e-6, same n). The guard caught a
real rounding-order bug on first run (median-of-rounded vs round-of-median). The
requested Edmonton neighbourhood map was rejected on data-grain grounds and recorded in
the run log; the critic was **not** re-run for this display-only iteration — flagged as
open follow-up rather than claimed as verified.
