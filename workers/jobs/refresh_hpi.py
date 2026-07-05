"""Quarterly: download the FHFA state House Price Index CSV (no key needed) and
upsert into market_hpi. Implemented in M2 — see docs/ROADMAP.md.

Run: backend/.venv/Scripts/python.exe -m workers.jobs.refresh_hpi
"""

import sys


def main() -> int:
    print("refresh_hpi: not implemented until M2 (FHFA HPI ingest)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
