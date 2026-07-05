import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Date, ForeignKey, Numeric, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import ListingStatus, db_enum


class Listing(Base):
    """v1.5 marketplace — schema exists now, no UI until then."""

    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE")
    )
    status: Mapped[ListingStatus] = mapped_column(
        db_enum(ListingStatus, "listing_status"),
        default=ListingStatus.draft,
        server_default="draft",
    )
    headline: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    rent_asked: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    available_from: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
