import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import PropertyKind, PropertyStatus, db_enum


class Property(Base):
    __tablename__ = "properties"
    __table_args__ = (Index("ix_properties_owner_kind", "owner_id", "kind"),)

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE")
    )
    kind: Mapped[PropertyKind] = mapped_column(db_enum(PropertyKind, "property_kind"))
    status: Mapped[PropertyStatus] = mapped_column(
        db_enum(PropertyStatus, "property_status"),
        default=PropertyStatus.active,
        server_default="active",
    )
    nickname: Mapped[str] = mapped_column(Text)
    address_line1: Mapped[str | None] = mapped_column(Text)
    address_line2: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str | None] = mapped_column(String(2))
    zip_code: Mapped[str | None] = mapped_column("zip", Text)
    beds: Mapped[int | None] = mapped_column(SmallInteger)
    baths: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    sqft: Mapped[int | None] = mapped_column(Integer)
    year_built: Mapped[int | None] = mapped_column(SmallInteger)
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    purchase_date: Mapped[date | None] = mapped_column(Date)
    sold_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    sold_date: Mapped[date | None] = mapped_column(Date)
    # manual loan fields -> equity / refi analytics (all optional)
    loan_balance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    interest_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))  # 6.875 = 6.875%
    monthly_payment: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    down_payment: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Lease(Base):
    __tablename__ = "leases"
    __table_args__ = (
        Index("ix_leases_property_active", "property_id", postgresql_where=text("is_active")),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE")
    )
    tenant_name: Mapped[str] = mapped_column(Text)
    tenant_email: Mapped[str | None] = mapped_column(Text)
    tenant_phone: Mapped[str | None] = mapped_column(Text)
    rent: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    deposit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    notes: Mapped[str | None] = mapped_column(Text)
