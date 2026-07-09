"""Quarterly: download the FHFA state House Price Index (free, no key) and upsert
into market_hpi. Powers index-based value estimates.

Run: backend/.venv/Scripts/python.exe -m workers.jobs.refresh_hpi
"""

import sys

import httpx

from app.db import SessionLocal
from app.services.market_data import FHFA_HPI_URL, parse_hpi_csv, upsert_hpi


def main() -> int:
    print(f"refresh_hpi: downloading {FHFA_HPI_URL}")
    resp = httpx.get(FHFA_HPI_URL, timeout=120, follow_redirects=True)
    resp.raise_for_status()
    rows = parse_hpi_csv(resp.text)
    if not rows:
        print("refresh_hpi: no state rows parsed — CSV format may have changed")
        return 1
    db = SessionLocal()
    try:
        n = upsert_hpi(db, rows)
    finally:
        db.close()
    states = len({r["region_code"] for r in rows})
    latest = max(r["period"] for r in rows)
    print(f"refresh_hpi: upserted {n} rows across {states} states, latest quarter {latest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
