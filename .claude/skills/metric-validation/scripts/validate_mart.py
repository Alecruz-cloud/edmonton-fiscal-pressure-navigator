"""Metric-validation code check. Exit 0 = curated mart is safe to use; non-zero = blocked.

Validates data/curated/metric_mart.json against the load-bearing rules in
governance/metric_dictionary.md and the owner-approved known-answer anchors.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MART = ROOT / "data" / "curated" / "metric_mart.json"

ANCHORS = [  # (year, mcode, metric_id, expected, tolerance)
    (2025, "0098", "pop", 1238295, 0),
    (2025, "0098", "debt_total", 4592150000, 0),
    (2025, "0098", "debt_limit", 7748380000, 0),
    (2025, "0098", "debt_utilization", 59.2659, 0.01),
    (2025, "0098", "exp_total", 4043938000, 0),
    (2025, "0098", "exp_per_capita", 3265.7307, 0.01),
    (2022, "0098", "debt_utilization", 64.11, 0.01),
    (2025, "0098", "fte_per_1000", 9.6237, 0.001),
    # CPI display context (owner-approved 2026-07-18): base-year identity + one deflation
    (2025, "0098", "exp_per_capita_real2025", 3265.7307, 0.01),
    (2018, "0098", "exp_per_capita_real2025", 3699.4255, 0.01),
]
VALID_QUALITY = {"reported_value", "reported_zero", "missing", "not_applicable",
                 "structurally_unavailable"}

def fail(msg):
    print(f"FAIL  {msg}")
    fail.count += 1
fail.count = 0

def main():
    if not MART.exists():
        print("FAIL  metric_mart.json not found — run pipeline/build_mart.py first")
        return 2
    with open(MART, encoding="utf-8") as f:
        mart = json.load(f)
    rec = mart["records"]
    ix = {(r["year"], r["municipality_code"], r["metric_id"]): r for r in rec}

    # 1. known-answer anchors
    for year, mcode, mid, exp, tol in ANCHORS:
        r = ix.get((year, mcode, mid))
        if r is None or r["value"] is None:
            fail(f"anchor missing: {year}/{mcode}/{mid}")
        elif abs(r["value"] - exp) > (tol or 0.0000001):
            fail(f"anchor {mid} {year}: got {r['value']}, expected {exp} (tol {tol})")

    # 2. stale-population guard
    for year, expected in ((2023, 1127183), (2024, 1197770), (2025, 1238295)):
        r = ix.get((year, "0098", "pop"))
        if not r or r["value"] != expected or r["value"] == 1010899:
            fail(f"population {year} must be {expected} from the estimates workbook")
        elif not str(r["source_file"]).startswith("population-estimates"):
            fail(f"population {year} sourced from {r['source_file']}")

    # 3. trace completeness, quality states, nominal labels, formulas
    for r in rec:
        key = f"{r['year']}/{r['municipality_code']}/{r['metric_id']}"
        for fld in ("source_file", "source_schedule", "source_variable_code",
                    "quality_status", "unit", "metric_name"):
            if not r.get(fld):
                fail(f"{key}: missing {fld}")
        if r["quality_status"] not in VALID_QUALITY:
            fail(f"{key}: invalid quality_status {r['quality_status']}")
        if r["quality_status"] in ("missing", "not_applicable", "structurally_unavailable") \
                and r["value"] is not None:
            fail(f"{key}: {r['quality_status']} row carries a value (missing must never become a number)")
        if r["unit"].startswith("$") and "nominal" not in r["unit"]:
            if "constant 2025" in r["unit"]:
                # owner-approved 2026-07-18: Edmonton-only CPI display context
                if not r["metric_id"].endswith("_real2025") or r["municipality_code"] != "0098":
                    fail(f"{key}: constant-2025 unit outside the approved Edmonton *_real2025 scope")
                elif r["comparability_status"] != "display_only_context":
                    fail(f"{key}: constant-2025 row must be display_only_context")
                elif r["value"] is not None and "18-10-0005" not in r["data_quality_note"]:
                    fail(f"{key}: constant-2025 row missing its StatCan 18-10-0005-01 CPI trace")
            else:
                fail(f"{key}: dollar unit not labelled nominal or approved constant 2025")
        if r["source_schedule"] == "derived" and r["municipality_code"] in ("0098", "0046") \
                and not r.get("formula"):
            fail(f"{key}: derived metric without formula")

    # 4. constant-2025$ context — every real value must equal its published nominal
    #    sibling × CPI factor; the base year must reproduce nominal exactly.
    cpi_raw = (mart.get("meta", {}).get("cpi_context") or {}).get("values") or {}
    cpi = {int(k): v for k, v in cpi_raw.items()}
    reals = [r for r in rec if r["metric_id"].endswith("_real2025")]
    if not cpi:
        fail("meta.cpi_context.values missing — CPI provenance must ship with the mart")
    elif not reals:
        fail("no *_real2025 rows found — approved CPI display context missing")
    else:
        for r in reals:
            key = f"{r['year']}/{r['municipality_code']}/{r['metric_id']}"
            if r["value"] is None:
                continue
            nom = ix.get((r["year"], "0098", r["metric_id"][:-len("_real2025")]))
            if nom is None or nom["value"] is None:
                fail(f"{key}: real value without a published nominal sibling")
            elif abs(r["value"] - nom["value"] * cpi[2025] / cpi[r["year"]]) > 0.0001:
                fail(f"{key}: real value drifts from published nominal × CPI factor")
            elif r["year"] == 2025 and r["value"] != nom["value"]:
                fail(f"{key}: base-year real must equal nominal exactly")

    if fail.count:
        print(f"\n{fail.count} check(s) failed — the mart must not be used until fixed.")
        return 1
    print(f"OK  {len(rec)} mart rows pass all metric-validation checks "
          f"({len(ANCHORS)} known-answer anchors reproduced).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
