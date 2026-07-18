"""Signal-engine tests against governance/pressure_rules.md v1.2 (approved 2026-07-17).

These test the OUTPUT (data/curated/signals.json), not the engine code.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def sig():
    with open(ROOT / "data" / "curated" / "signals.json", encoding="utf-8") as f:
        return json.load(f)


# ---------------- Structural rules (fixed by CLAUDE.md) ----------------

def test_at_most_three_signals(sig):
    assert len(sig["signals"]) <= 3


def test_high_priority_needs_two_tests_including_historical(sig):
    for s in sig["signals"]:
        if s["status"] == "High review priority":
            core = [t for t in s["tests"]
                    if t["test_id"] in ("EH-1", "EH-2", "PP-1", "CR-1") and t["triggered"]]
            hist = [t for t in core if t["family"] == "historical"]
            assert len(core) >= 2, f"{s['metric_id']}: High with fewer than 2 core tests"
            assert hist, f"{s['metric_id']}: High without an Edmonton historical test"


def test_context_comparison_never_creates_high(sig):
    """Known-answer case: debt_utilization triggers only CX-1 in 2025
    (EH-1 no: 2022 peak; EH-2 no: 3-yr movement is an improvement; CR-1 no:
    4.75 pp above minimum < 5.0 and below the 8-year median). It must be Watch."""
    all_flagged = {x["metric_id"]: x["status"] for x in sig["truncated_signals"]}
    all_flagged.update({s["metric_id"]: s["status"] for s in sig["signals"]})
    assert all_flagged.get("debt_utilization") == "Watch"


def test_every_signal_shows_tests_values_and_explanation(sig):
    for s in sig["signals"]:
        assert s["tests"], f"{s['metric_id']} has no test evidence"
        for t in s["tests"]:
            assert "triggered" in t and "values" in t and "rule" in t
        assert s["explanation"]
        assert s["history"], "signal must carry its Edmonton historical series"


def test_truncation_is_disclosed(sig):
    """13 metrics flag under v1.0 rules; anything beyond the top 3 must be listed,
    including the fourth High signal (fte_per_1000)."""
    truncated_ids = {x["metric_id"] for x in sig["truncated_signals"]}
    assert "fte_per_1000" in truncated_ids


def test_known_no_flag_case(sig):
    """rev_per_capita triggers no approved test in 2025 — must be Not flagged."""
    assert "rev_per_capita" in {x["metric_id"] for x in sig["not_flagged"]}
    shown_or_truncated = {s["metric_id"] for s in sig["signals"]}
    shown_or_truncated |= {x["metric_id"] for x in sig["truncated_signals"]}
    assert "rev_per_capita" not in shown_or_truncated


# ---------------- Disclosure & language ----------------

def test_context_tests_flagged_supporting_and_provisional(sig):
    for s in sig["signals"]:
        for t in s["tests"]:
            if t["test_id"] == "CX-1":
                assert t.get("supporting_only") is True
                assert t.get("provisional") is True  # 2025 peer year


def test_run_carries_rules_version_and_coverage(sig):
    assert sig["rules_version"].startswith("1.2")
    assert "306 of 332" in sig["coverage_note"]
    assert "not policy recommendations" in sig["disclaimer"]


# ---------------- v1.2 fold-back regression tests (critic re-run findings 3, 4, 5, 7) ----------------

def test_cx_only_watch_explanations_name_the_trigger(sig):
    """Critic re-run finding 3: a CX-1-only Watch must not claim nothing triggered."""
    for s in sig["truncated_signals"]:
        core = [t for t in s["tests"]
                if t["test_id"] != "CX-1" and t["triggered"]]
        cx = [t for t in s["tests"] if t["test_id"] == "CX-1" and t["triggered"]]
        if s["status"] == "Watch" and not core and cx:
            assert "supporting comparison" in s["explanation"], s["metric_id"]
            assert "none of the approved tests" not in s["explanation"], s["metric_id"]


def test_not_flagged_verdicts_carry_full_evidence(sig):
    """Critic re-run finding 4: every outcome is verifiable, including Not flagged."""
    assert sig["not_flagged"], "expected not-flagged metrics under current data"
    for r in sig["not_flagged"]:
        assert r.get("tests"), f"{r['metric_id']} not-flagged without test evidence"
        assert r.get("history"), f"{r['metric_id']} not-flagged without history"
        core_trig = [t for t in r["tests"] if t["test_id"] != "CX-1" and t["triggered"]]
        assert not core_trig, f"{r['metric_id']} marked Not flagged with a triggered core test"


def test_median_excludes_subject_and_names_cities():
    """Critic re-run finding 5 / rules v1.2: Edmonton is excluded from its own comparator
    and the included municipalities are named. mill_rate_res median must not equal
    Edmonton's own 7.6254 (the pre-v1.2 self-comparison artifact)."""
    with open(ROOT / "data" / "curated" / "metric_mart.json", encoding="utf-8") as f:
        mart = json.load(f)
    row = next(r for r in mart["records"]
               if r["year"] == 2025 and r["municipality_code"] == "AB_CITIES_MEDIAN"
               and r["metric_id"] == "mill_rate_res")
    assert row["value"] != 7.6254
    assert row["value"] == pytest.approx(7.5567, abs=0.001)  # critic's excl-Edmonton recompute
    assert "excl. Edmonton" in row["municipality_name"]
    assert "included:" in row["data_quality_note"] and "Calgary" in row["data_quality_note"]


