import enum

from sqlalchemy import Enum as SAEnum


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class PropertyKind(str, enum.Enum):
    my_home = "my_home"
    rental = "rental"
    airbnb = "airbnb"
    flip = "flip"
    other = "other"


class PropertyStatus(str, enum.Enum):
    active = "active"
    sold = "sold"
    archived = "archived"


class TxnKind(str, enum.Enum):
    income = "income"
    expense = "expense"


class TxnCategory(str, enum.Enum):
    # income
    rent = "rent"
    airbnb_payout = "airbnb_payout"
    other_income = "other_income"
    # expenses
    mortgage = "mortgage"
    property_tax = "property_tax"
    insurance = "insurance"
    hoa = "hoa"
    utilities = "utilities"
    repairs = "repairs"
    maintenance = "maintenance"
    cleaning = "cleaning"
    management_fee = "management_fee"
    renovation = "renovation"
    listing_fee = "listing_fee"
    other_expense = "other_expense"


class ValuationSource(str, enum.Enum):
    manual = "manual"
    purchase_price = "purchase_price"
    hpi_estimate = "hpi_estimate"
    rentcast = "rentcast"


class ConversationKind(str, enum.Enum):
    dm = "dm"
    agent = "agent"
    inquiry = "inquiry"


class SenderType(str, enum.Enum):
    user = "user"
    agent = "agent"
    system = "system"


class ListingStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    closed = "closed"


class NotificationKind(str, enum.Enum):
    message = "message"
    system = "system"
    digest = "digest"


def db_enum(py_enum: type[enum.Enum], name: str) -> SAEnum:
    """Postgres enum column type storing enum *values* (lowercase), matching the
    hand-written migrations. Types themselves are created in migration 001."""
    return SAEnum(py_enum, name=name, values_callable=lambda e: [m.value for m in e])
