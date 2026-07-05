"""Initial schema: enums and all tables (docs/DATABASE.md).

Targets Supabase Postgres — profiles.id references auth.users(id).

Revision ID: 001
Revises:
Create Date: 2026-07-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ENUMS: dict[str, list[str]] = {
    "user_role": ["user", "admin"],
    "property_kind": ["my_home", "rental", "airbnb", "flip", "other"],
    "property_status": ["active", "sold", "archived"],
    "txn_kind": ["income", "expense"],
    "txn_category": [
        "rent", "airbnb_payout", "other_income",
        "mortgage", "property_tax", "insurance", "hoa", "utilities",
        "repairs", "maintenance", "cleaning", "management_fee",
        "renovation", "listing_fee", "other_expense",
    ],
    "valuation_source": ["manual", "purchase_price", "hpi_estimate", "rentcast"],
    "conversation_kind": ["dm", "agent", "inquiry"],
    "sender_type": ["user", "agent", "system"],
    "listing_status": ["draft", "active", "paused", "closed"],
    "notification_kind": ["message", "system", "digest"],
}


def _enum(name: str) -> postgresql.ENUM:
    return postgresql.ENUM(*ENUMS[name], name=name, create_type=False)


def upgrade() -> None:
    for name, values in ENUMS.items():
        quoted = ", ".join(f"'{v}'" for v in values)
        op.execute(f"create type {name} as enum ({quoted})")

    uuid_pk = lambda: sa.Column(  # noqa: E731
        "id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    now = sa.text("now()")

    op.create_table(
        "profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("avatar_url", sa.Text()),
        sa.Column("role", _enum("user_role"), nullable=False, server_default="user"),
        sa.Column("email_mirror", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("email_digest", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
    )
    op.execute(
        "alter table profiles add constraint profiles_id_fkey "
        "foreign key (id) references auth.users(id) on delete cascade"
    )

    op.create_table(
        "properties",
        uuid_pk(),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", _enum("property_kind"), nullable=False),
        sa.Column("status", _enum("property_status"), nullable=False, server_default="active"),
        sa.Column("nickname", sa.Text(), nullable=False),
        sa.Column("address_line1", sa.Text()),
        sa.Column("address_line2", sa.Text()),
        sa.Column("city", sa.Text()),
        sa.Column("state", sa.String(2)),
        sa.Column("zip", sa.Text()),
        sa.Column("beds", sa.SmallInteger()),
        sa.Column("baths", sa.Numeric(3, 1)),
        sa.Column("sqft", sa.Integer()),
        sa.Column("year_built", sa.SmallInteger()),
        sa.Column("purchase_price", sa.Numeric(12, 2)),
        sa.Column("purchase_date", sa.Date()),
        sa.Column("sold_price", sa.Numeric(12, 2)),
        sa.Column("sold_date", sa.Date()),
        sa.Column("loan_balance", sa.Numeric(12, 2)),
        sa.Column("interest_rate", sa.Numeric(5, 3)),
        sa.Column("monthly_payment", sa.Numeric(12, 2)),
        sa.Column("down_payment", sa.Numeric(12, 2)),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
    )
    op.create_index("ix_properties_owner_kind", "properties", ["owner_id", "kind"])

    op.create_table(
        "property_valuations",
        uuid_pk(),
        sa.Column("property_id", sa.Uuid(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", _enum("valuation_source"), nullable=False),
        sa.Column("value", sa.Numeric(12, 2), nullable=False),
        sa.Column("valued_at", sa.Date(), nullable=False),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
    )
    op.create_index(
        "ix_property_valuations_property_valued", "property_valuations", ["property_id", "valued_at"]
    )

    op.create_table(
        "transactions",
        uuid_pk(),
        sa.Column("property_id", sa.Uuid(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", _enum("txn_kind"), nullable=False),
        sa.Column("category", _enum("txn_category"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.CheckConstraint("amount > 0", name="transactions_amount_positive"),
    )
    op.create_index("ix_transactions_property_occurred", "transactions", ["property_id", "occurred_on"])

    op.create_table(
        "leases",
        uuid_pk(),
        sa.Column("property_id", sa.Uuid(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_name", sa.Text(), nullable=False),
        sa.Column("tenant_email", sa.Text()),
        sa.Column("tenant_phone", sa.Text()),
        sa.Column("rent", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit", sa.Numeric(12, 2)),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.Text()),
    )
    op.create_index(
        "ix_leases_property_active", "leases", ["property_id"],
        postgresql_where=sa.text("is_active"),
    )

    op.create_table(
        "listings",
        uuid_pk(),
        sa.Column("property_id", sa.Uuid(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", _enum("listing_status"), nullable=False, server_default="draft"),
        sa.Column("headline", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("rent_asked", sa.Numeric(12, 2), nullable=False),
        sa.Column("available_from", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
    )

    op.create_table(
        "conversations",
        uuid_pk(),
        sa.Column("kind", _enum("conversation_kind"), nullable=False),
        sa.Column("listing_id", sa.Uuid(), sa.ForeignKey("listings.id")),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("last_message_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "conversation_participants",
        sa.Column(
            "conversation_id", sa.Uuid(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column(
            "profile_id", sa.Uuid(),
            sa.ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("last_read_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "messages",
        uuid_pk(),
        sa.Column(
            "conversation_id", sa.Uuid(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("sender_id", sa.Uuid(), sa.ForeignKey("profiles.id")),
        sa.Column("sender_type", _enum("sender_type"), nullable=False, server_default="user"),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
    )
    op.create_index("ix_messages_conversation_created", "messages", ["conversation_id", "created_at"])

    op.create_table(
        "notifications",
        uuid_pk(),
        sa.Column("profile_id", sa.Uuid(), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", _enum("notification_kind"), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text()),
        sa.Column("link_path", sa.Text()),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.Column("emailed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
    )
    op.create_index(
        "ix_notifications_profile_unread", "notifications", ["profile_id", "created_at"],
        postgresql_where=sa.text("read_at is null"),
    )

    op.create_table(
        "market_fmr",
        uuid_pk(),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("area_code", sa.Text(), nullable=False),
        sa.Column("area_name", sa.Text(), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("bedrooms", sa.SmallInteger(), nullable=False),
        sa.Column("rent", sa.Numeric(12, 2), nullable=False),
        sa.UniqueConstraint("year", "area_code", "bedrooms"),
    )

    op.create_table(
        "market_hpi",
        uuid_pk(),
        sa.Column("level", sa.Text(), nullable=False),
        sa.Column("region_code", sa.Text(), nullable=False),
        sa.Column("region_name", sa.Text(), nullable=False),
        sa.Column("period", sa.Date(), nullable=False),
        sa.Column("index_value", sa.Numeric(10, 2), nullable=False),
        sa.UniqueConstraint("level", "region_code", "period"),
    )

    op.create_table(
        "premium_waitlist",
        uuid_pk(),
        sa.Column("profile_id", sa.Uuid(), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.UniqueConstraint("profile_id", "feature"),
    )

    op.create_table(
        "app_settings",
        sa.Column("key", sa.Text(), primary_key=True),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
    )


def downgrade() -> None:
    for table in [
        "app_settings", "premium_waitlist", "market_hpi", "market_fmr",
        "notifications", "messages", "conversation_participants", "conversations",
        "listings", "leases", "transactions", "property_valuations",
        "properties", "profiles",
    ]:
        op.drop_table(table)
    for name in ENUMS:
        op.execute(f"drop type {name}")
