"""add activities table

Revision ID: f1e2d3c4b5a6
Revises: c9d8e7f6a5b4
Create Date: 2026-08-31
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f1e2d3c4b5a6"
down_revision: str | None = "c9d8e7f6a5b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("wedding_id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["wedding_id"],
            ["weddings.id"],
            name=op.f("activities_wedding_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("activities_actor_user_id_fkey"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("activities_pkey")),
    )
    op.create_index(
        op.f("activities_wedding_id_idx"), "activities", ["wedding_id"], unique=False
    )
    op.create_index(
        op.f("activities_actor_user_id_idx"),
        "activities",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("activities_created_at_idx"), "activities", ["created_at"], unique=False
    )
    # Composite index for tenant-scoped timeline queries: WHERE wedding_id=? ORDER BY created_at DESC
    op.create_index(
        "ix_activities_wedding_created",
        "activities",
        ["wedding_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_activities_wedding_created", table_name="activities")
    op.drop_index(op.f("activities_created_at_idx"), table_name="activities")
    op.drop_index(op.f("activities_actor_user_id_idx"), table_name="activities")
    op.drop_index(op.f("activities_wedding_id_idx"), table_name="activities")
    op.drop_table("activities")
