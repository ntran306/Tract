"""Enable RLS on alembic_version (Supabase linter: rls_disabled_in_public).

Alembic creates its version table itself, so migration 002 never covered it.
No policies = deny all client access; Alembic itself connects as the table
owner (postgres via the pooler), which bypasses RLS, so migrations still run.

Revision ID: 005
Revises: 004
Create Date: 2026-07-12
"""

from typing import Sequence, Union

from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("alter table alembic_version enable row level security")


def downgrade() -> None:
    op.execute("alter table alembic_version disable row level security")
