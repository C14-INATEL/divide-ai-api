"""add debts and debt_participants tables

Revision ID: 0001_add_debts
Revises: 
Create Date: 2026-05-31 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_add_debts'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'debts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('group_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_amount', sa.Numeric(12,2), nullable=False),
        sa.Column('split_type', sa.String(length=50), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pendente'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'debt_participants',
        sa.Column('debt_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('debts.id', ondelete='CASCADE'), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False),
        sa.Column('percentage', sa.Numeric(5,2), nullable=False),
        sa.Column('amount', sa.Numeric(12,2), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pendente'),
        sa.Column('has_proof', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('proof_path', sa.String(), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('debt_participants')
    op.drop_table('debts')
