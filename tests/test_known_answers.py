"""Known-answer tests — the gold example and the two owner-approved extra checks (G3).

These test the OUTPUT in data/curated/, not the pipeline code. Expected values were
certified against the raw workbooks during the 2026-07-17 read-only audit and are
recorded in governance/metric_dictionary.md.
"""
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


def get(mart, year, mcode, metric_id):
    rows = [r for r in mart["records"]
            if r["year"] == year and r["municipality_code"] == mcode and r["metric_id"] == metric_id]
    assert len(rows) == 1, f"expected exactly one row for {year}/{mcode}/{metric_id}, got {len(rows)}"
    return rows[0]


# ---------------- Gold example: Edmonton 2025 ----------------

def test_gold_population(mart):
    assert get(mart, 2025, "0098", "pop")["value"] == 1238295


def test_gold_population_source_is_estimates_workbook(mart):
    row = get(mart, 2025, "0098", "pop")
    assert row["source_file"].startswith("population-estimates")
    assert "4811061" in row["source_variable_code"]


def test_gold_total_debt(mart):
    assert get(mart, 2025, "0098", "debt_total")["value"] == 4592150000


def test_gold_debt_limit(mart):
    assert get(mart, 2025, "0098", "debt_limit")["value"] == 7748380000


def test_gold_debt_utilization(mart):
    row = get(mart, 2025, "0098", "debt_utilization")
    assert row["value"] == pytest.approx(59.2659, abs=0.01)  # tolerance: 0.01 pp
    assert row["formula"] == "debt_total / debt_limit"


def test_gold_total_expense(mart):
    assert get(mart, 2025, "0098", "exp_total")["value"] == 4043938000


def test_gold_expense_per_capita(mart):
    row = get(mart, 2025, "0098", "exp_per_capita")
    assert row["value"] == pytest.approx(3265.7307, abs=0.01)  # tolerance: $0.01
    assert "nominal" in row["unit"] or "nominal" in row["data_quality_note"]


# ---------------- Extra known answers (different domains, G3-approved) ----------------

def test_extra_debt_utilization_2022(mart):
    """Domain B, different year: 3,940,329,000 / 6,146,130,000 = 64.11%."""
    assert get(mart, 2022, "0098", "debt_utilization")["value"] == pytest.approx(64.11, abs=0.01)


def test_extra_fte_per_1000_2025(mart):
    """Domain D: 11,917 / 1,238.295k = 9.6237."""
    assert get(mart, 2025, "0098", "fte_per_1000")["value"] == pytest.approx(9.6237, abs=0.001)


# ---------------- Stale-population guard ----------------

def test_population_never_from_financial_workbook(mart):
    """2023-2025 financial workbooks repeat 1,010,899 for Edmonton. The mart must show
    the estimates-workbook values instead."""
    expected = {2023: 1127183, 2024: 1197770, 2025: 1238295}
    for year, pop in expected.items():
        row = get(mart, year, "0098", "pop")
        assert row["value"] == pop
        assert row["value"] != 1010899
