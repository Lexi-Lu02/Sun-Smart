#!/usr/bin/env python3
"""
Parse australian-postcodes.sql and output a JSON lookup by postcode.
Each postcode maps to the first valid (lat, lng) found (skips 0,0).
"""
import re
import json
from pathlib import Path

# Paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_PATH = PROJECT_ROOT / "data" / "reference" / "australian-postcodes.sql"
OUT_PATH = PROJECT_ROOT / "frontend" / "data" / "postcodes.json"

# Match: ('postcode', 'suburb', 'state', lat, lng),
ROW_RE = re.compile(
    r"\s*\('(\d+)',\s*'([^']*(?:''[^']*)*)',\s*'([A-Z]{2,4})',\s*(-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)"
)


def main():
    sql_text = SQL_PATH.read_text(encoding="utf-8", errors="replace")
    seen = {}
    for m in ROW_RE.finditer(sql_text):
        postcode, suburb, state, lat_s, lng_s = m.groups()
        lat, lng = float(lat_s), float(lng_s)
        # Skip invalid coordinates (0,0 or missing data)
        if (lat, lng) == (0.0, 0.0):
            continue
        if postcode not in seen:
            # Unescape SQL suburb ('' -> ')
            suburb_clean = suburb.replace("''", "'")
            seen[postcode] = {
                "postcode": postcode,
                "suburb": suburb_clean,
                "state": state,
                "latitude": round(lat, 3),
                "longitude": round(lng, 3),
            }
    out_list = list(seen.values())
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out_list, indent=0), encoding="utf-8")
    print(f"Wrote {len(out_list)} postcodes to {OUT_PATH}")


if __name__ == "__main__":
    main()
