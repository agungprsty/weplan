"""add savings targets and transactions (cashflow)

Revision ID: e7f8a9b0c1d2
Revises: a1b2c3d4e5f6
Create Date: 2026-08-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e7f8a9b0c1d2"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "savings_targets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("wedding_id", sa.Uuid(), nullable=False),
        sa.Column("target_amount", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["wedding_id"], ["weddings.id"], name=op.f("savings_targets_wedding_id_fkey"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("savings_targets_pkey")),
        sa.UniqueConstraint("wedding_id", name=op.f("savings_targets_wedding_id_key")),
    )
    op.create_index(op.f("savings_targets_wedding_id_idx"), "savings_targets", ["wedding_id"], unique=True)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("wedding_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="lainnya"),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("proof_url", sa.String(length=500), nullable=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["wedding_id"], ["weddings.id"], name=op.f("transactions_wedding_id_fkey"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("transactions_pkey")),
    )
    op.create_index(op.f("transactions_wedding_id_idx"), "transactions", ["wedding_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("transactions_wedding_id_idx"), table_name="transactions")
    op.drop_table("transactions")
    op.drop_index(op.f("savings_targets_wedding_id_idx"), table_name="savings_targets")
    op.drop_table("savings_targets")
