"""Edmonton Fiscal Pressure Navigator — pressure-signal detection (fixed pipeline).

Applies governance/pressure_rules.md v1.0 (owner-approved 2026-07-17) to the curated
metric mart and writes:

    data/curated/signals.json    <=3 ranked signals + full test evidence + not-flagged list
    dashboard/data.js            mart + signals embedded for the file:// dashboard

Every constant below mirrors the approved rules document. Do not change a threshold
here without a new owner approval and a change-control entry there.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURATED = ROOT / "data" / "curated"
DASHBOARD = ROOT / "dashboard"

RULES_VERSION = "1.2 (approved 2026-07-17)"
LATEST = 2025
WINDOW = list(range(2018, 2026))
LOOKBACK = 3  # "3-year change" = latest vs latest-3

# metric_id -> (adverse direction, metric class, numerator metric for PP-1 or None)
ELIGIBLE = {
    "debt_utilization":        ("up",   "utilization", None),
    "debt_service_utilization":("up",   "utilization", None),
    "exp_per_capita":          ("up",   "per_capita",  "exp_total"),
    "rev_per_capita":          ("down", "per_capita",  "rev_total"),
    "assessment_per_capita":   ("down", "per_capita",  "equalized_assessment"),
    "exp_police_per_capita":   ("up",   "per_capita",  "exp_police"),
    "exp_fire_per_capita":     ("up",   "per_capita",  "exp_fire"),
    "exp_roads_per_capita":    ("up",   "per_capita",  "exp_roads"),
    "exp_transit_per_capita":  ("up",   "per_capita",  "exp_transit"),
    "exp_parks_rec_per_capita":("up",   "per_capita",  "exp_parks_rec"),
    "exp_culture_per_capita":  ("up",   "per_capita",  "exp_culture"),
    "exp_police_share":        ("up",   "share",       None),
    "exp_fire_share":          ("up",   "share",       None),
    "exp_roads_share":         ("up",   "share",       None),
    "exp_transit_share":       ("up",   "share",       None),
    "exp_parks_rec_share":     ("up",   "share",       None),
    "exp_culture_share":       ("up",   "share",       None),
    "mill_rate_res":           ("up",   "mill_rate",   None),
    "mill_rate_nonres":        ("up",   "mill_rate",   None),
    "fte_per_1000":            ("down", "fte",         "fte_total"),
    "net_financial_assets":    ("down", "balance",     None),
    "accumulated_surplus":     ("down", "balance",     None),
}

EH2_THRESHOLDS = {   # class -> (threshold, kind)
    "utilization": (3.0, "pp"),
    "share":       (2.0, "pp"),
    "per_capita":  (10.0, "pct"),
    "mill_rate":   (10.0, "pct"),
    "fte":         (0.50, "abs"),
    "balance":     (15.0, "pct_of_median_abs_level"),
}
PP1_GAP_PP = 5.0
CR1_ABOVE_MIN_PP = 5.0
CX1_UTILIZATION_PP = 10.0
CX1_RELATIVE_PCT = 15.0  # per-capita and (v1.1) mill rates

# v1.1: metric classes with an owner-approved cross-sectional comparison. Deliverables
# must not render peer context for any other class.
CONTEXT_APPROVED_CLASSES = ("utilization", "per_capita", "mill_rate")


def load_mart():
    with open(CURATED / "metric_mart.json", encoding="utf-8") as f:
        return json.load(f)


def series(mart, mcode, metric_id):
    """year -> value. Includes reported_zero (a zero is a value, never a gap) —
    missing/not_applicable stay out. (v1.2 fold-back, critic finding 7.)"""
    out = {}
    for r in mart["records"]:
        if r["municipality_code"] == mcode and r["metric_id"] == metric_id \
                and r["quality_status"] in ("reported_value", "reported_zero") \
                and r["value"] is not None:
            out[r["year"]] = r["value"]
    return out


def mart_row(mart, year, mcode, metric_id):
    for r in mart["records"]:
        if r["year"] == year and r["municipality_code"] == mcode and r["metric_id"] == metric_id:
            return r
    return None


def adverse_delta(direction, latest, past):
    """Signed movement in the adverse direction (positive = more adverse)."""
    return (latest - past) if direction == "up" else (past - latest)


def fmt(v, nd=2):
    return None if v is None else round(v, nd)


def run_tests(mart, metric_id, spec):
    direction, mclass, pp1_numerator = spec
    ed = series(mart, "0098", metric_id)
    tests = []
    if LATEST not in ed or len(ed) < 4:
        return None  # cannot evaluate without a usable Edmonton history

    latest = ed[LATEST]
    prior = {y: v for y, v in ed.items() if y != LATEST}
    hist_vals = [ed[y] for y in sorted(ed)]
    past_y = LATEST - LOOKBACK
    past = ed.get(past_y)

    # ---- EH-1: latest value is the most adverse in the 8-year history ----
    most_adverse_prior = max(prior.values()) if direction == "up" else min(prior.values())
    eh1 = latest > most_adverse_prior if direction == "up" else latest < most_adverse_prior
    tests.append({
        "test_id": "EH-1", "name": "Edmonton historical level", "family": "historical",
        "triggered": bool(eh1),
        "values": {"latest": fmt(latest, 4), "most_adverse_prior": fmt(most_adverse_prior, 4),
                   "adverse_direction": direction,
                   "history_min": fmt(min(hist_vals), 4), "history_max": fmt(max(hist_vals), 4)},
        "rule": "latest value is the most adverse of 2018-2025",
    })

    # ---- EH-2: 3-year adverse movement >= class threshold ----
    thr, kind = EH2_THRESHOLDS[mclass]
    if past is None:
        tests.append({"test_id": "EH-2", "name": "Edmonton recent movement", "family": "historical",
                      "triggered": False, "values": {"note": f"{past_y} value unavailable"},
                      "rule": "3-year adverse change >= threshold"})
    else:
        if kind == "pp":
            move, rule = adverse_delta(direction, latest, past), f">= {thr} pp adverse over 3 years"
        elif kind == "pct":
            move = adverse_delta(direction, latest, past) / abs(past) * 100 if past else None
            rule = f">= {thr}% adverse over 3 years"
        elif kind == "abs":
            move, rule = adverse_delta(direction, latest, past), f">= {thr} adverse over 3 years"
        else:  # pct_of_median_abs_level
            med = statistics.median(abs(v) for v in hist_vals)
            move = adverse_delta(direction, latest, past) / med * 100 if med else None
            rule = f"adverse change >= {thr}% of 8-year median absolute level"
        tests.append({
            "test_id": "EH-2", "name": "Edmonton recent movement", "family": "historical",
            "triggered": bool(move is not None and move >= thr),
            "values": {"latest": fmt(latest, 4), f"value_{past_y}": fmt(past, 4),
                       "adverse_move": fmt(move, 4), "threshold": thr, "kind": kind},
            "rule": rule,
        })

    # ---- PP-1: pace of the nominal numerator vs population ----
    if pp1_numerator:
        num = series(mart, "0098", pp1_numerator)
        pop = series(mart, "0098", "pop")
        n_now, n_past = num.get(LATEST), num.get(past_y)
        p_now, p_past = pop.get(LATEST), pop.get(past_y)
        if None in (n_now, n_past, p_now, p_past) or n_past <= 0 or p_past <= 0:
            tests.append({"test_id": "PP-1", "name": "Pace relative to population", "family": "pace",
                          "triggered": False, "values": {"note": "inputs unavailable or non-positive"},
                          "rule": f"numerator growth vs population growth gap >= {PP1_GAP_PP} pp"})
        else:
            n_g = (n_now / n_past - 1) * 100
            p_g = (p_now / p_past - 1) * 100
            gap = (n_g - p_g) if direction == "up" else (p_g - n_g)
            tests.append({
                "test_id": "PP-1", "name": "Pace relative to population", "family": "pace",
                "triggered": bool(gap >= PP1_GAP_PP),
                "values": {f"{pp1_numerator}_growth_3yr_pct": fmt(n_g),
                           "population_growth_3yr_pct": fmt(p_g),
                           "adverse_gap_pp": fmt(gap), "threshold_pp": PP1_GAP_PP},
                "rule": f"adverse gap >= {PP1_GAP_PP} pp over 3 years",
            })

    # ---- CR-1: capacity-ratio movement (utilization ratios only) ----
    if mclass == "utilization":
        h_min, h_med = min(hist_vals), statistics.median(hist_vals)
        tests.append({
            "test_id": "CR-1", "name": "Capacity-ratio movement", "family": "capacity",
            "triggered": bool(latest - h_min >= CR1_ABOVE_MIN_PP and latest > h_med),
            "values": {"latest": fmt(latest, 4), "history_min": fmt(h_min, 4),
                       "history_median": fmt(h_med, 4), "above_min_pp": fmt(latest - h_min, 4),
                       "threshold_pp": CR1_ABOVE_MIN_PP},
            "rule": f"latest >= {CR1_ABOVE_MIN_PP} pp above 8-year minimum AND above 8-year median",
        })

    # ---- CX-1: supporting comparison (context only; never creates High) ----
    if mclass in CONTEXT_APPROVED_CLASSES:
        comparators = []
        cal = series(mart, "0046", metric_id).get(LATEST)
        if cal is not None:
            comparators.append(("Calgary", cal))
        med_row = mart_row(mart, LATEST, "AB_CITIES_MEDIAN", metric_id)
        if med_row and med_row["value"] is not None:
            comparators.append((med_row["municipality_name"], med_row["value"]))
        cx_vals, cx_trig = {}, False
        for cname, cval in comparators:
            if mclass == "utilization":
                gap = adverse_delta(direction, latest, cval)
                trig = gap >= CX1_UTILIZATION_PP
                cx_vals[cname] = {"comparator_value": fmt(cval, 4), "adverse_gap_pp": fmt(gap),
                                  "threshold_pp": CX1_UTILIZATION_PP, "triggered": bool(trig)}
            else:  # per_capita and mill_rate: relative threshold (v1.1)
                gap = adverse_delta(direction, latest, cval) / abs(cval) * 100 if cval else None
                trig = gap is not None and gap >= CX1_RELATIVE_PCT
                cx_vals[cname] = {"comparator_value": fmt(cval, 4), "adverse_gap_pct": fmt(gap),
                                  "threshold_pct": CX1_RELATIVE_PCT, "triggered": bool(trig)}
            cx_trig = cx_trig or trig
        if comparators:
            tests.append({
                "test_id": "CX-1", "name": "Supporting comparison", "family": "context",
                "triggered": bool(cx_trig), "supporting_only": True,
                "provisional": LATEST == 2025,
                "values": cx_vals,
                "rule": "context only — can never create a high-priority signal; "
                        "2025 comparisons provisional (306 of 332 returns)",
            })

    return {"metric_id": metric_id, "class": mclass, "adverse_direction": direction,
            "latest": latest, "history": {str(y): ed[y] for y in sorted(ed)}, "tests": tests}


def classify(result):
    core = [t for t in result["tests"] if t["test_id"] in ("EH-1", "EH-2", "PP-1", "CR-1")]
    hist = [t for t in core if t["family"] == "historical" and t["triggered"]]
    trig = [t for t in core if t["triggered"]]
    cx = [t for t in result["tests"] if t["test_id"] == "CX-1" and t["triggered"]]
    if len(trig) >= 2 and hist:
        return "High review priority", trig
    # v1.2 wording (rules §Classification): one or more approved tests triggered without
    # meeting the High criteria -> Watch, including the CX-1-only case. Incomplete
    # supporting evidence stays recorded on the individual tests.
    if trig or cx:
        return "Watch", trig or cx
    return "Not flagged", []


def explain(mart, metric_id, result, status):
    """One cautious, descriptive sentence. No causal or policy language."""
    name, unit = metric_id, ""
    for r in mart["records"]:
        if r["metric_id"] == metric_id and r["municipality_code"] == "0098":
            name, unit = r["metric_name"], r["unit"]
            break
    ed = result["history"]
    latest, first = result["latest"], ed[str(WINDOW[0])] if str(WINDOW[0]) in ed else None
    core_ids = [t["test_id"] for t in result["tests"] if t["triggered"] and t["test_id"] != "CX-1"]
    cx_trig = any(t["triggered"] for t in result["tests"] if t["test_id"] == "CX-1")
    if unit == "%":
        val, base = f"{latest:.2f}%", (f"{first:.2f}%" if first is not None else "n/a")
    elif unit.startswith("$"):
        val, base = f"${latest:,.2f}", (f"${first:,.2f}" if first is not None else "n/a")
    else:
        val, base = f"{latest:,.2f}", (f"{first:,.2f}" if first is not None else "n/a")
    # v1.2 fold-back (critic finding 3): the explanation must agree with the status —
    # a CX-1-only Watch names the supporting comparison as its trigger.
    if core_ids and cx_trig:
        trig_txt = f"tests {', '.join(core_ids)} triggered, with the supporting comparison (CX-1) also triggered"
    elif core_ids:
        trig_txt = f"tests {', '.join(core_ids)} triggered"
    elif cx_trig:
        trig_txt = "only the supporting comparison test (CX-1) triggered — context evidence, insufficient for high priority"
    else:
        trig_txt = "none of the approved tests triggered"
    return (f"{name} is {val} in {LATEST} (2018: {base}); {trig_txt}. "
            f"This flags the area for review; it is not an assessment of financial health."
            if (core_ids or cx_trig) else
            f"{name} is {val} in {LATEST} (2018: {base}); {trig_txt}.")


def main():
    mart = load_mart()
    results = []
    skipped = []
    for metric_id, spec in ELIGIBLE.items():
        r = run_tests(mart, metric_id, spec)
        if r is None:
            skipped.append(metric_id)
            continue
        status, _ = classify(r)
        r["status"] = status
        r["explanation"] = explain(mart, metric_id, r, status)
        results.append(r)

    rank_key = {"High review priority": 0, "Watch": 1, "Not flagged": 2}

    def eh2_exceedance(r):
        for t in r["tests"]:
            if t["test_id"] == "EH-2" and t["triggered"]:
                v = t["values"]
                return (v.get("adverse_move") or 0) / (v.get("threshold") or 1)
        return 0

    def other_exceedance(r):
        """v1.1 tie-break step 4: largest exceedance/threshold on any other triggered
        quantitative core test (PP-1, CR-1)."""
        best = 0
        for t in r["tests"]:
            if not t["triggered"]:
                continue
            v = t.get("values", {})
            if t["test_id"] == "PP-1":
                best = max(best, (v.get("adverse_gap_pp") or 0) / (v.get("threshold_pp") or 1))
            elif t["test_id"] == "CR-1":
                best = max(best, (v.get("above_min_pp") or 0) / (v.get("threshold_pp") or 1))
        return best

    flagged = [r for r in results if r["status"] != "Not flagged"]
    # governance/pressure_rules.md v1.1 §Selection, steps 1-5:
    flagged.sort(key=lambda r: (rank_key[r["status"]],
                                -sum(1 for t in r["tests"] if t["triggered"] and t["test_id"] != "CX-1"),
                                -eh2_exceedance(r),
                                -other_exceedance(r),
                                r["metric_id"]))
    shown, truncated = flagged[:3], flagged[3:]

    out = {
        "reporting_year": LATEST,
        "rules_version": RULES_VERSION,
        "rules_source": "governance/pressure_rules.md",
        "coverage_note": mart["meta"]["coverage_note_2025"],
        "metrics_evaluated": len(results),
        "metrics_skipped_no_history": skipped,
        "signals": shown,
        # v1.1 (critic finding 1): truncated signals carry their FULL test evidence so the
        # drill-down can honour "full evidence available" for every flagged metric.
        "truncated_signals": truncated,
        "context_approved_metrics": sorted(
            mid for mid, spec in ELIGIBLE.items() if spec[1] in CONTEXT_APPROVED_CLASSES),
        # v1.2 (critic re-run finding 4): Not-flagged verdicts publish their full test
        # evidence too — every outcome is verifiable, not just flagged ones.
        "not_flagged": [r for r in results if r["status"] == "Not flagged"],
        "disclaimer": "Signals are transparent flags for human review under documented heuristics. "
                      "They are not City policy, not a fiscal-health score, and not policy recommendations.",
    }
    with open(CURATED / "signals.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)

    # dashboard data bundle (file:// safe)
    DASHBOARD.mkdir(exist_ok=True)
    with open(DASHBOARD / "data.js", "w", encoding="utf-8") as f:
        f.write("// Generated by pipeline/detect_signals.py — do not edit by hand.\n")
        f.write("window.MART = ")
        json.dump(mart, f)
        f.write(";\nwindow.SIGNALS = ")
        json.dump(out, f)
        f.write(";\n")

    print(f"evaluated {len(results)} metrics | flagged {len(flagged)} | shown {len(shown)}"
          f" | truncated {len(truncated)}")
    for r in shown:
        trig = [t["test_id"] for t in r["tests"] if t["triggered"]]
        print(f"  {r['status']:<22} {r['metric_id']:<26} triggered: {trig}")
    print("not flagged:", [r["metric_id"] for r in results if r["status"] == "Not flagged"])


if __name__ == "__main__":
    main()
