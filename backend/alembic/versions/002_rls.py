"""Row Level Security policies + realtime publication.

Supabase-specific: relies on auth.uid() and the supabase_realtime publication.
Writes go through the API (service role bypasses RLS); these policies protect the
frontend's direct read paths (realtime) and act as defense in depth.

Revision ID: 002
Revises: 001
Create Date: 2026-07-05
"""

from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ALL_TABLES = [
    "profiles", "properties", "property_valuations", "transactions", "leases",
    "listings", "conversations", "conversation_participants", "messages",
    "notifications", "market_fmr", "market_hpi", "premium_waitlist", "app_settings",
]

POLICIES = [
    # profiles: own row
    """create policy profiles_select_own on profiles
       for select to authenticated using (id = auth.uid())""",
    """create policy profiles_update_own on profiles
       for update to authenticated using (id = auth.uid())""",
    # properties: owner reads own
    """create policy properties_select_own on properties
       for select to authenticated using (owner_id = auth.uid())""",
    # children of properties: via ownership join
    """create policy valuations_select_own on property_valuations
       for select to authenticated using (exists (
         select 1 from properties p where p.id = property_id and p.owner_id = auth.uid()))""",
    """create policy transactions_select_own on transactions
       for select to authenticated using (exists (
         select 1 from properties p where p.id = property_id and p.owner_id = auth.uid()))""",
    """create policy leases_select_own on leases
       for select to authenticated using (exists (
         select 1 from properties p where p.id = property_id and p.owner_id = auth.uid()))""",
    # listings: public sees active, owner sees own (v1.5 browse-ready)
    """create policy listings_select_active on listings
       for select to authenticated using (
         status = 'active' or exists (
           select 1 from properties p where p.id = property_id and p.owner_id = auth.uid()))""",
    # messaging: participants only — this is what makes realtime subscriptions safe
    """create policy conversations_select_participant on conversations
       for select to authenticated using (exists (
         select 1 from conversation_participants cp
         where cp.conversation_id = id and cp.profile_id = auth.uid()))""",
    """create policy participants_select_own on conversation_participants
       for select to authenticated using (profile_id = auth.uid())""",
    """create policy messages_select_participant on messages
       for select to authenticated using (exists (
         select 1 from conversation_participants cp
         where cp.conversation_id = conversation_id and cp.profile_id = auth.uid()))""",
    # notifications: own
    """create policy notifications_select_own on notifications
       for select to authenticated using (profile_id = auth.uid())""",
    # market data: readable by any signed-in user
    "create policy market_fmr_select_all on market_fmr for select to authenticated using (true)",
    "create policy market_hpi_select_all on market_hpi for select to authenticated using (true)",
    # premium_waitlist / app_settings: no client policies -> deny all (API only)
]


def upgrade() -> None:
    for table in ALL_TABLES:
        op.execute(f"alter table {table} enable row level security")
    for policy in POLICIES:
        op.execute(policy)
    # Realtime: the frontend subscribes to INSERTs on these two tables only
    op.execute("alter publication supabase_realtime add table messages")
    op.execute("alter publication supabase_realtime add table notifications")


def downgrade() -> None:
    op.execute("alter publication supabase_realtime drop table messages")
    op.execute("alter publication supabase_realtime drop table notifications")
    for policy in POLICIES:
        name = policy.split(" on ")[0].replace("create policy ", "").strip()
        table = policy.split(" on ")[1].split()[0]
        op.execute(f"drop policy if exists {name} on {table}")
    for table in ALL_TABLES:
        op.execute(f"alter table {table} disable row level security")
