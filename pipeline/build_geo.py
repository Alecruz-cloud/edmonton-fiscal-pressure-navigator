"""Alberta context map — geometry and per-city values for the approved CX ratio classes.

Deterministic raw -> curated build, run after build_mart.py. Reads READ-ONLY:

    data/raw/lcsd000b21a_e.zip            StatCan 2021 Census cartographic boundary file,
                                          census subdivisions (EPSG:3347). Source approved
                                          by the owner 2026-07-17 (map decision record).
    governance/municipality_crosswalk.csv 19 Alberta cities, geo/context-map scope
    data/curated/financial_long.csv       inputs for the four approved CX metric classes
    data/curated/metric_mart.csv          published medians (consistency cross-check)

Writes:
    data/curated/alberta_geo.json         audit copy
    dashboard/geo.js                      window.GEO consumed by the Map view

Load-bearing rules:
  * the map shows only the four financial-workbook-only CX classes approved in
    governance/pressure_rules.md v1.2 (debt_utilization, debt_service_utilization,
    mill_rate_res, mill_rate_nonres) — never per-capita peer values (structurally
    unavailable) and never a signal;
  * per-city values replicate build_mart.py semantics exactly: derived ratios need the
    numerator reported and the denominator reported non-zero; mill rates need
    quality_status == reported_value. Missing stays missing — never zero;
  * hard guards: every crosswalk city must match exactly one CSD polygon; Edmonton's
    2025 debt utilization must reproduce the gold example (59.27 ±0.01 pp); the median
    of the embedded per-city values must equal the mart's published median per
    metric-year (±1e-6) with the same included count.
"""
from __future__ import annotations

import csv
import json
import statistics
import tempfile
import zipfile
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CURATED = ROOT / "data" / "curated"
DASHBOARD = ROOT / "dashboard"
BOUNDARY_ZIP = RAW / "lcsd000b21a_e.zip"
SOURCE_DESC = ("Statistics Canada, 2021 Census cartographic boundary file, census "
               "subdivisions (lcsd000b21a_e.zip, EPSG:3347), downloaded 2026-07-17; "
               "owner-approved external source, geo/context-map scope only")

YEARS = list(range(2018, 2026))
SUBJECT = "0098"
GOLD_DEBT_UTILIZATION_2025 = 59.27   # gold example, tolerance 0.01 pp
OUTLINE_SIMPLIFY_M = 1500            # metres, applied in EPSG:3347 before reprojection
COORD_DECIMALS = 4                   # ~11 m at this latitude — display only

# The four approved CX classes (pressure_rules.md v1.2). Mirrors build_mart.MEDIAN_METRICS.
MAP_METRICS = {
    "debt_utilization": {
        "name": "Debt utilization", "unit": "%", "kind": "derived",
        "num": ("AA(1)-Debt", "05710"), "den": ("AA(1)-Debt", "05700"), "scale": 100.0,
        "formula": "debt_total / debt_limit",
    },
    "debt_service_utilization": {
        "name": "Debt-service utilization", "unit": "%", "kind": "derived",
        "num": ("AA(1)-Debt", "05730"), "den": ("AA(1)-Debt", "05720"), "scale": 100.0,
        "formula": "debt_service_cost / debt_service_limit",
    },
    "mill_rate_res": {
        "name": "Residential general municipal mill rate", "unit": "mills", "kind": "base",
        "src": ("MR(3)-Mill Rate", "10030"), "formula": "source value",
    },
    "mill_rate_nonres": {
        "name": "Non-residential general municipal mill rate", "unit": "mills", "kind": "base",
        "src": ("MR(3)-Mill Rate", "10034"), "formula": "source value",
    },
}


def read_crosswalk():
    cities = []
    with open(ROOT / "governance" / "municipality_crosswalk.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cities.append({
                "code": r["financial_municipality_code"],
                "name": r["name_normalized"],
                "csd": r["census_subdivision_code"],
                "match_status": r["match_status"],
            })
    if len(cities) != len({c["code"] for c in cities}):
        raise RuntimeError("crosswalk: duplicate financial codes")
    return cities


