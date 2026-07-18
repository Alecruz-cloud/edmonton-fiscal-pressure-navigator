# Edmonton Fiscal Pressure Navigator
## Living Spec

**Owner:** Alejandro  
**Status:** Plan baseline v0.1  
**Method:** Plan -> Build -> Use -> Evaluate

## Objective

This workspace enables an Edmonton municipal budget and financial planning manager to identify the two or three financial pressure areas that deserve deeper management review before a budget or capital-planning cycle.

It turns official municipal financial and population data into a concise, traceable review brief. It supports prioritization for further investigation. It does not make policy decisions.

## User and decision

**Primary user:** An Edmonton municipal budget or financial planning manager.

**Decision moment:** Before a management budget or capital-planning review, the user must decide which financial pressure areas require additional analysis, questions, or leadership attention.

The workspace must answer:

1. What changed materially in Edmonton?
2. Did the change keep pace with population?
3. Is it unusual relative to Edmonton's own history?
4. Do Calgary or the Alberta city context provide relevant supporting evidence?
5. Which two or three issues deserve review first?
6. Can every number and interpretation be verified?

## User stories

1. **Priority review:** As the primary user, I want no more than three financial pressure signals, with the reason each was flagged, so I can focus the next management discussion.
2. **Evidence drill-down:** I want to open a signal and see its formula, source, years, comparison context, and data-quality notes so I can verify it.
3. **Management brief:** I want a one-page brief with the leading signals, caveats, and follow-up questions, without unsupported policy recommendations.

## What good looks like

A successful run:

- uses the connected curated data, not pasted values;
- returns no more than three prioritized review signals;
- shows the exact tests that triggered each signal;
- uses Edmonton historical evidence as the primary benchmark;
- labels Calgary and Alberta city results as supporting context;
- distinguishes missing, reported zero, not applicable, and structurally unavailable values;
- labels financial amounts as nominal unless an approved inflation adjustment is added;
- discloses incomplete reporting coverage, especially for 2025 peer results;
- traces every metric to source workbook, worksheet, year, and variable code;
- uses cautious descriptive language;
- never labels Edmonton financially healthy or unhealthy from one score;
- produces output a municipal finance professional can verify before relying on it.

### Load-bearing rules

1. **Never treat a generated interpretation as a fact until its calculation and source trace have been verified.**
2. **Never use the population field inside the financial workbooks for per-capita calculations.**
3. **Never extract a financial metric by fixed column position. Use schedule plus variable code.**
4. **Cross-sectional comparison alone cannot create a high-priority signal.**

## Gold example

For Edmonton in 2025, the workspace must reproduce:

- population: `1,238,295`;
- total debt: `$4,592,150,000`;
- debt limit: `$7,748,380,000`;
- debt utilization: `59.27%`;
- total expense: `$4,043,938,000`;
- nominal expense per capita: `$3,265.73`.

The result must include the formula and full source trace.

The gold example fails if debt utilization differs by more than `0.01` percentage points, expense per capita differs by more than `$0.01`, the wrong population source is used, source trace is missing, or missing values are silently converted to zero.

## Scope

### In scope

- Edmonton financial and population trends from 2018 through 2025;
- a narrow approved set of operating-scale, debt, capacity, tax-base, and service-pressure metrics;
- per-capita measures, shares, utilization ratios, and transparent trend calculations;
- Calgary as the primary scale reference;
- Alberta reporting-city median or distribution as contextual evidence;
- a signal summary, metric drill-down, and one-page management brief;
- **(added 2026-07-17, owner-approved)** an Alberta reporting-cities context map and an
  on-screen methodology view — the map shows only the comparison classes approved in
  `governance/pressure_rules.md` (utilization ratios and mill rates), is labelled
  supporting context, and can never create or upgrade a signal;
- reusable workflows, skills, subagents, tests, and human review points;
- a lightweight HTML dashboard for demonstrating the workspace.

