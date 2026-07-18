# Use Log — Edmonton Fiscal Pressure Navigator

Structured record of real runs: what was run, what the output showed, what fell short,
what was corrected. (Course requirement: log of use, kept short and honest.)

## 2026-07-17 · Session 1 (PLAN audit → BUILD)

### Run 1 — Read-only data audit (pre-build)
- **Ran:** read-only inspection scripts over all 9 raw workbooks.
- **Good:** every project assumption confirmed (codes 0098/4811061 present all years; schedule+variable-code extraction viable; gold values reproduced by hand; returns per year 342→306 match the assessment).
- **Fell short:** my blank-cell count for 2025 `AA(1)-Debt` (4 blanks) was wrong — the blanks sit on a footer row (`"306 out of 332"`), not on municipality returns. **Correction:** the known-answer test was rewritten against the verified truth before it ever gated the pipeline. **Lesson:** even audit notes are claims until tested.
- **Surprise:** the "306 of 332" coverage figure is printed inside the workbook itself — the coverage notice now cites the workbook, not just the assessment memo.

### Run 2 — Extraction pipeline (`pipeline/build_mart.py`)
- **Ran:** full raw → curated build.
- **Good:** first run produced 53,018 long-form rows, 672 mart rows; gold example reproduced (59.265937% utilization; $3,265.7307 per capita); stale-population guard effective (2023–2025 populations come from the estimates workbook, never 1,010,899).
- **Surprise:** exactly one genuine `missing` value exists across all approved codes and years — Granum (0135), 2021 equalized assessment. It became the missing-vs-zero test anchor.

### Run 3 — Signal engine (`pipeline/detect_signals.py`, rules v1.0)
- **Ran:** signal detection after owner approved `governance/pressure_rules.md` v1.0.
- **Good:** 22 metrics evaluated, 13 flagged, top 3 shown, truncation disclosed. Hand-verified every triggered-test value in the three shown signals against raw workbook numbers.
- **Notable behavior (working as designed):** a 4th High signal (`fte_per_1000`) fell to the truncation notice; `debt_utilization` stayed Watch because its only trigger is cross-sectional (Calgary 36.34% / AB median 31.81% vs Edmonton 59.27%) and context alone cannot create High.

### Run 4 — Dashboard used as the budget manager (User Story 1)
- **Ran:** opened `dashboard/index.html` (served over localhost; the in-app pane renders `file://` as static snapshots), walked all three views, followed "Open evidence →", hovered chart points.
- **Good:** ≤3 signals with reasons visible without scrolling past a KPI wall; gold panel with six certified values and trace stamps; the story-1 question ("can I verify every number?") answerable from the drill-down alone.
- **Fell short — two defects found by use, not by tests:**
  1. CX-1 comparison values rendered as raw JSON in the tests table. *Home: Deliverables.* Fixed (formatted prose), verified by reload.
  2. Drill-down status chip showed "Not flagged" for truncated metrics (e.g. debt_utilization is actually Watch). *Home: Deliverables.* Fixed (chip now uses shown-or-truncated status plus a "not among top 3" note), verified on debt_utilization (Watch), fte_per_1000 (High), rev_per_capita (Not flagged).
- **Lesson:** every computed value was correct; both defects lived in the product around the numbers — exactly the failure mode the value-by-value checks cannot see.

### Run 5 — Skill gate behavior checks
- **Ran:** both skill code checks on good input (both OK), then tampered the mart's gold utilization to 42.0 and re-ran.
- **Good:** `validate_mart.py` exited 1 and named the broken anchor; after rebuilding, both checks and all 32 pytest tests green again. The gate blocks; it does not advise.

### Run 6 — Subagents (analyst brief draft + independent critic)
- **Ran:** municipal-finance-analyst (draft `outputs/brief_2025.md`) and independent-critic (fresh context, adversarial).
- **Good:** the analyst's brief stayed inside every boundary (traces, nominal labels, truncation disclosure, no policy language). The critic independently recomputed the gold example and all three signals from raw — every number matched — and returned 9 specific findings.
- **Fell short:** the critic exposed a real verifiability hole (truncated High signal had no inspectable evidence), an undocumented ranking tie-break, and a spec promise (`structurally_unavailable`) no code could produce. Owner triaged all 9: accepted. Homes: 4 Deliverables, 3 Governance, 2 Skills — notably, several fixes were governance-text fixes (rules v1.1), not code.

### Run 7 — Fold-back and after reading (rules v1.1)
- **Ran:** rules amendment v1.1 (owner-approved tie-break, truncation wording, mill-rate CX-1, approved context classes), engine + dashboard fixes, full rebuild, 5 new regression tests.
- **Good:** same three signals under v1.1 (ranking now rule-determined); 37/37 tests pass; both skill gates green; all four UI fixes verified live (fte evidence visible, brief statuses disclosed, peer context restricted, structurally-unavailable state real). Critic re-run in fresh context for the before/after comparison — results in `outputs/evaluation.md`.

