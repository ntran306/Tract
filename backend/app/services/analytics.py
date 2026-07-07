"""All money math lives here — formulas and display rules follow
.claude/skills/real-estate-finance. Routers call this; nothing else computes."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Profile, Property, PropertyStatus, PropertyValuation, Transaction, TxnKind
from app.schemas.analytics import MonthCashFlow, PortfolioSummary, PropertyRow

ZERO = Decimal("0.00")


def latest_valuations(
    db: Session, property_ids: list[uuid.UUID]
) -> dict[uuid.UUID, PropertyValuation]:
    """Newest valuation per property (by valued_at, then created_at)."""
    if not property_ids:
        return {}
    rows = db.execute(
        select(PropertyValuation)
        .where(PropertyValuation.property_id.in_(property_ids))
        .order_by(
            PropertyValuation.property_id,
            PropertyValuation.valued_at.desc(),
            PropertyValuation.created_at.desc(),
        )
    ).scalars()
    latest: dict[uuid.UUID, PropertyValuation] = {}
    for v in rows:
        latest.setdefault(v.property_id, v)
    return latest


def _month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def _last_12_months(today: date) -> list[str]:
    keys = []
    year, month = today.year, today.month
    for _ in range(12):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return list(reversed(keys))


def portfolio_summary(db: Session, user: Profile, today: date | None = None) -> PortfolioSummary:
    today = today or date.today()
    months = _last_12_months(today)
    current = months[-1]

    props = list(
        db.execute(
            select(Property).where(
                Property.owner_id == user.id, Property.status == PropertyStatus.active
            )
        ).scalars()
    )
    prop_ids = [p.id for p in props]
    latest = latest_valuations(db, prop_ids)

    window_start = date(int(months[0][:4]), int(months[0][5:]), 1)
    txns = list(
        db.execute(
            select(Transaction).where(
                Transaction.property_id.in_(prop_ids) if prop_ids else False,
                Transaction.occurred_on >= window_start,
                Transaction.occurred_on <= today,
            )
        ).scalars()
    )

    income_by_month: dict[str, Decimal] = {m: ZERO for m in months}
    expense_by_month: dict[str, Decimal] = {m: ZERO for m in months}
    net_current_by_prop: dict[uuid.UUID, Decimal] = {pid: ZERO for pid in prop_ids}

    for t in txns:
        key = _month_key(t.occurred_on)
        if key not in income_by_month:
            continue
        if t.kind == TxnKind.income:
            income_by_month[key] += t.amount
            if key == current:
                net_current_by_prop[t.property_id] += t.amount
        else:
            expense_by_month[key] += t.amount
            if key == current:
                net_current_by_prop[t.property_id] -= t.amount

    series = [
        MonthCashFlow(
            month=m,
            income=income_by_month[m],
            expense=expense_by_month[m],
            net=income_by_month[m] - expense_by_month[m],
        )
        for m in months
    ]

    valued = [p for p in props if p.id in latest]
    total_value = sum((latest[p.id].value for p in valued), ZERO) if valued else None
    # Equity estimate: missing loan_balance counts as 0 (owned outright) — it's an
    # estimate over manual inputs and is labeled as such in the UI.
    total_equity = (
        sum((latest[p.id].value - (p.loan_balance or ZERO) for p in valued), ZERO)
        if valued
        else None
    )

    rows = [
        PropertyRow(
            id=p.id,
            nickname=p.nickname,
            kind=p.kind,
            value=latest[p.id].value if p.id in latest else None,
            value_source=latest[p.id].source if p.id in latest else None,
            cash_flow_month=net_current_by_prop[p.id],
        )
        for p in props
    ]
    rows.sort(key=lambda r: (r.value is None, -(r.value or ZERO)))

    return PortfolioSummary(
        property_count=len(props),
        valued_count=len(valued),
        total_value=total_value,
        total_equity=total_equity,
        income_month=income_by_month[current],
        expense_month=expense_by_month[current],
        cash_flow_month=income_by_month[current] - expense_by_month[current],
        series=series,
        properties=rows,
    )
