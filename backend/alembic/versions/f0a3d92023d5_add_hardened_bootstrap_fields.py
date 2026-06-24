"""add hardened bootstrap fields

Revision ID: f0a3d92023d5
Revises: f78e4d2a1359
Create Date: 2026-06-24 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0a3d92023d5'
down_revision: Union[str, Sequence[str], None] = 'f78e4d2a1359'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the Enum type in the database
    bootstrap_status_enum = sa.Enum('pending', 'running', 'completed', 'failed', name='bootstrapstatus')
    bootstrap_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add columns
    op.add_column('repositories', sa.Column(
        'bootstrap_status',
        sa.Enum('pending', 'running', 'completed', 'failed', name='bootstrapstatus'),
        server_default='pending',
        nullable=False
    ))
    op.add_column('repositories', sa.Column('bootstrap_error', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('repositories', 'bootstrap_error')
    op.drop_column('repositories', 'bootstrap_status')

    # Drop the Enum type
    bootstrap_status_enum = sa.Enum('pending', 'running', 'completed', 'failed', name='bootstrapstatus')
    bootstrap_status_enum.drop(op.get_bind(), checkfirst=True)
