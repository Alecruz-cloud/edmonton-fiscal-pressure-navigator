---
name: metric-validation
description: Enforces the Edmonton Fiscal Pressure Navigator metric rules whenever a financial metric is computed, validated, quoted, or reported — formulas, units, denominators, missing-value handling, nominal-dollar labels, tolerances, and full source traces. Use before relying on or presenting any metric value.
---

# Metric Validation

You are working inside the Edmonton Fiscal Pressure Navigator. Any metric you compute,
quote, or present must satisfy every rule below. These rules are load-bearing; a violation
means the number must not be used.

## Rules

1. **Approved metrics only.** A metric must appear in `governance/metric_dictionary.md`
   with its formula, schedule, variable code, and unit. Do not invent or extend metrics
   because a field exists in the source.
2. **Extraction is schedule + variable code.** Values come from the worksheet named in the
   dictionary, located by the variable code in row 3 — never by fixed column position.
   Municipality `CODE` is text with leading zeros (`0098` Edmonton, `0046` Calgary).
3. **Population rule.** Every per-capita denominator comes from the population-estimates
   workbook (`CSD 4811061` Edmonton, `4806016` Calgary). The population field inside the
   financial workbooks is stale (repeats 1,010,899 for 2023–2025) and is never used.
4. **Missing is never zero.** Blank source cells are `missing`; explicit zeros are
   `reported_zero`. Never substitute, average over, or silently drop either state.
   Derived metrics with a missing input are `not_applicable`, not 0.
5. **Nominal labels.** Every dollar amount is labelled nominal. Never describe nominal
   growth as real growth, cost efficiency, or affordability change.
6. **Source trace.** Every value you present carries workbook › schedule › variable code ›
   year (or `derived › formula` with traced inputs). A number without its trace is not
   reportable.
7. **Tolerances.** Known-answer anchors (dictionary §Known-answer anchors) must reproduce
   within ±0.01 pp for ratios and ±$0.01 for per-capita dollars.

## Code check (run it — do not reason that the mart "should" be fine)

```
python .claude/skills/metric-validation/scripts/validate_mart.py
```

Exit code 0 means the curated mart passes all checks above. A non-zero exit blocks any
use of the mart until the pipeline is fixed and re-run. If the mart is stale or absent,
rebuild with `python pipeline/build_mart.py` first.

## Escalate instead of guessing

Stop and ask the owner when: a variable code is absent for a year, a denominator is
missing, two sources conflict, a new metric or formula is requested, or a requested
conclusion exceeds descriptive evidence.
