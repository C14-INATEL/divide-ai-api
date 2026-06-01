"""add description column to groups table

Revision ID: 0002_add_group_description
Revises: 0001_add_debts
Create Date: 2026-06-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_group_description'
down_revision = '0001_add_debts'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('groups', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('groups', 'description')
