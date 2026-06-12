"""rename proof_path to proof_url on debt_participants

Revision ID: 0003_rename_proof_url
Revises: 0002_add_group_description
Create Date: 2026-06-11 00:00:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0003_rename_proof_url'
down_revision = '0002_add_group_description'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('debt_participants', 'proof_path', new_column_name='proof_url')


def downgrade() -> None:
    op.alter_column('debt_participants', 'proof_url', new_column_name='proof_path')
