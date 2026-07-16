# -*- coding: utf-8 -*-
"""
Geometrisk — Find Your Line: data check.

Run before committing an edit to data/industry_losses.json. Catches the mistakes
that would break the tool: bad JSON, missing fields, non-number costs, empty
loss lists, duplicate ids. Exits non-zero on any error so it can gate a commit.

    python scripts/validate_data.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_IN = os.path.join(ROOT, "data", "industry_losses.json")

def main():
    errs, warns = [], []
    try:
        data = json.load(open(JSON_IN, encoding="utf-8"))
    except Exception as e:
        print(f"FAIL — industry_losses.json is not valid JSON: {e}")
        sys.exit(1)

    if not isinstance(data, list) or not data:
        print("FAIL — expected a non-empty list of industries."); sys.exit(1)

    seen = set()
    for i, d in enumerate(data):
        tag = d.get("id", f"#{i}")
        for field in ("id", "label", "division", "small", "large"):
            if field not in d:
                errs.append(f"{tag}: missing '{field}'")
        if d.get("id") in seen:
            errs.append(f"{tag}: duplicate id")
        seen.add(d.get("id"))
        if "keywords" not in d:
            warns.append(f"{tag}: no keywords (harder to find in the type-ahead)")
        for band in ("small", "large"):
            rows = d.get(band, [])
            if not rows:
                errs.append(f"{tag}: '{band}' has no losses")
            for r in rows:
                if not (isinstance(r, list) and len(r) >= 2):
                    errs.append(f"{tag}/{band}: a loss row is not [text, cost, peril]"); continue
                if not r[0] or not str(r[0]).strip():
                    errs.append(f"{tag}/{band}: a loss has no text")
                if not isinstance(r[1], (int, float)):
                    errs.append(f"{tag}/{band}: cost '{r[1]}' is not a number")

    for w in warns:
        print("warn —", w)
    if errs:
        print(f"\nFAIL — {len(errs)} error(s):")
        for e in errs:
            print("  •", e)
        sys.exit(1)
    rows = sum(len(d["small"]) + len(d["large"]) for d in data)
    print(f"OK — {len(data)} industries, {rows} loss rows, no errors.")

if __name__ == "__main__":
    main()
