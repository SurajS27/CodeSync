"""add bootstrap info to repositories

Revision ID: f78e4d2a1359
Revises: e25e9854ef24
Create Date: 2026-06-24 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f78e4d2a1359'
down_revision: Union[str, Sequence[str], None] = 'e25e9854ef24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('repositories', sa.Column('bootstrapped_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('repositories', sa.Column('bootstrap_version', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('repositories', 'bootstrap_version')
    op.drop_column('repositories', 'bootstrapped_at')
