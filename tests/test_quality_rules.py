"""Data-quality rule tests: missing vs zero, provisional coverage, source-trace completeness."""
import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CURATED = ROOT / "data" / "curated"


@pytest.fixture(scope="module")
def mart():
    with open(CURATED / "metric_mart.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def fin_long():
    with open(CURATED / "financial_long.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------- Missing vs zero ----------------

def test_missing_and_zero_are_distinct_states(fin_long):
    """2025 AA(1)-Debt municipality rows hold 1,015 reported values and 209 zeros
    (verified against the raw sheet 2026-07-17; the sheet's only blank cells sit on
    the '306 out of 332' footer row, which is not a municipality return). A silent
    blank->0 or 0->blank conversion would move these counts."""
    rows = [r for r in fin_long
            if r["financial_year"] == "2025" and r["schedule"] == "AA(1)-Debt"]
    by_status = {}
    for r in rows:
        by_status[r["quality_status"]] = by_status.get(r["quality_status"], 0) + 1
    assert by_status.get("reported_zero") == 209
    assert by_status.get("reported_value") == 1015
    assert by_status.get("missing") is None  # no genuine blanks among 2025 debt returns


def test_genuine_missing_value_preserved(fin_long):
    """The one genuine blank in the approved-code extract: Granum (0135),
    2021 equalized assessment. It must surface as `missing`, never as zero."""
    rows = [r for r in fin_long if r["quality_status"] == "missing"]
    assert len(rows) == 1
    r = rows[0]
    assert (r["financial_year"], r["schedule"], r["variable_code"], r["municipality_code"]) == \
           ("2021", "EA(1)-Assessment", "08260", "0135")
    assert r["value"] == ""
    # and zeros exist elsewhere in volume, so the two states demonstrably coexist
    assert sum(1 for x in fin_long if x["quality_status"] == "reported_zero") == 6295


def test_no_missing_row_carries_a_value(fin_long):
    for r in fin_long:
        if r["quality_status"] == "missing":
            assert r["value"] == "", f"missing row has value {r['value']!r}"
        if r["quality_status"] == "reported_zero":
            assert float(r["value"]) == 0.0


def test_derived_metrics_not_computed_from_missing_inputs(mart):
    for r in mart["records"]:
        if r["quality_status"] in ("not_applicable", "missing"):
            assert r["value"] is None, (
                f"{r['year']}/{r['municipality_code']}/{r['metric_id']} has "
                f"quality {r['quality_status']} but a value")


# ---------------- Provisional 2025 peer coverage ----------------

def test_2025_coverage_is_306(mart):
    assert mart["meta"]["returns_received_by_year"]["2025"] == 306


def test_2025_peer_rows_labelled_provisional(mart):
    peers = [r for r in mart["records"]
             if r["year"] == 2025 and r["municipality_code"] == "AB_CITIES_MEDIAN"]
    assert peers, "expected AB_CITIES_MEDIAN rows for 2025"
    for r in peers:
        assert r["comparability_status"] == "provisional_peer_year"


def test_peer_rows_disclose_included_count(mart):
    for r in mart["records"]:
        if r["municipality_code"] == "AB_CITIES_MEDIAN" and r["value"] is not None:
            assert "n=" in r["municipality_name"]
            assert "reporting cities" in r["data_quality_note"]


# ---------------- Source-trace completeness ----------------

def test_every_mart_row_has_full_source_trace(mart):
    for r in mart["records"]:
        for field in ("source_file", "source_schedule", "source_variable_code",
                      "quality_status", "unit", "metric_id", "metric_name"):
            assert r.get(field), f"row {r['year']}/{r['municipality_code']}/{r['metric_id']} missing {field}"


def test_every_derived_row_shows_formula(mart):
    for r in mart["records"]:
        if r["source_schedule"] == "derived" and r["municipality_code"] in ("0098", "0046"):
            assert r["formula"], f"derived row {r['metric_id']} has no formula"


def test_dollar_metrics_labelled_nominal(mart):
    """Every dollar unit is nominal, except the owner-approved (2026-07-18) Edmonton
    *_real2025 display context, which must be labelled constant 2025 instead."""
    for r in mart["records"]:
        if not r["unit"].startswith("$"):
            continue
        if r["metric_id"].endswith("_real2025"):
            assert "constant 2025" in r["unit"], \
                f"{r['metric_id']} real row not labelled constant 2025"
            assert r["municipality_code"] == "0098", \
                f"{r['metric_id']} constant-2025 approval is Edmonton-only"
        else:
            assert "nominal" in r["unit"], f"{r['metric_id']} dollar unit not labelled nominal"


# ---------------- structurally_unavailable (critic finding 5, v1.1) ----------------

def test_structurally_unavailable_state_is_real(mart):
    """Per-capita peer medians cannot be computed without population joins beyond the
    approved crosswalk — the mart must say so explicitly, not stay silent."""
    rows = [r for r in mart["records"] if r["quality_status"] == "structurally_unavailable"]
    assert rows, "expected structurally_unavailable rows for per-capita peer medians"
    for r in rows:
        assert r["municipality_code"] == "AB_CITIES_MEDIAN"
        assert r["value"] is None
        assert "crosswalk" in r["data_quality_note"]
    ids = {r["metric_id"] for r in rows}
    assert "exp_per_capita" in ids and "fte_per_1000" in ids


# ---------------- Raw preservation ----------------

def test_raw_files_present_and_untouched_names(mart):
    raw = ROOT / "data" / "raw"
    files = sorted(p.name for p in raw.glob("*.xlsx"))
    assert len(files) == 9
    for year in range(2018, 2026):
        assert f"{year}_financial_year.xlsx" in files
