"""Seed three demo accounts with realistic dummy data for prototyping.

Creates (or reuses) the auth users via Supabase Auth signup, then wipes and
reseeds their properties directly in the DB. Idempotent: safe to re-run.

Run from backend/ with the venv:
    ./.venv/Scripts/python.exe -m scripts.seed_demo

Requires email confirmation to be OFF on the Supabase project (it is, for dev).
Reads the anon key from ../frontend/.env.local.
"""

from __future__ import annotations

import random
import sys
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

import httpx
from sqlalchemy import text

from app.core.config import get_settings
from app.db import SessionLocal
from app.models import (
    Lease,
    Property,
    PropertyKind,
    PropertyValuation,
    Transaction,
    TxnCategory,
    TxnKind,
    ValuationSource,
)

PASSWORD = "demo-tract-2026"

DEMO_USERS = [
    ("nathangsu306+alex@gmail.com", "Alex Rivera (portfolio)"),
    ("nathangsu306+sam@gmail.com", "Sam Chen (landlord + renter)"),
    ("nathangsu306+jordan@gmail.com", "Jordan Lee (homeowner)"),
]


def _anon_key() -> str:
    env = Path(__file__).resolve().parents[2] / "frontend" / ".env.local"
    for line in env.read_text().splitlines():
        if line.startswith("VITE_SUPABASE_ANON_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("Could not find VITE_SUPABASE_ANON_KEY in frontend/.env.local")


def _ensure_user(base_url: str, anon_key: str, email: str, name: str) -> None:
    """Sign up the user (ignore 'already registered')."""
    httpx.post(
        f"{base_url}/auth/v1/signup",
        headers={"apikey": anon_key, "Content-Type": "application/json"},
        json={"email": email, "password": PASSWORD, "data": {"display_name": name}},
        timeout=30,
    )


def _months_ago(n: int) -> date:
    today = date.today()
    y, m = today.year, today.month - n
    while m <= 0:
        m += 12
        y -= 1
    return date(y, m, 1)


def _val(prop: Property, value: str, when: date, source=ValuationSource.manual) -> PropertyValuation:
    return PropertyValuation(
        property_id=prop.id, source=source, value=Decimal(value), valued_at=when
    )


def _txn(prop: Property, kind: TxnKind, cat: TxnCategory, amount: str, when: date, desc=None):
    return Transaction(
        property_id=prop.id, kind=kind, category=cat, amount=Decimal(amount),
        occurred_on=when, description=desc,
    )


def _monthly_expenses(db, prop: Property, specs: list[tuple[TxnCategory, str]], months: int):
    """Add a recurring-looking expense in each of the last `months` months."""
    for n in range(months):
        when = _months_ago(n)
        for cat, amount in specs:
            db.add(_txn(prop, TxnKind.expense, cat, amount, when.replace(day=5)))


def seed_alex(db, owner_id: uuid.UUID) -> None:
    """Power user: 5 properties across kinds, months of history."""
    # Rental 1
    r1 = Property(owner_id=owner_id, kind=PropertyKind.rental, nickname="Maple St duplex",
                  address_line1="812 Maple St", city="Atlanta", state="GA", zip_code="30312",
                  beds=4, baths=Decimal("3.0"), sqft=2100, purchase_price=Decimal("310000"),
                  purchase_date=date(2022, 5, 1), loan_balance=Decimal("240000"),
                  monthly_payment=Decimal("1850"), down_payment=Decimal("62000"),
                  interest_rate=Decimal("5.750"))
    # Rental 2
    r2 = Property(owner_id=owner_id, kind=PropertyKind.rental, nickname="Oak Ave bungalow",
                  address_line1="47 Oak Ave", city="Decatur", state="GA", zip_code="30030",
                  beds=3, baths=Decimal("2.0"), sqft=1500, purchase_price=Decimal("265000"),
                  purchase_date=date(2023, 2, 15), loan_balance=Decimal("205000"),
                  monthly_payment=Decimal("1580"), down_payment=Decimal("53000"),
                  interest_rate=Decimal("6.250"))
    # Airbnb
    ab = Property(owner_id=owner_id, kind=PropertyKind.airbnb, nickname="Blue Ridge cabin",
                  address_line1="9 Ridgeline Dr", city="Blue Ridge", state="GA", zip_code="30513",
                  beds=2, baths=Decimal("2.0"), sqft=1200, purchase_price=Decimal("340000"),
                  purchase_date=date(2021, 9, 1), loan_balance=Decimal("250000"),
                  monthly_payment=Decimal("1990"), down_payment=Decimal("85000"))
    # Flip
    fl = Property(owner_id=owner_id, kind=PropertyKind.flip, nickname="Pine St flip",
                  address_line1="220 Pine St", city="East Point", state="GA", zip_code="30344",
                  beds=3, baths=Decimal("1.0"), sqft=1350, purchase_price=Decimal("155000"),
                  purchase_date=date(2026, 1, 10))
    # My Home
    hm = Property(owner_id=owner_id, kind=PropertyKind.my_home, nickname="Our house",
                  address_line1="15 Elmwood Ct", city="Atlanta", state="GA", zip_code="30307",
                  beds=4, baths=Decimal("2.5"), sqft=2600, purchase_price=Decimal("520000"),
                  purchase_date=date(2020, 6, 1), loan_balance=Decimal("360000"),
                  monthly_payment=Decimal("2650"), down_payment=Decimal("104000"))
    for p in (r1, r2, ab, fl, hm):
        db.add(p)
    db.flush()

    # valuations
    db.add(_val(r1, "310000", date(2022, 5, 1), ValuationSource.purchase_price))
    db.add(_val(r1, "355000", _months_ago(6)))
    db.add(_val(r1, "372000", _months_ago(1)))
    db.add(_val(r2, "265000", date(2023, 2, 15), ValuationSource.purchase_price))
    db.add(_val(r2, "289000", _months_ago(2)))
    db.add(_val(ab, "340000", date(2021, 9, 1), ValuationSource.purchase_price))
    db.add(_val(ab, "398000", _months_ago(1)))
    db.add(_val(fl, "155000", date(2026, 1, 10), ValuationSource.purchase_price))
    db.add(_val(fl, "225000", _months_ago(0)))  # ARV estimate
    db.add(_val(hm, "520000", date(2020, 6, 1), ValuationSource.purchase_price))
    db.add(_val(hm, "610000", _months_ago(1)))

    # leases on rentals
    db.add(Lease(property_id=r1.id, tenant_name="Priya Nair", tenant_email="priya@example.com",
                 rent=Decimal("2400"), deposit=Decimal("2400"), start_date=date(2024, 8, 1),
                 is_active=True))
    db.add(Lease(property_id=r2.id, tenant_name="Marcus Bell", rent=Decimal("1950"),
                 deposit=Decimal("1950"), start_date=date(2025, 1, 1), is_active=True))

    # 8 months of activity
    for n in range(8):
        when = _months_ago(n)
        db.add(_txn(r1, TxnKind.income, TxnCategory.rent, "2400", when.replace(day=1), "Monthly rent"))
        db.add(_txn(r2, TxnKind.income, TxnCategory.rent, "1950", when.replace(day=1), "Monthly rent"))
    _monthly_expenses(db, r1, [(TxnCategory.mortgage, "1850"), (TxnCategory.property_tax, "310"),
                               (TxnCategory.insurance, "120")], 8)
    _monthly_expenses(db, r2, [(TxnCategory.mortgage, "1580"), (TxnCategory.insurance, "95")], 8)
    db.add(_txn(r1, TxnKind.expense, TxnCategory.repairs, "480", _months_ago(2).replace(day=14), "Water heater"))
    db.add(_txn(r2, TxnKind.expense, TxnCategory.maintenance, "160", _months_ago(1).replace(day=9), "HVAC service"))

    # Airbnb: variable payouts + cleaning
    for n in range(6):
        when = _months_ago(n)
        payout = str(random.choice([2100, 2650, 3200, 1800, 2900]))
        db.add(_txn(ab, TxnKind.income, TxnCategory.airbnb_payout, payout, when.replace(day=2), "Airbnb payout"))
        db.add(_txn(ab, TxnKind.expense, TxnCategory.cleaning, "320", when.replace(day=3), "Turnover cleaning"))
    _monthly_expenses(db, ab, [(TxnCategory.mortgage, "1990"), (TxnCategory.utilities, "180")], 6)

    # Flip: renovation spend
    db.add(_txn(fl, TxnKind.expense, TxnCategory.renovation, "28000", date(2026, 2, 1), "Kitchen + baths"))
    db.add(_txn(fl, TxnKind.expense, TxnCategory.renovation, "14500", date(2026, 4, 1), "Roof + exterior"))
    db.add(_txn(fl, TxnKind.expense, TxnCategory.property_tax, "1200", _months_ago(1).replace(day=5)))

    # My Home: ownership costs
    _monthly_expenses(db, hm, [(TxnCategory.mortgage, "2650"), (TxnCategory.property_tax, "540"),
                               (TxnCategory.insurance, "160"), (TxnCategory.utilities, "290")], 8)


def seed_sam(db, owner_id: uuid.UUID) -> None:
    """Landlord who rents out one place and rents where they live."""
    rental = Property(owner_id=owner_id, kind=PropertyKind.rental, nickname="Cypress condo",
                      address_line1="600 Cypress Way #4B", city="Savannah", state="GA", zip_code="31401",
                      beds=2, baths=Decimal("2.0"), sqft=1050, purchase_price=Decimal("240000"),
                      purchase_date=date(2023, 7, 1), loan_balance=Decimal("192000"),
                      monthly_payment=Decimal("1490"), down_payment=Decimal("48000"),
                      interest_rate=Decimal("6.500"))
    # "Where they live, renting" — a my_home tracked as a rental situation
    home = Property(owner_id=owner_id, kind=PropertyKind.my_home, nickname="Apartment (renting)",
                    address_line1="88 Habersham St", city="Savannah", state="GA", zip_code="31405",
                    beds=1, baths=Decimal("1.0"), sqft=720)
    db.add(rental)
    db.add(home)
    db.flush()

    db.add(_val(rental, "240000", date(2023, 7, 1), ValuationSource.purchase_price))
    db.add(_val(rental, "258000", _months_ago(1)))

    db.add(Lease(property_id=rental.id, tenant_name="Dana Okafor", tenant_email="dana@example.com",
                 rent=Decimal("1750"), deposit=Decimal("1750"), start_date=date(2025, 3, 1),
                 is_active=True))

    for n in range(7):
        when = _months_ago(n)
        db.add(_txn(rental, TxnKind.income, TxnCategory.rent, "1750", when.replace(day=1), "Monthly rent"))
        db.add(_txn(home, TxnKind.expense, TxnCategory.rent, "1400", when.replace(day=1), "My rent"))
    _monthly_expenses(db, rental, [(TxnCategory.mortgage, "1490"), (TxnCategory.hoa, "260"),
                                   (TxnCategory.insurance, "70")], 7)
    db.add(_txn(rental, TxnKind.expense, TxnCategory.repairs, "220", _months_ago(3).replace(day=12), "Garbage disposal"))
    # Sam's utilities on their rented apartment
    _monthly_expenses(db, home, [(TxnCategory.utilities, "140")], 7)


def seed_jordan(db, owner_id: uuid.UUID) -> None:
    """Just owns their home, nothing else."""
    home = Property(owner_id=owner_id, kind=PropertyKind.my_home, nickname="Home",
                    address_line1="34 Larkspur Ln", city="Marietta", state="GA", zip_code="30064",
                    beds=3, baths=Decimal("2.0"), sqft=1850, purchase_price=Decimal("395000"),
                    purchase_date=date(2021, 11, 1), loan_balance=Decimal("312000"),
                    monthly_payment=Decimal("2180"), down_payment=Decimal("79000"),
                    interest_rate=Decimal("3.250"))
    db.add(home)
    db.flush()
    db.add(_val(home, "395000", date(2021, 11, 1), ValuationSource.purchase_price))
    db.add(_val(home, "452000", _months_ago(1)))
    _monthly_expenses(db, home, [(TxnCategory.mortgage, "2180"), (TxnCategory.property_tax, "410"),
                                 (TxnCategory.insurance, "135"), (TxnCategory.utilities, "240")], 8)
    db.add(_txn(home, TxnKind.expense, TxnCategory.maintenance, "350", _months_ago(2).replace(day=20), "Gutter cleaning + tune-up"))


def main() -> int:
    settings = get_settings()
    anon_key = _anon_key()
    base_url = settings.supabase_url.rstrip("/")

    for email, name in DEMO_USERS:
        _ensure_user(base_url, anon_key, email, name)

    db = SessionLocal()
    try:
        seeders = {
            "nathangsu306+alex@gmail.com": seed_alex,
            "nathangsu306+sam@gmail.com": seed_sam,
            "nathangsu306+jordan@gmail.com": seed_jordan,
        }
        for email, _name in DEMO_USERS:
            row = db.execute(
                text("select id from auth.users where email = :e"), {"e": email}
            ).first()
            if row is None:
                print(f"!! {email} not found in auth.users — signup may have failed")
                continue
            owner_id = row[0]
            # wipe existing properties (cascades valuations/txns/leases/images)
            existing = db.execute(
                text("select id from properties where owner_id = :o"), {"o": owner_id}
            ).all()
            for (pid,) in existing:
                db.execute(text("delete from properties where id = :p"), {"p": pid})
            db.flush()
            seeders[email](db, owner_id)
            db.commit()
            count = db.execute(
                text("select count(*) from properties where owner_id = :o"), {"o": owner_id}
            ).scalar()
            print(f"OK  {email}: {count} properties")
    finally:
        db.close()

    print("\nDemo accounts (password for all): " + PASSWORD)
    for email, name in DEMO_USERS:
        print(f"  {email}  — {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