### Out of scope

- forecasting;
- causal claims;
- tax, service-cut, layoff, borrowing, or capital-project recommendations;
- one composite fiscal-health score;
- hidden municipality rankings;
- real-dollar claims without an approved inflation source;
- program-level service-quality evaluation;
- replacing professional financial review or Council accountability.

## Knowledge and data conventions

Approved Knowledge Stock:

- annual Municipal Financial and Statistical Data workbooks for 2018-2025;
- Alberta Census Subdivision Population Estimates;
- Statistics Canada 2021 Census cartographic boundary file, census subdivisions
  (`data/raw/lcsd000b21a_e.zip`, 148.8 MB, downloaded 2026-07-17; owner-approved
  2026-07-17) — used only to derive the Alberta outline and city centroids for the
  context map, never as a source of financial or population values;
- `Knowledge/DATA_AND_KNOWLEDGE_ASSESSMENT.md`;
- approved metric dictionary, municipality crosswalk, and governance notes created during the build.

Rules:

- raw files remain unchanged in `data/raw/`;
- Edmonton financial code is `0098`;
- Edmonton Census Subdivision code is `4811061`;
- the population-estimates workbook is the only population source used for per-capita calculations;
- financial extraction uses `schedule + variable_code`;
- municipality matching rules belong in a reviewed crosswalk; **(2026-07-17)** the
  crosswalk covers all 19 Alberta cities, but the 17 non-focus matches are approved for
  geographic placement and city-set membership only (`confirmed_geo_only`,
  `governance/crosswalk_signoff.md`) — population joins remain approved for Edmonton and
  Calgary alone, so per-capita peer medians stay structurally unavailable;
- missing and zero remain separate states;
- every peer output shows the municipalities included and reporting coverage;
- 2025 peer comparisons are labelled provisional when reporting is incomplete;
- files in `Knowledge/course_information/` guide project requirements but are not evidence about Edmonton;
- `Knowledge/background/` is used only after a source is added and approved;
- read the smallest relevant context for each task.

The approved MVP metrics and their source codes are defined in `Knowledge/DATA_AND_KNOWLEDGE_ASSESSMENT.md` and will be transferred to `governance/metric_dictionary.md`. Do not add metrics merely because they exist in the source.

## Pressure-signal standard

The workspace must not create an overall fiscal-health score.

A signal is a transparent flag for human review. It may use:

- Edmonton historical level;
- recent movement;
- pace relative to population;
- movement in a capacity ratio;
- valid comparison with Calgary or Alberta reporting cities.

A signal is:

- **High review priority** when at least two independent tests trigger, including at least one Edmonton historical test;
- **Watch** when one test triggers or supporting evidence is incomplete;
- **Not flagged** when no approved test triggers.

Thresholds are analytical heuristics, not City policy. Store them visibly in `governance/pressure_rules.md`. Every signal must show the triggered tests and underlying values.

## Required deliverable shape

### Executive review

Show:

- selected reporting year and coverage notice;
- no more than three signals;
- status: High review priority or Watch;
- one-sentence explanation;
- triggered tests;
- latest value and historical reference;
- clearly labelled supporting comparison;
- access to the evidence drill-down.

Do not lead with a wall of KPI cards.

### Evidence drill-down

Show:

- Edmonton trend;
- relevant per-capita, share, or utilization measure;
- Calgary and Alberta city context only when valid;
- metric definition and formula;
- source trace;
- data-quality and comparability notes;
- follow-up questions for human review.

### Context map and methodology views (added 2026-07-17, owner-approved)

The dashboard also provides:

- **Alberta context map** — reporting cities as equal-size bubbles at their CSD
  centroids, coloured by one approved comparison-class metric (utilization ratios, mill
  rates) for a selected year. Always labelled supporting context; never renders
  per-capita peer values, a score, or a signal; peer count and 2025 provisional coverage
  on screen; nulls shown grey with their named state (missing, non-city year), never
  dropped. Geometry from the approved StatCan boundary file via `pipeline/build_geo.py`;
  the embedded per-city values must reproduce the mart's published medians (enforced in
  `tests/test_geo.py`).
