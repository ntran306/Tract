import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import TxnCategory, TxnKind, ValuationSource, db_enum


class PropertyValuation(Base):
    """Append-only value history; 'current value' = latest row per property."""

    __tablename__ = "property_valuations"
    __table_args__ = (
        Index("ix_property_valuations_property_valued", "property_id", "valued_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE")
    )
    source: Mapped[ValuationSource] = mapped_column(
        db_enum(ValuationSource, "valuation_source")
    )
    value: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    valued_at: Mapped[date] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Transaction(Base):
    """Every dollar in or out. Amounts are positive; direction comes from kind."""

    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="transactions_amount_positive"),
        Index("ix_transactions_property_occurred", "property_id", "occurred_on"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE")
    )
    kind: Mapped[TxnKind] = mapped_column(db_enum(TxnKind, "txn_kind"))
    category: Mapped[TxnCategory] = mapped_column(db_enum(TxnCategory, "txn_category"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    occurred_on: Mapped[date] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
