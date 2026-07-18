# Municipality Crosswalk Extension — Sign-off

**Date:** 2026-07-17 · **Status:** APPROVED (owner decision in session, 2026-07-17) ·
**Trigger:** owner request to add an Alberta context map to the dashboard, adapting the
group project's spatial technique to this project's municipality-level grain.

## What was matched

The financial workbooks contain **19 municipalities with status `City`** across 2018–2025.
The population-estimates workbook contains **exactly 19 rows of census type `CY`**.
Matching used normalized names (uppercase, strip footnote digits/asterisks/periods) plus
the municipal-type filter, per `Knowledge/DATA_AND_KNOWLEDGE_ASSESSMENT.md` §6.2 — never
raw name alone.

| Result | Count | Cities |
|---|---|---|
| Exact normalized match, type CY | 17 | Airdrie, Beaumont, Brooks, Camrose, Chestermere, Cold Lake, Fort Saskatchewan, Grande Prairie, Lacombe, Leduc, Lethbridge, Medicine Hat, Red Deer, Spruce Grove, St. Albert, Wetaskiwin (+ Calgary already confirmed) |
| Already confirmed (pre-existing) | 2 | Edmonton (0098 ↔ 4811061), Calgary (0046 ↔ 4806016) |
| Manual special case | 1 | Lloydminster (0206 ↔ 4810039 "Lloydminster (Part)") |
| Unmatched leftovers | 0 financial · 0 population | one-to-one after the special case |

## Special cases (flagged, not silently resolved)

1. **Lloydminster** — the city spans Alberta/Saskatchewan. The population CSD row covers
   the **Alberta part only**; the financial return covers the whole city. Matched for
   **geographic placement only**. Ratio metrics shown on the map (mill rates, debt
   utilizations) require no population denominator, so the mismatch cannot contaminate any
   displayed value. Any future population use for Lloydminster requires separate review.
2. **Beaumont** — reports as **Town in 2018**, City from 2019. It is therefore absent from
   the 2018 city set; the map shows it as "not in the city set" for 2018 rather than
   treating the gap as missing data.
3. **Cold Lake** — the assessment flagged name ambiguity with reserves; the `CY` type
   filter resolves it (the IRI rows were never candidates).

## Scope of this approval — what did NOT change

- The 17 new matches are approved **only** for geographic placement and city-set
  membership on the Alberta context map (`match_status = confirmed_geo_only`).
- **No new population joins are approved.** Per-capita peer medians remain
  `structurally_unavailable` in the metric mart; computing them would require a separate
  owner approval and new tests.
- The comparator definition in `governance/pressure_rules.md` v1.2 (median across
  reporting cities excl. Edmonton, financial-workbook-only classes) is unchanged.
- Signal generation is unchanged — the map is supporting context and can never create or
  upgrade a signal.

## Verification

- `pipeline/build_geo.py` fails hard if any 2025 reporting city lacks a crosswalk row or
  a boundary-file geometry (no silent drops).
- `tests/test_geo.py` pins Edmonton's centroid to its known location, requires all 19
  cities to carry coordinates, and cross-checks the map's Edmonton 2025 debt-utilization
  value against the gold example (59.27%, tolerance 0.01 pp).

**Approved by:** Alejandro (project owner) — decision recorded from the 2026-07-17 session
(map option "Alberta bubble map" selected, including StatCan source download and this
crosswalk extension with sign-off).
