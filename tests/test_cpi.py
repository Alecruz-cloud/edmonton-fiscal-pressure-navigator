"""CPI display-context tests — StatCan 18-10-0005-01, All-items Alberta, base 2025.

Owner-approved 2026-07-18, display-only. The pinned values below were verified against
the raw StatCan table on download day; the signal engine must never read these rows.
"""
import csv
import io
import json
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PINNED_CPI = {2018: 140.6, 2019: 143.1, 2020: 144.7, 2021: 149.3,
              2022: 158.9, 2023: 164.1, 2024: 168.9, 2025: 172.2}


@pytest.fixture(scope="module")
def mart():
    with open(ROOT / "data" / "curated" / "metric_mart.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def signals():
    with open(ROOT / "data" / "curated" / "signals.json", encoding="utf-8") as f:
        return json.load(f)


def row(mart, year, mid):
    for r in mart["records"]:
        if r["year"] == year and r["municipality_code"] == "0098" and r["metric_id"] == mid:
            return r
    return None


def test_cpi_source_reproduces_pinned_values():
    """Independent re-extraction from the raw zip must equal the owner-verified values."""
    got = {}
    with zipfile.ZipFile(ROOT / "data" / "raw" / "18100005-eng.zip") as z, \
            z.open("18100005.csv") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig")):
            if (r["GEO"] == "Alberta" and r["Products and product groups"] == "All-items"
                    and r["REF_DATE"].isdigit() and 2018 <= int(r["REF_DATE"]) <= 2025):
                assert r["UOM"] == "2002=100", "CPI unit of measure changed"
                assert not r["STATUS"].strip(), "CPI value carries a status flag"
                assert int(r["REF_DATE"]) not in got, "duplicate CPI source row"
                got[int(r["REF_DATE"])] = float(r["VALUE"])
    assert got == PINNED_CPI


def test_meta_carries_cpi_provenance(mart):
    ctx = mart["meta"]["cpi_context"]
    assert ctx["table"] == "18-10-0005-01"
    assert ctx["base_year"] == 2025
    assert {int(k): v for k, v in ctx["values"].items()} == PINNED_CPI
    assert "display-only" in ctx["scope"]


def test_base_year_identity(mart):
    """2025 real == 2025 nominal, exactly — the base year deflates to itself."""
    reals = [r for r in mart["records"]
             if r["metric_id"].endswith("_real2025") and r["year"] == 2025]
    assert reals, "no real rows for the base year"
    for r in reals:
        nom = row(mart, 2025, r["metric_id"][: -len("_real2025")])
        if r["value"] is None:
            assert nom["value"] is None
        else:
            assert r["value"] == nom["value"]


def test_known_answer_deflation(mart):
    """2018 expense per capita in 2025 dollars: published nominal x 172.2/140.6."""
    nom = row(mart, 2018, "exp_per_capita")
    real = row(mart, 2018, "exp_per_capita_real2025")
    expected = round(nom["value"] * PINNED_CPI[2025] / PINNED_CPI[2018], 6)
    assert real["value"] == pytest.approx(expected, abs=1e-6)
    assert real["value"] == pytest.approx(3699.4255, abs=0.01)  # owner-verifiable literal


def test_real_rows_scope_and_traces(mart):
    reals = [r for r in mart["records"] if r["metric_id"].endswith("_real2025")]
    assert len(reals) == 26 * 8, "26 dollar metrics x 8 years"
    for r in reals:
        assert r["municipality_code"] == "0098", "approval is Edmonton-only"
        assert "constant 2025" in r["unit"]
        assert r["comparability_status"] == "display_only_context"
        if r["value"] is not None:
            assert "18-10-0005" in r["data_quality_note"]
            assert "rules v1.2" in r["data_quality_note"]


def test_signal_engine_never_reads_real_rows(signals):
    ids = {s["metric_id"]
           for k in ("signals", "truncated_signals", "not_flagged") for s in signals[k]}
    assert not [i for i in ids if i.endswith("_real2025")]
    assert not [i for i in signals["context_approved_metrics"] if i.endswith("_real2025")]
    assert signals["metrics_evaluated"] == 22  # unchanged by the CPI context
