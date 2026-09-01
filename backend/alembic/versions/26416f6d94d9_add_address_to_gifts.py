"""add address to gifts

Revision ID: 26416f6d94d9
Revises: f1e2d3c4b5a6
Create Date: 2026-09-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "26416f6d94d9"
down_revision: str | None = "f1e2d3c4b5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("gifts", sa.Column("address", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("gifts", "address")