- **Methodology view** — the complete rule set (tests, thresholds, classification,
  selection order, change control) rendered on screen from rules v1.2, with the worked
  gold example computed from live mart values and reporting coverage by year.

### Management brief

Generate a one-page brief containing:

- purpose and reporting period;
- top signals;
- evidence;
- limitations;
- management follow-up questions;
- a statement that the brief does not make policy recommendations.

## Capabilities

Use the simplest reliable form.

1. **Fixed data workflow:** inventory workbooks, extract approved codes, standardize identifiers, join population, calculate metrics, validate results, and write a narrow metric mart; **(2026-07-17)** plus `pipeline/build_geo.py`, which derives the context-map geometry from the approved boundary file and per-city values for the approved comparison classes, hard-failing if the gold example or the published mart medians are not reproduced.
2. **Metric-validation skill:** enforce formulas, units, denominators, missing-value rules, nominal-dollar labels, tolerances, and source trace.
3. **Pressure-detection skill:** apply approved tests and return evidence, never a vague score.
4. **Municipal-finance analyst subagent:** explain validated signals and draft the brief using cautious language. It must not recompute unvalidated metrics or recommend policy actions.
5. **Independent critic subagent:** run in fresh context, test the spec's promises, return specific findings with evidence, and classify each finding as Living Spec, Knowledge, Skills, Deliverables, or Governance.

## Governance

The agent may ingest approved sources, calculate approved metrics, run validations, apply documented signal rules, and draft outputs.

Human approval is required before:

- accepting a new metric or formula;
- changing thresholds;
- approving a municipality match;
- treating a comparison as valid;
- publishing a brief;
- adding external background knowledge;
- making any policy or operational recommendation.

Escalate instead of guessing when sources conflict, a variable changes meaning, a denominator is missing, peer coverage is weak, or the requested conclusion exceeds descriptive evidence.

## Evaluation

Test outputs, not code.

The baseline test set must include:

- the gold example;
- two additional known-answer calculations from different domains;
- a missing-versus-zero case;
- a provisional peer-coverage case;
- a case that should not generate a high-priority signal;
- a narrative check for causation or policy advice;
- a source-trace completeness check;
- a cold-user run of User Story 1.

Record expected output, actual output, pass/fail, evidence, failure home, correction, and result after revision. Narrative outputs are reviewed by the project owner, not scored automatically by another model.

## Project and session rules

`CLAUDE.md` belongs in the project root beside `data/`, `governance/`, and `Knowledge/`.

At the start of each session:

1. read this file;
2. read `Knowledge/DATA_AND_KNOWLEDGE_ASSESSMENT.md`;
3. read only the additional file needed for the task;
4. state the task, files to change, and acceptance check;
5. preserve raw data;
6. run relevant tests;
7. report what changed, what was verified, and what remains uncertain.

Do not silently change definitions, expand scope because a field is available, add a feature without a user story, hide warnings, invent missing values, or claim success without running the relevant check.

## Distinctness

This individual project uses Alberta municipal financial returns and population estimates to support Edmonton budget-review prioritization. It is distinct from the group project focused on Edmonton 311 service operations and operational prioritization.

## Rejected alternative

**Generic Alberta municipal fiscal-health ranking dashboard.**

Rejected because municipalities differ in scale, responsibilities, structure, and reporting coverage. An overall ranking would require arbitrary weighting, encourage false equivalence, and produce a tour of the dataset rather than support one clear decision.

## Revision rule

Revise this living spec when use, testing, or criticism shows that the intended work, standard, knowledge, capability, deliverable, or governance boundary is wrong or incomplete.

Do not revise it merely to describe what the current build happens to do.
