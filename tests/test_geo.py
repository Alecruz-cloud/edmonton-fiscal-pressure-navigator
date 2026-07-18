"""Known-answer tests for the Alberta context map artifacts (pipeline/build_geo.py).

The map is supporting context only (pressure_rules.md v1.2). These tests pin:
  * the artifact parses and carries all 19 crosswalked cities with coordinates;
  * Edmonton's centroid lands where Edmonton is;
  * the gold example is reproduced from the map's own values;
  * embedded per-city values reproduce the mart's published medians (no second truth);
  * missing stays missing (Beaumont's 2018 town-status year is a named state, not a zero).
"""
import csv
import json
import statistics
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GEO_JS = ROOT / "dashboard" / "geo.js"
GEO_JSON = ROOT / "data" / "curated" / "alberta_geo.json"

MAP_METRICS = ["debt_utilization", "debt_service_utilization", "mill_rate_res", "mill_rate_nonres"]
YEARS = [str(y) for y in range(2018, 2026)]


@pytest.fixture(scope="module")
def geo():
    with open(GEO_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def mart_medians():
    out = {}
    with open(ROOT / "data" / "curated" / "metric_mart.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["municipality_code"] == "AB_CITIES_MEDIAN" and r["metric_id"] in MAP_METRICS:
                v = float(r["value"]) if r["value"] not in ("", None) else None
                out[(r["metric_id"], r["year"])] = v
    return out


def test_geo_js_parses_and_matches_audit_copy(geo):
    text = GEO_JS.read_text(encoding="utf-8")
    payload = text.split("window.GEO = ", 1)[1].rstrip().rstrip(";")
    assert json.loads(payload) == geo, "dashboard/geo.js must equal the audit copy"


def test_all_19_cities_have_coordinates(geo):
    assert len(geo["cities"]) == 19
    for c in geo["cities"]:
        assert c["lon"] is not None and c["lat"] is not None, c["name"]
        assert -120.5 <= c["lon"] <= -109.5, c
        assert 48.5 <= c["lat"] <= 60.5, c


def test_edmonton_centroid_is_in_edmonton(geo):
    ed = next(c for c in geo["cities"] if c["code"] == "0098")
    assert ed["csd"] == "4811061"
    assert -113.8 <= ed["lon"] <= -113.1
    assert 53.3 <= ed["lat"] <= 53.8


def test_lloydminster_is_the_alberta_part(geo):
    ll = next(c for c in geo["cities"] if c["code"] == "0206")
    assert ll["csd"] == "4810039"
    assert 52.8 <= ll["lat"] <= 53.6 and -110.5 <= ll["lon"] <= -109.8


def test_gold_example_reproduced(geo):
    v = geo["values"]["debt_utilization"]["2025"]["0098"]
    assert v is not None and abs(v - 59.27) <= 0.01


def test_map_medians_reproduce_mart_medians(geo, mart_medians):
    checked = 0
    for mid in MAP_METRICS:
        for year in YEARS:
            vals = [v for code, v in geo["values"][mid][year].items()
                    if code != "0098" and v is not None]
            mart_v = mart_medians.get((mid, year))
            if mart_v is None:
                assert not vals
                continue
            med = statistics.median(vals)
            assert abs(med - mart_v) <= 1e-4, (mid, year, med, mart_v)
            assert len(vals) == geo["medians"][mid][year]["n"]
            checked += 1
    assert checked >= 30, "expected medians for nearly all metric-years"


def test_beaumont_2018_is_named_state_not_zero(geo):
    assert "0019" not in geo["city_set_by_year"]["2018"]
    assert geo["values"]["debt_utilization"]["2018"]["0019"] is None
    assert "not in the city set" in geo["null_reasons"]["debt_utilization"]["2018"]["0019"]
    assert "0019" in geo["city_set_by_year"]["2019"]


def test_every_null_value_has_a_reason(geo):
    for mid in MAP_METRICS:
        for year in YEARS:
            for code, v in geo["values"][mid][year].items():
                if v is None:
                    assert geo["null_reasons"][mid][year].get(code), (mid, year, code)


def test_outline_is_alberta_sized(geo):
    pts = [p for ring in geo["outline"] for p in ring]
    assert len(pts) >= 100
    lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
    # Alberta bbox: 49-60 N, -120 to -110 W (cartographic tolerance)
    assert min(lats) <= 49.5 and max(lats) >= 59.5
    assert min(lons) <= -119.0 and max(lons) >= -110.5


def test_scope_note_present(geo):
    note = geo["meta"]["scope_note"]
    assert "never create" in note and "provisional" in note
