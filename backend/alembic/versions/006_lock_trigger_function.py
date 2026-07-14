"""Revoke public EXECUTE on handle_new_user() (Supabase linter findings).

Postgres grants EXECUTE on new functions to PUBLIC by default, and PostgREST
exposes public-schema functions at /rest/v1/rpc/*. The signup trigger only ever
needs to run as a trigger on auth.users — EXECUTE for that is checked against
supabase_auth_admin (the table owner), which we grant explicitly.

Revision ID: 006
Revises: 005
Create Date: 2026-07-12
"""

from typing import Sequence, Union

from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "revoke execute on function public.handle_new_user() from public, anon, authenticated"
    )
    op.execute("grant execute on function public.handle_new_user() to supabase_auth_admin")


def downgrade() -> None:
    op.execute("grant execute on function public.handle_new_user() to public")
