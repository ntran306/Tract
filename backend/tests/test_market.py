from datetime import date
from decimal import Decimal

from app.models import MarketHPI
from app.services.market_data import (
    estimate_value,
    hpi_at,
    latest_hpi,
    parse_hpi_csv,
    quarter_start,
)

PROPS = "/api/v1/properties"
MARKET = "/api/v1/market"

CSV = (
    "hpi_type,hpi_flavor,frequency,level,place_name,place_id,yr,period,index_nsa,index_sa,H\n"
    '"traditional","all-transactions","quarterly","State","Georgia","GA",2020,2,300.00,,""\n'
    '"traditional","all-transactions","quarterly","State","Georgia","GA",2026,1,375.00,,""\n'
    '"non-metro","all-transactions","quarterly","State","Georgia","GA",2026,1,999.00,,""\n'
    '"traditional","purchase-only","quarterly","State","Georgia","GA",2026,1,111.00,,""\n'
    '"traditional","all-transactions","quarterly","MSA","Atlanta","12060",2026,1,222.00,,""\n'
)


def test_parse_hpi_filters_to_state_all_transactions():
    rows = parse_hpi_csv(CSV)
    # only the two 'traditional/all-transactions/State' GA rows survive
    assert len(rows) == 2
    assert {r["region_code"] for r in rows} == {"GA"}
    assert all(r["level"] == "state" for r in rows)
    q1 = next(r for r in rows if r["period"] == date(2026, 1, 1))
    assert q1["index_value"] == Decimal("375.00")


def test_quarter_start():
    assert quarter_start(date(2024, 5, 17)) == date(2024, 4, 1)
    assert quarter_start(date(2024, 1, 1)) == date(2024, 1, 1)
    assert quarter_start(date(2024, 12, 31)) == date(2024, 10, 1)


def _seed_ga(db):
    db.add(MarketHPI(level="state", region_code="GA", region_name="Georgia",
                     period=date(2020, 4, 1), index_value=Decimal("300.00")))
    db.add(MarketHPI(level="state", region_code="GA", region_name="Georgia",
                     period=date(2026, 1, 1), index_value=Decimal("375.00")))
    db.commit()


def test_estimate_value_math(client, db, user):
    # property purchased Q2 2020 for 300k -> latest index 375/300 = 1.25 -> 375k
    _seed_ga(db)
    from app.models import Property, PropertyKind
    p = Property(owner_id=user.id, kind=PropertyKind.rental, nickname="X",
                 state="GA", purchase_price=Decimal("300000"), purchase_date=date(2020, 5, 1))
    db.add(p)
    db.commit()
    assert estimate_value(db, p) == Decimal("375000")


def test_estimate_rounds_to_thousand(client, db, user):
    _seed_ga(db)
    from app.models import Property, PropertyKind
    p = Property(owner_id=user.id, kind=PropertyKind.rental, nickname="X",
                 state="GA", purchase_price=Decimal("287500"), purchase_date=date(2020, 5, 1))
    db.add(p)
    db.commit()
    # 287500 * 1.25 = 359375 -> rounds to 359000
    assert estimate_value(db, p) == Decimal("359000")


def test_estimate_none_without_state(db, user):
    _seed_ga(db)
    from app.models import Property, PropertyKind
    p = Property(owner_id=user.id, kind=PropertyKind.rental, nickname="X",
                 purchase_price=Decimal("300000"), purchase_date=date(2020, 5, 1))
    db.add(p)
    db.commit()
    assert estimate_value(db, p) is None


def test_hpi_estimate_endpoint(client, db):
    _seed_ga(db)
    pid = client.post(PROPS, json={
        "kind": "rental", "nickname": "Maple", "state": "GA",
        "purchase_price": "300000.00", "purchase_date": "2020-05-01",
    }).json()["id"]
    res = client.post(f"{PROPS}/{pid}/hpi-estimate")
    assert res.status_code == 201
    assert res.json()["source"] == "hpi_estimate"
    assert res.json()["value"] == "375000.00"
    # becomes the property's latest value
    assert client.get(f"{PROPS}/{pid}").json()["latest_value"] == "375000.00"


def test_hpi_estimate_endpoint_422_without_data(client):
    pid = client.post(PROPS, json={"kind": "rental", "nickname": "No data", "state": "GA",
                                    "purchase_price": "300000.00", "purchase_date": "2020-05-01"}).json()["id"]
    # no HPI rows seeded -> 422
    assert client.post(f"{PROPS}/{pid}/hpi-estimate").status_code == 422


def test_hpi_helpers(db):
    _seed_ga(db)
    assert latest_hpi(db, "GA").index_value == Decimal("375.00")
    assert hpi_at(db, "GA", date(2020, 5, 1)).index_value == Decimal("300.00")
    # a date before all data falls back to earliest
    assert hpi_at(db, "GA", date(2000, 1, 1)).index_value == Decimal("300.00")


def test_market_hpi_endpoint(client, db):
    _seed_ga(db)
    res = client.get(f"{MARKET}/hpi?state=GA")
    assert res.status_code == 200
    body = res.json()
    assert body["state"] == "GA"
    assert body["latest_index"] == "375.00"
    assert len(body["points"]) == 2


def test_market_hpi_404_unknown_state(client):
    assert client.get(f"{MARKET}/hpi?state=ZZ").status_code == 404
