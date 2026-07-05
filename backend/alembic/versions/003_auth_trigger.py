"""Signup trigger: auth.users insert -> public.profiles row.

Revision ID: 003
Revises: 002
Create Date: 2026-07-05
"""

from typing import Sequence, Union

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        create or replace function public.handle_new_user()
        returns trigger
        language plpgsql
        security definer set search_path = public
        as $$
        begin
          insert into public.profiles (id, display_name)
          values (
            new.id,
            coalesce(
              new.raw_user_meta_data->>'display_name',
              split_part(new.email, '@', 1),
              'New user'
            )
          );
          return new;
        end
        $$
        """
    )
    op.execute(
        """
        create trigger on_auth_user_created
        after insert on auth.users
        for each row execute function public.handle_new_user()
        """
    )


def downgrade() -> None:
    op.execute("drop trigger if exists on_auth_user_created on auth.users")
    op.execute("drop function if exists public.handle_new_user()")
