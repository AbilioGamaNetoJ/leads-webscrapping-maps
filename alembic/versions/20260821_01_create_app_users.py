"""Create application users.

Revision ID: 20260821_01
Revises:
Create Date: 2026-08-21
"""

import sqlalchemy as sa

from alembic import op

revision = "20260821_01"
down_revision = "20260821_00"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_users",
        sa.Column("clerk_user_id", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("role IN ('admin', 'member')", name="app_users_role_check"),
        sa.PrimaryKeyConstraint("clerk_user_id"),
    )
    op.create_index("ix_app_users_email", "app_users", ["email"])
    op.create_index("ix_app_users_role", "app_users", ["role"])
    op.create_index("ix_app_users_is_active", "app_users", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_app_users_is_active", table_name="app_users")
    op.drop_index("ix_app_users_role", table_name="app_users")
    op.drop_index("ix_app_users_email", table_name="app_users")
    op.drop_table("app_users")