def read_financial():
    """financial_long.csv -> index (year, code, schedule, vcode) -> (value, quality)."""
    ix, status_by_year = {}, {}
    with open(CURATED / "financial_long.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y = int(r["financial_year"])
            v = float(r["value"]) if r["value"] not in ("", None) else None
            ix[(y, r["municipality_code"], r["schedule"], r["variable_code"])] = (v, r["quality_status"])
            if r["municipality_status"] == "City":
                status_by_year.setdefault(y, set()).add(r["municipality_code"])
    return ix, status_by_year


def city_value(ix, year, code, spec):
    """Replicates build_mart.py guards. Returns (value|None, reason_if_null)."""
    if spec["kind"] == "derived":
        nr = ix.get((year, code) + spec["num"])
        dr = ix.get((year, code) + spec["den"])
        if not nr or not dr or nr[0] is None or dr[0] in (None, 0.0):
            if dr and dr[0] == 0.0:
                return None, "denominator reported zero"
            return None, "input missing — not computed (missing is never treated as zero)"
        return nr[0] / dr[0] * spec["scale"], ""
    r = ix.get((year, code) + spec["src"])
    if not r or r[1] != "reported_value":
        return None, "value not reported"
    return r[0], ""


def read_mart_medians():
    """Published AB_CITIES_MEDIAN rows for the four classes -> {(mid, year): (value, n)}."""
    out = {}
    with open(CURATED / "metric_mart.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["municipality_code"] == "AB_CITIES_MEDIAN" and r["metric_id"] in MAP_METRICS:
                v = float(r["value"]) if r["value"] not in ("", None) else None
                name = r["municipality_name"]           # "... excl. Edmonton (n=18)"
                n = int(name.split("(n=")[1].rstrip(")")) if "(n=" in name else None
                out[(r["metric_id"], int(r["year"]))] = (v, n)
    return out


def extract_geometry(cities):
    """StatCan shapefile -> (outline_rings, {csd: (lon, lat)}). Fails on any unmatched city."""
    csds = [c["csd"] for c in cities]
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(BOUNDARY_ZIP) as z:
            z.extractall(tmp)
        shp = next(Path(tmp).glob("*.shp"))
        con = duckdb.connect()
        con.execute("INSTALL spatial; LOAD spatial;")

        rows = con.execute(
            f"""
            SELECT CSDUID,
                   ST_AsGeoJSON(ST_Transform(ST_Centroid(geom),
                       'EPSG:3347', 'EPSG:4326', always_xy := true)) AS pt
            FROM st_read('{shp.as_posix()}')
            WHERE PRUID = '48' AND CSDUID IN ({", ".join("?" * len(csds))})
            """,
            csds,
        ).fetchall()
        centroids = {}
        for csduid, pt in rows:
            lon, lat = json.loads(pt)["coordinates"]
            centroids[csduid] = (round(lon, COORD_DECIMALS), round(lat, COORD_DECIMALS))
        missing = [c for c in cities if c["csd"] not in centroids]
        if missing:
            raise RuntimeError(f"boundary file: no CSD polygon for {missing} — refusing silent drop")

        outline_geojson = con.execute(
            f"""
            SELECT ST_AsGeoJSON(ST_Transform(
                       ST_Simplify(ST_Union_Agg(geom), {OUTLINE_SIMPLIFY_M}),
                       'EPSG:3347', 'EPSG:4326', always_xy := true))
            FROM st_read('{shp.as_posix()}')
            WHERE PRUID = '48'
            """
        ).fetchone()[0]
        con.close()

    g = json.loads(outline_geojson)
    polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    rings = []
    for poly in polys:                       # outer ring only; union slivers dropped
        outer = poly[0]
        if len(outer) >= 30:
            rings.append([[round(x, COORD_DECIMALS), round(y, COORD_DECIMALS)] for x, y in outer])
    if not rings:
        raise RuntimeError("outline: no ring with >= 30 points after simplification")
    return rings, centroids


def main():
    cities = read_crosswalk()
    fin_ix, city_set_by_year = read_financial()
    mart_medians = read_mart_medians()

    # raw_values feed the median guard unrounded, matching build_mart.py's order of
    # operations (median over raw ratios, rounded once at the end); values are the
    # 6-decimal display copies embedded in geo.js.
    values, raw_values, null_reasons = {}, {}, {}
    for mid, spec in MAP_METRICS.items():
        values[mid], raw_values[mid], null_reasons[mid] = {}, {}, {}
        for year in YEARS:
            vy, rawy, ry = {}, {}, {}
            for c in cities:
                if c["code"] not in city_set_by_year.get(year, set()):
                    vy[c["code"]] = None
                    ry[c["code"]] = "not in the city set this year (non-city status)"
                    continue
                v, reason = city_value(fin_ix, year, c["code"], spec)
                vy[c["code"]] = round(v, 6) if v is not None else None
                rawy[c["code"]] = v
                if v is None:
                    ry[c["code"]] = reason
            values[mid][year] = vy
            raw_values[mid][year] = rawy
            null_reasons[mid][year] = ry

    # --- hard guard 1: gold example ---
    ed25 = values["debt_utilization"][2025][SUBJECT]
    if ed25 is None or abs(ed25 - GOLD_DEBT_UTILIZATION_2025) > 0.01:
        raise RuntimeError(f"gold check failed: Edmonton 2025 debt utilization {ed25!r} "
                           f"vs {GOLD_DEBT_UTILIZATION_2025} ±0.01 pp")

    # --- hard guard 2: medians reproduce the published mart medians ---
    medians = {}
    for mid in MAP_METRICS:
        medians[mid] = {}
        for year in YEARS:
            peer_vals = [v for code, v in raw_values[mid][year].items()
                         if code != SUBJECT and v is not None]
            med = round(statistics.median(peer_vals), 6) if peer_vals else None
            mart_v, mart_n = mart_medians.get((mid, year), (None, None))
            if mart_v is None if med is not None else mart_v is not None:
                raise RuntimeError(f"median presence mismatch {mid} {year}: geo {med!r} vs mart {mart_v!r}")
            if med is not None and (abs(med - mart_v) > 1e-6 or len(peer_vals) != mart_n):
                raise RuntimeError(f"median mismatch {mid} {year}: geo {med} (n={len(peer_vals)}) "
                                   f"vs mart {mart_v} (n={mart_n})")
            medians[mid][year] = {"value": med, "n": len(peer_vals)}

    outline, centroids = extract_geometry(cities)

    geo = {
        "meta": {
            "source": SOURCE_DESC,
            "source_zip": "data/raw/lcsd000b21a_e.zip",
            "crs": "EPSG:3347 -> EPSG:4326 (always_xy)",
            "outline_simplify_m": OUTLINE_SIMPLIFY_M,
            "generated_by": "pipeline/build_geo.py",
            "scope_note": ("Supporting context only (pressure_rules.md v1.2 CX classes). "
                           "Cross-sectional comparison alone can never create a high-priority "
                           "signal; the map never generates or upgrades signals. 2025 peer "
                           "values are provisional (306 of 332 returns received)."),
            "crosswalk": "governance/municipality_crosswalk.csv + governance/crosswalk_signoff.md",
        },
        "outline": outline,
        "cities": [{"code": c["code"], "name": c["name"], "csd": c["csd"],
                    "lon": centroids[c["csd"]][0], "lat": centroids[c["csd"]][1]}
                   for c in cities],
        "metrics": {mid: {"name": s["name"], "unit": s["unit"], "formula": s["formula"]}
                    for mid, s in MAP_METRICS.items()},
        "values": values,
        "null_reasons": null_reasons,
        "medians": medians,
        "city_set_by_year": {y: sorted(city_set_by_year.get(y, set())) for y in YEARS},
    }

    CURATED.mkdir(parents=True, exist_ok=True)
    with open(CURATED / "alberta_geo.json", "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=1)
    with open(DASHBOARD / "geo.js", "w", encoding="utf-8") as f:
        f.write("// Generated by pipeline/build_geo.py — do not edit. "
                "Source: StatCan 2021 CSD cartographic boundary file (owner-approved 2026-07-17).\n")
        f.write("window.GEO = ")
        json.dump(geo, f, separators=(",", ":"))
        f.write(";\n")

    pts = sum(len(r) for r in outline)
    print(f"cities: {len(geo['cities'])} | outline rings: {len(outline)} ({pts} pts) "
          f"| gold Edmonton 2025 debt_utilization: {ed25}")
    print(f"medians cross-checked against mart for {len(MAP_METRICS)} metrics x {len(YEARS)} years")
    print(f"wrote {CURATED / 'alberta_geo.json'} and {DASHBOARD / 'geo.js'}")


if __name__ == "__main__":
    main()
