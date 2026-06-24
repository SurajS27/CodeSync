"""add bootstrap index and attempt timestamp

Revision ID: 7a3b4c5d6e7f
Revises: f0a3d92023d5
Create Date: 2026-06-24 11:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a3b4c5d6e7f'
down_revision: Union[str, Sequence[str], None] = 'f0a3d92023d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add attempt timestamp column
    op.add_column('repositories', sa.Column('last_bootstrap_attempt_at', sa.DateTime(timezone=True), nullable=True))

    # 2. Add index on bootstrap_status column
    op.create_index(
        op.f('ix_repositories_bootstrap_status'),
        'repositories',
        ['bootstrap_status'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Drop index
    op.drop_index(op.f('ix_repositories_bootstrap_status'), table_name='repositories')

    # 2. Drop attempt timestamp column
    op.drop_column('repositories', 'last_bootstrap_attempt_at')
