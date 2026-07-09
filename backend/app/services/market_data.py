"""Free public housing data: FHFA House Price Index (value estimates) and HUD
Fair Market Rents (rent benchmarks). Parsing + lookups live here so the workers
stay thin and the math is unit-testable.

Estimate rules follow .claude/skills/real-estate-finance: HPI estimates round to
the nearest $1,000 and are always stored/labeled as source='hpi_estimate'.
"""

from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MarketFMR, MarketHPI, Property, PropertyValuation, ValuationSource

FHFA_HPI_URL = "https://fhfa.gov/hpi/download/monthly/hpi_master.csv"

# The state series we key value estimates off: broadest coverage, every state.
HPI_TYPE = "traditional"
HPI_FLAVOR = "all-transactions"
HPI_FREQ = "quarterly"


def quarter_start(d: date) -> date:
    """First day of the calendar quarter containing d."""
    return date(d.year, ((d.month - 1) // 3) * 3 + 1, 1)


# ---------------------------------------------------------------- FHFA HPI

def parse_hpi_csv(text: str) -> list[dict]:
    """State-level quarterly rows from the FHFA master CSV, as upsert dicts."""
    out: list[dict] = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        if (
            row.get("level") != "State"
            or row.get("hpi_type") != HPI_TYPE
            or row.get("hpi_flavor") != HPI_FLAVOR
            or row.get("frequency") != HPI_FREQ
        ):
            continue
        index_raw = (row.get("index_nsa") or "").strip()
        if not index_raw:
            continue
        try:
            yr = int(row["yr"])
            quarter = int(row["period"])
            index_value = Decimal(index_raw)
        except (ValueError, KeyError, ArithmeticError):
            continue
        out.append(
            {
                "level": "state",
                "region_code": row["place_id"].strip(),
                "region_name": row["place_name"].strip(),
                "period": date(yr, (quarter - 1) * 3 + 1, 1),
                "index_value": index_value,
            }
        )
    return out


def upsert_hpi(db: Session, rows: Iterable[dict]) -> int:
    """Insert/update market_hpi rows keyed on (level, region_code, period)."""
    existing = {
        (r.level, r.region_code, r.period): r
        for r in db.execute(select(MarketHPI).where(MarketHPI.level == "state")).scalars()
    }
    n = 0
    for row in rows:
        key = (row["level"], row["region_code"], row["period"])
        cur = existing.get(key)
        if cur is None:
            db.add(MarketHPI(**row))
        else:
            cur.index_value = row["index_value"]
            cur.region_name = row["region_name"]
        n += 1
    db.commit()
    return n


def latest_hpi(db: Session, state: str) -> MarketHPI | None:
    return db.execute(
        select(MarketHPI)
        .where(MarketHPI.level == "state", MarketHPI.region_code == state.upper())
        .order_by(MarketHPI.period.desc())
        .limit(1)
    ).scalar_one_or_none()


def hpi_at(db: Session, state: str, when: date) -> MarketHPI | None:
    """HPI row for the quarter containing `when`, else the nearest earlier one,
    else the earliest available."""
    target = quarter_start(when)
    row = db.execute(
        select(MarketHPI)
        .where(
            MarketHPI.level == "state",
            MarketHPI.region_code == state.upper(),
            MarketHPI.period <= target,
        )
        .order_by(MarketHPI.period.desc())
        .limit(1)
    ).scalar_one_or_none()
    if row is not None:
        return row
    return db.execute(
        select(MarketHPI)
        .where(MarketHPI.level == "state", MarketHPI.region_code == state.upper())
        .order_by(MarketHPI.period.asc())
        .limit(1)
    ).scalar_one_or_none()


def estimate_value(db: Session, prop: Property) -> Decimal | None:
    """purchase_price x (latest index / index at purchase), rounded to $1,000.
    Returns None when inputs or state HPI data are missing."""
    if prop.purchase_price is None or prop.purchase_date is None or not prop.state:
        return None
    latest = latest_hpi(db, prop.state)
    base = hpi_at(db, prop.state, prop.purchase_date)
    if latest is None or base is None or base.index_value == 0:
        return None
    raw = prop.purchase_price * (latest.index_value / base.index_value)
    return (raw / 1000).quantize(Decimal("1")) * 1000


def store_estimate(db: Session, prop: Property) -> PropertyValuation | None:
    """Compute an HPI estimate and record it as a valuation. Latest row wins in
    the UI regardless of source, so this never clobbers a newer manual value."""
    value = estimate_value(db, prop)
    if value is None:
        return None
    latest = latest_hpi(db, prop.state)
    val = PropertyValuation(
        property_id=prop.id,
        source=ValuationSource.hpi_estimate,
        value=value,
        valued_at=latest.period if latest else date.today(),
        note="FHFA index estimate",
    )
    db.add(val)
    db.commit()
    db.refresh(val)
    return val


# ---------------------------------------------------------------- HUD FMR

def fmr_for(db: Session, state: str, bedrooms: int, year: int | None = None) -> MarketFMR | None:
    """Latest-year Fair Market Rent for a state + bedroom count. bedrooms capped
    at 4 (HUD tops out at 4+). Needs the FMR worker to have run (HUD token)."""
    beds = max(0, min(4, bedrooms))
    q = select(MarketFMR).where(
        MarketFMR.state == state.upper(), MarketFMR.bedrooms == beds
    )
    if year is not None:
        q = q.where(MarketFMR.year == year)
    return db.execute(q.order_by(MarketFMR.year.desc()).limit(1)).scalar_one_or_none()


def parse_fmr_statedata(payload: dict, year: int) -> list[dict]:
    """Rows from HUD's /fmr/statedata/{state} response into upsert dicts.
    HUD returns per-area rows with Efficiency..'Four-Bedroom' fields."""
    beds_fields = [
        (0, "Efficiency"),
        (1, "One-Bedroom"),
        (2, "Two-Bedroom"),
        (3, "Three-Bedroom"),
        (4, "Four-Bedroom"),
    ]
    data = payload.get("data", {})
    state = data.get("state_code") or data.get("statecode") or ""
    out: list[dict] = []
    for area in data.get("data", []):
        code = area.get("code") or area.get("fips_code") or ""
        name = area.get("area_name") or area.get("metro_name") or code
        for beds, field in beds_fields:
            raw = area.get(field)
            if raw in (None, ""):
                continue
            try:
                rent = Decimal(str(raw))
            except ArithmeticError:
                continue
            out.append(
                {
                    "year": year,
                    "area_code": str(code),
                    "area_name": str(name),
                    "state": state.upper()[:2],
                    "bedrooms": beds,
                    "rent": rent,
                }
            )
    return out


def upsert_fmr(db: Session, rows: Iterable[dict]) -> int:
    existing = {
        (r.year, r.area_code, r.bedrooms): r
        for r in db.execute(select(MarketFMR)).scalars()
    }
    n = 0
    for row in rows:
        key = (row["year"], row["area_code"], row["bedrooms"])
        cur = existing.get(key)
        if cur is None:
            db.add(MarketFMR(**row))
        else:
            cur.rent = row["rent"]
            cur.area_name = row["area_name"]
        n += 1
    db.commit()
    return n