def test_series_includes_reported_zero():
    """Critic re-run finding 7: a reported zero is a value in signal histories, never a gap."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "detect_signals", ROOT / "pipeline" / "detect_signals.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fake = {"records": [
        {"municipality_code": "0098", "metric_id": "m", "year": 2024,
         "quality_status": "reported_zero", "value": 0.0},
        {"municipality_code": "0098", "metric_id": "m", "year": 2025,
         "quality_status": "reported_value", "value": 5.0},
        {"municipality_code": "0098", "metric_id": "m", "year": 2023,
         "quality_status": "missing", "value": None},
    ]}
    s = mod.series(fake, "0098", "m")
    assert s == {2024: 0.0, 2025: 5.0}  # zero present, missing absent


# ---------------- v1.1 fold-back regression tests (critic findings 1, 2, 5, 8) ----------------

def test_truncated_signals_carry_full_evidence(sig):
    """Critic finding 1: every truncated signal must be verifiable — tests, values,
    history, status — so the drill-down honours 'full evidence available'."""
    assert sig["truncated_signals"], "expected truncated signals under current data"
    for t in sig["truncated_signals"]:
        assert t.get("status") in ("High review priority", "Watch")
        assert t.get("tests"), f"{t['metric_id']} truncated without test evidence"
        assert t.get("history"), f"{t['metric_id']} truncated without history"
        assert t.get("explanation")


def test_tiebreak_is_documented_rule_not_dict_order(sig):
    """Critic finding 2 / rules v1.1 steps 4-5: police (PP-1 exceedance 9.32/5=1.86)
    outranks fte_per_1000 (5.58/5=1.12) for the third slot by the documented rule."""
    shown = [s["metric_id"] for s in sig["signals"]]
    assert shown[2] == "exp_police_per_capita"
    pol = next(s for s in sig["signals"] if s["metric_id"] == "exp_police_per_capita")
    fte = next(t for t in sig["truncated_signals"] if t["metric_id"] == "fte_per_1000")
    def pp1_exc(r):
        t = next(x for x in r["tests"] if x["test_id"] == "PP-1")
        return t["values"]["adverse_gap_pp"] / t["values"]["threshold_pp"]
    assert pp1_exc(pol) > pp1_exc(fte)


def test_mill_rate_signal_has_supporting_comparison(sig):
    """Critic finding 8 / rules v1.1: CX-1 extended to mill rates at 15% relative."""
    s = next(x for x in sig["signals"] if x["metric_id"] == "mill_rate_nonres")
    cx = [t for t in s["tests"] if t["test_id"] == "CX-1"]
    assert cx and cx[0].get("supporting_only") is True
    assert any(v.get("threshold_pct") == 15.0 for v in cx[0]["values"].values()
               if isinstance(v, dict))


def test_context_approved_metrics_exported(sig):
    """Rules v1.1: deliverables need the approved-comparison list; balance-sheet dollars
    must not be in it."""
    ok = set(sig["context_approved_metrics"])
    assert "debt_utilization" in ok and "exp_per_capita" in ok and "mill_rate_nonres" in ok
    assert "net_financial_assets" not in ok and "accumulated_surplus" not in ok


def test_explanations_use_descriptive_language(sig):
    banned = ("caused", "because of", "should raise", "should cut", "must borrow",
              "healthy", "unhealthy", "recommend")
    for s in sig["signals"]:
        low = s["explanation"].lower()
        for w in banned:
            assert w not in low, f"{s['metric_id']} explanation contains {w!r}"


# ---------------- Hand-verified anchors (recomputed from raw 2026-07-17) ----------------

def test_parks_rec_signal_values(sig):
    s = next(x for x in sig["signals"] if x["metric_id"] == "exp_parks_rec_per_capita")
    assert s["latest"] == pytest.approx(295.9707, abs=0.01)  # 366,499,000 / 1,238,295
    eh2 = next(t for t in s["tests"] if t["test_id"] == "EH-2")
    assert eh2["values"]["adverse_move"] == pytest.approx(20.70, abs=0.01)


def test_mill_rate_nonres_signal_values(sig):
    s = next(x for x in sig["signals"] if x["metric_id"] == "mill_rate_nonres")
    assert s["latest"] == pytest.approx(24.2229, abs=0.0001)
    eh2 = next(t for t in s["tests"] if t["test_id"] == "EH-2")
    assert eh2["values"]["adverse_move"] == pytest.approx(14.92, abs=0.01)
