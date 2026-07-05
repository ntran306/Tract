"""Yearly: pull HUD Fair Market Rents (free HUD_API_TOKEN) and upsert into
market_fmr. Implemented in M2 — see docs/ROADMAP.md.

Run: backend/.venv/Scripts/python.exe -m workers.jobs.refresh_fmr
"""

import sys


def main() -> int:
    print("refresh_fmr: not implemented until M2 (HUD FMR ingest)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
