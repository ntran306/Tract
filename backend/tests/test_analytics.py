from datetime import date

PROPS = "/api/v1/properties"
TXNS = "/api/v1/transactions"
PORTFOLIO = "/api/v1/analytics/portfolio"


def _month_start(d: date) -> str:
    return d.replace(day=1).isoformat()


def _prev_month_start(d: date) -> str:
    first = d.replace(day=1)
    prev_last_month = first.replace(year=first.year - 1, month=12) if first.month == 1 \
        else first.replace(month=first.month - 1)
    return prev_last_month.isoformat()


def seed(client):
    today = date.today()
    rental = client.post(PROPS, json={
        "kind": "rental", "nickname": "Maple St",
        "purchase_price": "300000.00", "purchase_date": "2024-03-01",
        "loan_balance": "100000.00",
    }).json()
    cabin = client.post(PROPS, json={"kind": "airbnb", "nickname": "Cabin"}).json()

    # current month: +1800 rent, -240.50 repairs on rental
    client.post(TXNS, json={
        "property_id": rental["id"], "kind": "income", "category": "rent",
        "amount": "1800.00", "occurred_on": _month_start(today),
    })
    client.post(TXNS, json={
        "property_id": rental["id"], "kind": "expense", "category": "repairs",
        "amount": "240.50", "occurred_on": _month_start(today),
    })
    # previous month: +1800 rent (series coverage, not current month)
    client.post(TXNS, json={
        "property_id": rental["id"], "kind": "income", "category": "rent",
        "amount": "1800.00", "occurred_on": _prev_month_start(today),
    })
    return rental, cabin


def test_portfolio_totals(client):
    seed(client)
    body = client.get(PORTFOLIO).json()

    assert body["property_count"] == 2
    assert body["valued_count"] == 1          # cabin has no valuation
    assert body["total_value"] == "300000.00"
    assert body["total_equity"] == "200000.00"  # 300000 - 100000 loan
    assert body["income_month"] == "1800.00"
    assert body["expense_month"] == "240.50"
    assert body["cash_flow_month"] == "1559.50"


def test_portfolio_series_shape(client):
    seed(client)
    body = client.get(PORTFOLIO).json()
    series = body["series"]

    assert len(series) == 12
    today = date.today()
    assert series[-1]["month"] == f"{today.year:04d}-{today.month:02d}"
    assert series[-1]["net"] == "1559.50"
    assert series[-2]["income"] == "1800.00"  # previous month rent
    # months are contiguous and oldest-first
    assert series[0]["month"] < series[-1]["month"]


def test_portfolio_property_rows(client):
    rental, cabin = seed(client)
    rows = client.get(PORTFOLIO).json()["properties"]

    assert len(rows) == 2
    assert rows[0]["id"] == rental["id"]          # valued first
    assert rows[0]["cash_flow_month"] == "1559.50"
    assert rows[0]["value_source"] == "purchase_price"
    assert rows[1]["id"] == cabin["id"]
    assert rows[1]["value"] is None
    assert rows[1]["cash_flow_month"] == "0.00"


def test_portfolio_empty(client):
    body = client.get(PORTFOLIO).json()
    assert body["property_count"] == 0
    assert body["total_value"] is None
    assert body["cash_flow_month"] == "0.00"
    assert len(body["series"]) == 12
