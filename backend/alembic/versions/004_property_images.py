"""Property images: table + Supabase storage bucket + policies.

Prototype choice: a PUBLIC bucket so reads need no signed URLs. House exterior
photos are low-sensitivity; hardening to a private bucket with signed URLs and
per-owner read policies is a v2 item (see docs/DECISIONS.md D12).

Revision ID: 004
Revises: 003
Create Date: 2026-07-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BUCKET = "property-images"


def upgrade() -> None:
    op.create_table(
        "property_images",
        sa.Column(
            "id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "property_id",
            sa.Uuid(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("storage_path", sa.Text(), nullable=False),  # object key within bucket
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_property_images_property", "property_images", ["property_id", "sort_order"]
    )

    op.execute("alter table property_images enable row level security")
    op.execute(
        """
        create policy property_images_select_own on property_images
        for select to authenticated using (exists (
          select 1 from properties p
          where p.id = property_id and p.owner_id = auth.uid()))
        """
    )

    # Storage: public bucket + authenticated write. Files uploaded client-side by
    # the owner via supabase-js; reads are public URLs.
    op.execute(
        f"""
        insert into storage.buckets (id, name, public)
        values ('{BUCKET}', '{BUCKET}', true)
        on conflict (id) do nothing
        """
    )
    op.execute(
        f"""
        create policy "property_images_authenticated_write" on storage.objects
        for insert to authenticated
        with check (bucket_id = '{BUCKET}')
        """
    )
    op.execute(
        f"""
        create policy "property_images_authenticated_modify" on storage.objects
        for update to authenticated
        using (bucket_id = '{BUCKET}')
        """
    )
    op.execute(
        f"""
        create policy "property_images_authenticated_delete" on storage.objects
        for delete to authenticated
        using (bucket_id = '{BUCKET}')
        """
    )


def downgrade() -> None:
    op.execute('drop policy if exists "property_images_authenticated_delete" on storage.objects')
    op.execute('drop policy if exists "property_images_authenticated_modify" on storage.objects')
    op.execute('drop policy if exists "property_images_authenticated_write" on storage.objects')
    op.execute(f"delete from storage.buckets where id = '{BUCKET}'")
    op.drop_table("property_images")
