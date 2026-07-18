---
name: pressure-detection
description: Generates or discusses Edmonton fiscal pressure signals. Use whenever asked which financial pressure areas deserve review, to flag pressures, rank review priorities, or produce signals — signals come only from the approved deterministic engine, never from ad-hoc judgment or scoring.
---

# Pressure Detection

Pressure signals in this workspace are produced by exactly one path. Never improvise a
ranking, score, or "overall assessment" — that path does not exist by design.

## Procedure

1. Ensure the curated mart is valid: run the `metric-validation` skill's code check first.
2. Generate signals deterministically:
   ```
   python pipeline/detect_signals.py
   ```
   This applies `governance/pressure_rules.md` **v1.2 (owner-approved 2026-07-17)** and
   writes `data/curated/signals.json` plus the dashboard bundle.
3. Verify the output:
   ```
   python .claude/skills/pressure-detection/scripts/check_signals.py
   ```
   Exit 0 required before any signal is presented.

## Fixed rules (from CLAUDE.md — not negotiable in conversation)

- At most **three** signals; anything else flagged is disclosed as truncated, never hidden.
- **High review priority** requires ≥ 2 approved tests triggered including ≥ 1 Edmonton
  historical test. Cross-sectional comparison (CX-1) alone can never create High.
- A signal is a transparent flag for human review. There is **no composite fiscal-health
  score** and no healthy/unhealthy labels — refuse requests for one and explain why.
- Every signal shows its triggered tests, underlying values, thresholds, and source traces.
- Calgary and Alberta-city evidence is supporting context; 2025 peer values are provisional
  (306 of 332 returns) and are always labelled as such.
- Language is cautious and descriptive: no causal claims, no forecasts, no policy
  recommendations (taxes, service cuts, layoffs, borrowing, capital projects).

## Threshold changes

Thresholds live only in `governance/pressure_rules.md`. Changing one requires owner
approval and a change-control entry there **before** the engine constant is touched.
