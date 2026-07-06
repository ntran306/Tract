import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import TxnCategory, TxnKind

INCOME_CATEGORIES = {
    TxnCategory.rent,
    TxnCategory.airbnb_payout,
    TxnCategory.other_income,
}


def category_matches_kind(kind: TxnKind, category: TxnCategory) -> bool:
    return (category in INCOME_CATEGORIES) == (kind == TxnKind.income)


class TransactionCreate(BaseModel):
    property_id: uuid.UUID
    kind: TxnKind
    category: TxnCategory
    amount: Decimal = Field(gt=0, le=Decimal("9999999999.99"))
    occurred_on: date
    description: str | None = Field(default=None, max_length=500)
    is_recurring: bool = False

    @model_validator(mode="after")
    def _check_category(self):
        if not category_matches_kind(self.kind, self.category):
            raise ValueError(
                f"category '{self.category.value}' does not match kind '{self.kind.value}'"
            )
        return self


class TransactionUpdate(BaseModel):
    # kind+category must be updated together if either changes; router re-validates
    kind: TxnKind | None = None
    category: TxnCategory | None = None
    amount: Decimal | None = Field(default=None, gt=0, le=Decimal("9999999999.99"))
    occurred_on: date | None = None
    description: str | None = Field(default=None, max_length=500)
    is_recurring: bool | None = None


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    property_id: uuid.UUID
    kind: TxnKind
    category: TxnCategory
    amount: Decimal
    occurred_on: date
    description: str | None
    is_recurring: bool
    created_at: datetime
