import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PropertyKind, PropertyStatus, ValuationSource

MONEY = Field(default=None, gt=0, le=Decimal("9999999999.99"))


class PropertyBase(BaseModel):
    nickname: str = Field(min_length=1, max_length=120)
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = Field(default=None, min_length=2, max_length=2)
    zip_code: str | None = Field(default=None, max_length=10)
    beds: int | None = Field(default=None, ge=0, le=100)
    baths: Decimal | None = Field(default=None, ge=0, le=Decimal("99.5"))
    sqft: int | None = Field(default=None, gt=0)
    year_built: int | None = Field(default=None, ge=1600, le=2100)
    purchase_price: Decimal | None = MONEY
    purchase_date: date | None = None
    sold_price: Decimal | None = MONEY
    sold_date: date | None = None
    loan_balance: Decimal | None = MONEY
    interest_rate: Decimal | None = Field(default=None, ge=0, le=25)
    monthly_payment: Decimal | None = MONEY
    down_payment: Decimal | None = MONEY
    notes: str | None = None


class PropertyCreate(PropertyBase):
    kind: PropertyKind


class PropertyUpdate(PropertyBase):
    # Everything optional; kind is intentionally immutable after creation
    # (analytics semantics differ per kind) — archive and recreate instead.
    nickname: str | None = Field(default=None, min_length=1, max_length=120)
    status: PropertyStatus | None = None


class PropertyImageRead(BaseModel):
    id: uuid.UUID
    url: str  # public URL, built by the router from SUPABASE_URL + storage_path


class ImageAttach(BaseModel):
    storage_path: str = Field(min_length=1, max_length=400)


class PropertyRead(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: PropertyKind
    status: PropertyStatus
    created_at: datetime
    # Latest valuation, attached by the router so the Owned grid needs one call
    latest_value: Decimal | None = None
    latest_value_source: ValuationSource | None = None
    images: list[PropertyImageRead] = []


class ValuationCreate(BaseModel):
    value: Decimal = Field(gt=0, le=Decimal("9999999999.99"))
    valued_at: date
    note: str | None = None


class ValuationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: ValuationSource
    value: Decimal
    valued_at: date
    note: str | None
    created_at: datetime


class LeaseUpsert(BaseModel):
    tenant_name: str = Field(min_length=1, max_length=200)
    tenant_email: str | None = None
    tenant_phone: str | None = None
    rent: Decimal = Field(gt=0, le=Decimal("9999999999.99"))
    deposit: Decimal | None = Field(default=None, ge=0)
    start_date: date
    end_date: date | None = None
    notes: str | None = None


class LeaseRead(LeaseUpsert):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
