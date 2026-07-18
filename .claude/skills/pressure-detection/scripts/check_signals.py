"""Pressure-detection code check. Exit 0 = signals.json obeys the governance rules."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SIG = ROOT / "data" / "curated" / "signals.json"

BANNED = ("caused", "because of", "should raise", "should cut", "must borrow",
          "healthy", "unhealthy", "recommend", "forecast", "will grow")

def fail(msg):
    print(f"FAIL  {msg}")
    fail.count += 1
fail.count = 0

def main():
    if not SIG.exists():
        print("FAIL  signals.json not found — run pipeline/detect_signals.py first")
        return 2
    with open(SIG, encoding="utf-8") as f:
        sig = json.load(f)

    if len(sig["signals"]) > 3:
        fail(f"{len(sig['signals'])} signals shown — maximum is three")
    if not str(sig.get("rules_version", "")).startswith("1.2"):
        fail(f"unexpected rules version: {sig.get('rules_version')}")

    # v1.1: truncated signals must carry full evidence and their status
    for t in sig.get("truncated_signals", []):
        if not t.get("tests") or not t.get("status") or not t.get("history"):
            fail(f"truncated signal {t.get('metric_id')} lacks full evidence (tests/status/history)")

    # v1.2: Not-flagged verdicts publish full evidence too
    for t in sig.get("not_flagged", []):
        if not t.get("tests") or not t.get("history"):
            fail(f"not-flagged metric {t.get('metric_id')} lacks verifiable test evidence")
        for x in t["tests"]:
            if x["test_id"] != "CX-1" and x.get("triggered"):
                fail(f"not-flagged metric {t.get('metric_id')} has a triggered core test")

    for s in sig["signals"]:
        mid = s["metric_id"]
        core = [t for t in s["tests"]
                if t["test_id"] in ("EH-1", "EH-2", "PP-1", "CR-1") and t["triggered"]]
        hist = [t for t in core if t.get("family") == "historical"]
        if s["status"] == "High review priority":
            if len(core) < 2:
                fail(f"{mid}: High with fewer than two core tests")
            if not hist:
                fail(f"{mid}: High without an Edmonton historical test")
        if not core and s["status"] == "High review priority":
            fail(f"{mid}: High from context evidence alone")
        if not s.get("explanation"):
            fail(f"{mid}: signal without explanation")
        low = s.get("explanation", "").lower()
        for w in BANNED:
            if w in low:
                fail(f"{mid}: explanation contains banned language {w!r}")
        for t in s["tests"]:
            if t["test_id"] == "CX-1" and not t.get("supporting_only"):
                fail(f"{mid}: CX-1 not marked supporting_only")
        if not s.get("history"):
            fail(f"{mid}: no Edmonton historical series attached")

    if "truncated_signals" not in sig or "not_flagged" not in sig:
        fail("truncation / not-flagged disclosure missing")
    if "provisional" not in sig.get("coverage_note", "").lower() and \
       "306 of 332" not in sig.get("coverage_note", ""):
        fail("coverage note missing provisional disclosure")
    if "not policy recommendations" not in sig.get("disclaimer", ""):
        fail("disclaimer missing no-policy-recommendation statement")

    if fail.count:
        print(f"\n{fail.count} check(s) failed — signals must not be presented until fixed.")
        return 1
    print(f"OK  {len(sig['signals'])} signals obey rules {sig['rules_version']} "
          f"({len(sig['truncated_signals'])} truncated disclosed, "
          f"{len(sig['not_flagged'])} not flagged).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
