"""add vendors kua mahar subscription (50k/6bulan)

Revision ID: a1b2c3d4e5f6
Revises: dd216406ac21
Create Date: 2026-08-26
"""

from collections.abc import Sequence
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "dd216406ac21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # plans.duration_months
    op.add_column("plans", sa.Column("duration_months", sa.Integer(), nullable=False, server_default="6"))
    # weddings.plan_expires_at
    op.add_column("weddings", sa.Column("plan_expires_at", sa.DateTime(), nullable=True))
    # orders.expires_at
    op.add_column("orders", sa.Column("expires_at", sa.DateTime(), nullable=True))

    # vendors
    op.create_table(
        "vendors",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("wedding_id", UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="lainnya"),
        sa.Column("contact_wa", sa.String(length=50), nullable=True),
        sa.Column("total_amount", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("dp_amount", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("paid_amount", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="belum_bayar"),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("invoice_url", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["wedding_id"], ["weddings.id"], name=op.f("vendors_wedding_id_fkey"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("vendors_pkey")),
    )
    op.create_index(op.f("vendors_wedding_id_idx"), "vendors", ["wedding_id"], unique=False)

    # kua_documents
    op.create_table(
        "kua_documents",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("wedding_id", UUID(as_uuid=True), nullable=False),
        sa.Column("owner_type", sa.String(length=20), nullable=False, server_default="both"),
        sa.Column("document_key", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="belum"),
        sa.Column("file_url", sa.String(length=500), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["wedding_id"], ["weddings.id"], name=op.f("kua_documents_wedding_id_fkey"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("kua_documents_pkey")),
    )
    op.create_index(op.f("kua_documents_wedding_id_idx"), "kua_documents", ["wedding_id"], unique=False)

    # mahar_seserahan_items
    op.create_table(
        "mahar_seserahan_items",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("wedding_id", UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False, server_default="mahar"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("estimated_cost", sa.BigInteger(), nullable=True),
        sa.Column("actual_cost", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="rencana"),
        sa.Column("tenor_total", sa.Integer(), nullable=True),
        sa.Column("tenor_paid", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["wedding_id"], ["weddings.id"], name=op.f("mahar_seserahan_items_wedding_id_fkey"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("mahar_seserahan_items_pkey")),
    )
    op.create_index(op.f("mahar_seserahan_items_wedding_id_idx"), "mahar_seserahan_items", ["wedding_id"], unique=False)

    # Seed plans: Gratis & Premium 50k/6bln (idempotent)
    conn = op.get_bind()
    # Update existing plans duration (since column added with server_default 6, gratis should be 0)
    conn.execute(sa.text("UPDATE plans SET duration_months = 0 WHERE slug = 'gratis'"))
    conn.execute(sa.text("UPDATE plans SET duration_months = 6 WHERE slug = 'premium'"))
    # Insert if not exists
    now = datetime.utcnow()
    for slug, name, price, max_guests, duration in [
        ("gratis", "Gratis", 0, 50, 0),
        ("premium", "Premium", 50000, 9999, 6),
    ]:
        exists = conn.execute(sa.text("SELECT 1 FROM plans WHERE slug = :slug"), {"slug": slug}).first()
        if not exists:
            conn.execute(
                sa.text(
                    "INSERT INTO plans (id, name, slug, price, max_guests, duration_months, is_active, created_at, updated_at) "
                    "VALUES (:id, :name, :slug, :price, :max_guests, :duration_months, :is_active, :created_at, :updated_at)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "slug": slug,
                    "price": price,
                    "max_guests": max_guests,
                    "duration_months": duration,
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                },
            )


def downgrade() -> None:
    op.drop_index(op.f("mahar_seserahan_items_wedding_id_idx"), table_name="mahar_seserahan_items")
    op.drop_table("mahar_seserahan_items")
    op.drop_index(op.f("kua_documents_wedding_id_idx"), table_name="kua_documents")
    op.drop_table("kua_documents")
    op.drop_index(op.f("vendors_wedding_id_idx"), table_name="vendors")
    op.drop_table("vendors")
    op.drop_column("orders", "expires_at")
    op.drop_column("weddings", "plan_expires_at")
    op.drop_column("plans", "duration_months")
