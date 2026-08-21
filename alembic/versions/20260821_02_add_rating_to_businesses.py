"""Add rating and user_ratings_total to businesses.

Revision ID: 20260821_02
Revises: 20260821_01
Create Date: 2026-08-21
"""

import sqlalchemy as sa

from alembic import op

revision = "20260821_02"
down_revision = "20260821_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ``main.py`` may have created the legacy table before Alembic ran. Check
    # the schema so this revision can safely be applied in either order.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("businesses"):
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

    columns = {column["name"] for column in sa.inspect(bind).get_columns("businesses")}
    if "rating" not in columns:
        op.add_column("businesses", sa.Column("rating", sa.Float(), nullable=True))
    if "user_ratings_total" not in columns:
        op.add_column("businesses", sa.Column("user_ratings_total", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("businesses", "user_ratings_total")
    op.drop_column("businesses", "rating")
