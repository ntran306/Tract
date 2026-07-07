import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import PropertyKind, ValuationSource


class MonthCashFlow(BaseModel):
    month: str  # "2026-07"
    income: Decimal
    expense: Decimal
    net: Decimal


class PropertyRow(BaseModel):
    id: uuid.UUID
    nickname: str
    kind: PropertyKind
    value: Decimal | None
    value_source: ValuationSource | None
    cash_flow_month: Decimal  # current calendar month net


class PortfolioSummary(BaseModel):
    property_count: int
    valued_count: int  # properties with any valuation — total_value covers only these
    total_value: Decimal | None
    total_equity: Decimal | None  # Σ(value − loan_balance‖0) over valued props; estimate
    income_month: Decimal
    expense_month: Decimal
    cash_flow_month: Decimal
    series: list[MonthCashFlow]  # last 12 calendar months, oldest first
    properties: list[PropertyRow]
