"""Register the existing businesses table as the Alembic baseline.

Revision ID: 20260821_00
Revises:
Create Date: 2026-08-21
"""

import sqlalchemy as sa

from alembic import op

revision = "20260821_00"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing deployments already have this table. Creating it here as a
    # fallback also makes a fresh Neon database migratable before the app
    # starts and calls ``create_all``.
    bind = op.get_bind()
    if sa.inspect(bind).has_table("businesses"):
        return

    op.create_table(
        "businesses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("place_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("maps_url", sa.Text(), nullable=True),
        sa.Column("has_website", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("business_type", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("place_id"),
    )
    op.create_index("ix_businesses_id", "businesses", ["id"])
    op.create_index("ix_businesses_place_id", "businesses", ["place_id"])
    op.create_index("ix_businesses_business_type", "businesses", ["business_type"])


def downgrade() -> None:
    pass
