"""Yearly: pull HUD Fair Market Rents into market_fmr. Powers the "your rent vs
area FMR" benchmark. Requires HUD_API_TOKEN (free: huduser.gov FMR API).

Iterates all states via HUD's /fmr/statedata/{state} endpoint for the current
FMR year. No-ops with a clear message if the token isn't configured yet.

Run: backend/.venv/Scripts/python.exe -m workers.jobs.refresh_fmr
"""

import sys
from datetime import date

import httpx

from app.core.config import get_settings
from app.db import SessionLocal
from app.services.market_data import parse_fmr_statedata, upsert_fmr

HUD_BASE = "https://www.huduser.gov/hudapi/public/fmr"

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]


def main() -> int:
    token = get_settings().hud_api_token
    if not token:
        print("refresh_fmr: HUD_API_TOKEN not set — skipping. Get a free token at")
        print("            https://www.huduser.gov/portal/dataset/fmr-api.html")
        return 0

    year = date.today().year  # HUD serves the current FMR year
    headers = {"Authorization": f"Bearer {token}"}
    db = SessionLocal()
    total = 0
    try:
        with httpx.Client(timeout=60, headers=headers) as client:
            for st in STATES:
                resp = client.get(f"{HUD_BASE}/statedata/{st}?year={year}")
                if resp.status_code != 200:
                    print(f"  {st}: HTTP {resp.status_code} — skipped")
                    continue
                rows = parse_fmr_statedata(resp.json(), year)
                total += upsert_fmr(db, rows)
                print(f"  {st}: {len(rows)} rows")
    finally:
        db.close()
    print(f"refresh_fmr: upserted {total} FMR rows for {year}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
