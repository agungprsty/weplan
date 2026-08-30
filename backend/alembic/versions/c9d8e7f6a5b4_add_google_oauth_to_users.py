"""add google oauth to users

Revision ID: c9d8e7f6a5b4
Revises: 38567cb18485
Create Date: 2026-08-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c9d8e7f6a5b4'
down_revision: Union[str, None] = '38567cb18485'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('provider', sa.String(length=20), nullable=False, server_default='email'))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.alter_column('users', 'hashed_password', existing_type=sa.String(length=255), nullable=True)
    op.create_index(op.f('users_google_id_idx'), 'users', ['google_id'], unique=True)
    # hilangkan server_default setelah kolom terisi agar model default tetap jalan
    op.alter_column('users', 'provider', server_default=None)
    op.alter_column('users', 'email_verified', server_default=None)


def downgrade() -> None:
    op.drop_index(op.f('users_google_id_idx'), table_name='users')
    op.alter_column('users', 'hashed_password', existing_type=sa.String(length=255), nullable=False)
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'provider')
    op.drop_column('users', 'google_id')