### Run 8 — Critic round 2 and second fold-back (rules v1.2)
- **Ran:** same critic brief, fresh context, against the v1.1 build; owner triaged 8 new findings; rules v1.2 approved; engine/dashboard fixes; full rebuild; 4 new regression tests.
- **Good:** every round-1 fix held under adversarial re-verification; all recomputations matched again; the sharpest new find — the AB-cities median included Edmonton itself, so one "peer" comparator WAS Edmonton's own mill rate — became rules v1.2 (subject excluded, included cities named). 41/41 tests; both gates green; fixes verified live.
- **Fell short / lesson:** two critic findings were an artifact of concurrent agents (it read the brief mid-regeneration) — recorded as resolved-before-triage rather than claimed as fixes. Sequencing note: run the analyst *before* the critic next cycle.
- **Surprise:** the CX-only Watch explanations were self-contradictory ("none of the approved tests triggered… this flags the area") — generated text can fail exactly like UI: correct numbers, wrong product around them.

## 2026-07-17 · Session 2 (group-project comparison → owner-approved map + dashboard iteration)

### Run 9 — Comparative evaluation against the group's 311 dashboard
- **Ran:** structured exploration of both repos (group: React/Plotly/MapLibre app, DuckDB prep, sign-off gates, standing critic brief; this project: vanilla dashboard, pytest suite, blocking skill gates).
- **Good:** the comparison sorted cleanly into "adopt" (on-screen methodology, product brief, decision-record habits, map technique) and "already stronger here" (automated known-answer tests, blocking code gates, missing-vs-zero states, doc coherence — the group's design doc had drifted from its build).
- **Governance held under temptation:** the requested "Edmonton city map like the group's" was **rejected on data grounds** — this project's grain is municipal, so 407 neighbourhood polygons would all display one number. The owner-approved adaptation: a province-level context map of the 19 reporting cities, display-only, CX classes only.

### Run 10 — Geo pipeline (`pipeline/build_geo.py`) and crosswalk extension
- **Ran:** owner-approved StatCan 2021 CSD cartographic boundary download (148.8 MB → `data/raw/`, read-only); crosswalk extended 2 → 19 rows (17 `confirmed_geo_only`, sign-off in `governance/crosswalk_signoff.md`); geo build with hard guards.
- **Good:** 19/19 cities matched (Lloydminster via its Alberta part, flagged; Beaumont's 2018 town status a named state); gold reproduced from the geo path (59.265937%); **the median-consistency guard caught a real bug on first run** — medians computed over rounded per-city values differed from the mart at the 6th decimal; fixed to mirror the mart's order of operations (median first, round once).
- **Fell short:** the boundary zip is 148.8 MB, above the "tens of MB" estimate given at approval — disclosed rather than swapped for a lesser source.

### Run 11 — Dashboard restructure (3 → 5 views) and re-verification
- **Ran:** Executive Review + verdict board (all 22 verdicts, evidence links), Evidence Explorer (small-multiples grid), Alberta Context Map (SVG, no library), Methodology (rules v1.2 on screen, worked gold example from live values, coverage bars, change control), Brief (unchanged). Full pipeline rebuild; browser walk of all five views and every cross-link (board → drill, card → drill, drill → map).
- **Good:** 51/51 tests (10 new geo tests); console clean; signals still lead (no KPI wall); map states verified live (Beaumont 2018 grey with reason; mill_rate_nonres 2025 shows Edmonton 24.22 vs n=18 median 13.42, matching S2's CX-1 evidence); submission regenerated with five view screenshots and the honest disclosure that the practice import came from the group project.
- **Lesson:** a stale-cache reload nearly let an outdated `data_quality_note` masquerade as current — cache-busted and re-verified against disk before trusting the pane.

### Run 12 — Real base map for the context view (Leaflet + Carto Positron)
- **Ran:** owner-approved (2026-07-18) conversion of the Alberta context map from hand-projected SVG to Leaflet 1.9.4 (vendored at `dashboard/vendor/leaflet/`) over Carto Positron tiles — presentation only, attribution on screen, zoom capped at province↔region scale, StatCan outline kept as the offline fallback. Bubbles, ramp, legend, provisional chip, side panel, and the mart-median verification stamp unchanged.
- **Good:** live browser walk clean (deep-link activates the map tab, 9/9 tiles loaded, 19 bubbles, Edmonton/Calgary labels, zoom fits Alberta); 51/51 tests still green (display-only change, no pipeline or rule touched); the submission's three "no chart library / hand-projected SVG" claims were re-worded the moment they stopped being true, the map figure was re-captured, and the live GitHub Pages link was added so the evaluator can verify interactively.
- **Bug caught live:** Leaflet's animated `fitBounds` silently kept zoom at max when the map initialized inside a hidden tab — the animation swallowed the refit. Fixed with `animate:false` on both fits plus an `invalidateSize` hook on tab activation.
- **Also this session:** repository published to `github.com/Alecruz-cloud/edmonton-fiscal-pressure-navigator` (50 files; the 148.8 MB boundary zip gitignored with its provenance and download URL documented) and the dashboard deployed via GitHub Pages with a root redirect.
