"""add performance indexes for p1

Revision ID: 5a6b7c8d9e0f
Revises: 26416f6d94d9
Create Date: 2026-09-02
"""

from collections.abc import Sequence

from alembic import op

revision: str = "5a6b7c8d9e0f"
down_revision: str | None = "26416f6d94d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # guests: category, rsvp, side filtering is frequent
    op.create_index("ix_guests_wedding_category", "guests", ["wedding_id", "category"], unique=False)
    op.create_index("ix_guests_wedding_rsvp", "guests", ["wedding_id", "rsvp_status"], unique=False)
    op.create_index("ix_guests_wedding_side", "guests", ["wedding_id", "side"], unique=False)

    # checklists: status, due_date, category
    op.create_index("ix_checklists_wedding_status", "checklists", ["wedding_id", "status"], unique=False)
    op.create_index("ix_checklists_wedding_due", "checklists", ["wedding_id", "due_date"], unique=False)
    op.create_index("ix_checklists_wedding_category", "checklists", ["wedding_id", "category"], unique=False)

    # transactions: date & type
    op.create_index("ix_transactions_wedding_date", "transactions", ["wedding_id", "transaction_date"], unique=False)
    op.create_index("ix_transactions_wedding_type", "transactions", ["wedding_id", "type"], unique=False)

    # vendors: due_date & status
    op.create_index("ix_vendors_wedding_due", "vendors", ["wedding_id", "due_date"], unique=False)
    op.create_index("ix_vendors_wedding_status", "vendors", ["wedding_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_vendors_wedding_status", table_name="vendors")
    op.drop_index("ix_vendors_wedding_due", table_name="vendors")
    op.drop_index("ix_transactions_wedding_type", table_name="transactions")
    op.drop_index("ix_transactions_wedding_date", table_name="transactions")
    op.drop_index("ix_checklists_wedding_category", table_name="checklists")
    op.drop_index("ix_checklists_wedding_due", table_name="checklists")
    op.drop_index("ix_checklists_wedding_status", table_name="checklists")
    op.drop_index("ix_guests_wedding_side", table_name="guests")
    op.drop_index("ix_guests_wedding_rsvp", table_name="guests")
    op.drop_index("ix_guests_wedding_category", table_name="guests")
