# Pressure Rules

> **STATUS: APPROVED v1.2 — owner approval 2026-07-17 (second amendment after independent-critic re-run findings 5, 6).**
> Thresholds below are analytical heuristics for review prioritization. They are **not City policy** and
> do not define financial health. Any change requires a new owner approval and a change-control entry.

## Principles (fixed by CLAUDE.md — not editable here)

1. A signal is a transparent flag for human review, never a score.
2. **High review priority** requires at least **two independent tests** triggered, including at least **one Edmonton historical test** (EH-1 or EH-2).
3. Cross-sectional comparison alone (CX-1) can **never** create a high-priority signal.
4. At most **three** signals are surfaced per run.
5. Every signal must display its triggered tests, the underlying values, the thresholds applied, and full source traces.

## Adverse direction per metric

A test triggers only on movement in the metric's *adverse* direction (the direction that indicates possible pressure):

| Metric class | Adverse direction | Rationale |
|---|---|---|
| `debt_utilization`, `debt_service_utilization` | up | less regulated headroom |
| `exp_per_capita`, `svc_per_capita_*` | up | nominal cost pressure per resident |
| `svc_share_*` | up | function crowding out other spending |
| `net_financial_assets` | down | weakening financial position |
| `accumulated_surplus` | down | weakening cushion |
| `assessment_per_capita` | down | tax base not keeping pace |
| `mill_rate_res`, `mill_rate_nonres` | up | rising rate burden |
| `fte_per_1000` | down | service capacity thinning vs population |
| `rev_per_capita` | down | revenue not keeping pace |

## Approved tests

Window: the full 2018–2025 Edmonton history. "3-year change" = latest year vs three reporting years earlier (2025 vs 2022).

### EH-1 · Edmonton historical level *(historical test)*
Triggers when the latest value is the **most adverse in the 8-year history** (new maximum for up-adverse metrics; new minimum for down-adverse metrics).

### EH-2 · Edmonton recent movement *(historical test)*
Triggers when the adverse-direction change over the last 3 years meets the class threshold:

| Metric class | Threshold (3-year adverse change) |
|---|---|
| Utilization ratios | ≥ 3.0 pp |
| Shares | ≥ 2.0 pp |
| Per-capita nominal dollars | ≥ 10.0% |
| Mill rates | ≥ 10.0% |
| FTE per 1,000 | ≥ 0.50 |
| Balance-sheet dollars (`net_financial_assets`, `accumulated_surplus`) | adverse change ≥ 15.0% of the 8-year median absolute level |

### PP-1 · Pace relative to population
For metrics with a nominal-dollar or count numerator: triggers when the numerator's 3-year growth exceeds population growth over the same period by **≥ 5.0 pp** (up-adverse), or trails it by ≥ 5.0 pp (down-adverse).

### CR-1 · Capacity-ratio movement
For utilization ratios only: triggers when the latest value sits **≥ 5.0 pp above the 8-year minimum** *and* above the 8-year median.

### CX-1 · Supporting comparison *(context only — can never create High)*
Edmonton's latest value differs from the comparator in the adverse direction by ≥ 10.0 pp (utilization) or ≥ 15% relative (per-capita and mill rates, v1.1) versus **Calgary**, or versus the **Alberta reporting-city median**. Any 2025 comparison is labelled *provisional (306 of 332 returns)* and the included-municipality count is displayed. Invalid or unapproved comparisons are excluded, not silently substituted.

**Approved comparison classes (v1.1):** utilization ratios, per-capita measures, and mill rates. No cross-sectional display or test is approved for raw nominal balance-sheet or expense dollars, counts, or shares; deliverables state "comparison not approved as valid" for those classes rather than rendering peer values.

**Comparator composition (v1.2):** the subject municipality (Edmonton) is **excluded** from its own Alberta reporting-city median — a municipality is never compared against a benchmark containing itself. Every peer output names the municipalities included, not just their count.

## Classification

| Status | Rule |
|---|---|
| **High review priority** | ≥ 2 of {EH-1, EH-2, PP-1, CR-1} triggered, including ≥ 1 of {EH-1, EH-2} |
| **Watch** | *(v1.2 wording, matching the implemented rule)* one or more approved tests triggered without meeting the High criteria — including the case where only CX-1 triggered. Incomplete supporting evidence is recorded on the signal's tests. |
| **Not flagged** | no approved test triggered — and the full test evidence for the verdict is still published, like any other outcome |

## Selection when more than three signals qualify

Rank by: (1) High before Watch; (2) number of triggered core tests; (3) magnitude of the EH-2 exceedance relative to its threshold; (4) *(v1.1)* largest exceedance relative to threshold on any other triggered quantitative test (PP-1, CR-1); (5) *(v1.1)* alphabetical `metric_id` as the final deterministic step.

Truncation is disclosed with each overflowed signal's **status** ("N additional flagged signals not shown", naming every metric and its High/Watch status — a High signal can overflow, and the disclosure must make that visible). Full test evidence for truncated signals remains available in the drill-down.

## Change control

Any threshold change requires owner approval and a dated entry below.

| Date | Version | Change | Approved by |
|---|---|---|---|
| 2026-07-17 | 0.1-draft | Initial draft for owner review | — |
| 2026-07-17 | 1.0 | Draft approved without changes; signal generation unblocked | Alejandro (project owner) |
| 2026-07-17 | 1.1 | Critic fold-back: documented tie-break steps 4–5; truncation disclosure covers any status; CX-1 extended to mill rates (15% relative); approved comparison classes made explicit | Alejandro (project owner) |
| 2026-07-17 | 1.2 | Critic re-run fold-back: subject excluded from its own comparator median; included municipalities named in peer outputs; Watch wording aligned with the implemented classification; Not-flagged verdicts publish full test evidence | Alejandro (project owner) |
