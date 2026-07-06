import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, SmallInteger, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class MarketFMR(Base):
    """HUD Fair Market Rents — refreshed yearly by workers/jobs/refresh_fmr.py."""

    __tablename__ = "market_fmr"
    __table_args__ = (UniqueConstraint("year", "area_code", "bedrooms"),)

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    year: Mapped[int] = mapped_column(SmallInteger)
    area_code: Mapped[str] = mapped_column(Text)  # HUD area / county FIPS
    area_name: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(2))
    bedrooms: Mapped[int] = mapped_column(SmallInteger)  # 0-4
    rent: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class MarketHPI(Base):
    """FHFA House Price Index — refreshed quarterly by workers/jobs/refresh_hpi.py."""

    __tablename__ = "market_hpi"
    __table_args__ = (UniqueConstraint("level", "region_code", "period"),)

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    level: Mapped[str] = mapped_column(Text)  # 'state' | 'msa'
    region_code: Mapped[str] = mapped_column(Text)
    region_name: Mapped[str] = mapped_column(Text)
    period: Mapped[date] = mapped_column(Date)  # quarter start
    index_value: Mapped[Decimal] = mapped_column(Numeric(10, 2))
