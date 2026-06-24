"""create repositories table

Revision ID: e25e9854ef24
Revises: 5d137b0183a5
Create Date: 2026-06-24 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e25e9854ef24'
down_revision: Union[str, Sequence[str], None] = '5d137b0183a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('repositories',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('github_repo_id', sa.BigInteger(), nullable=False),
    sa.Column('repo_name', sa.String(length=255), nullable=False),
    sa.Column('repo_full_name', sa.String(length=255), nullable=False),
    sa.Column('repo_url', sa.String(length=500), nullable=False),
    sa.Column('owner_github_username', sa.String(length=255), nullable=False),
    sa.Column('default_branch', sa.String(length=100), nullable=False),
    sa.Column('is_private', sa.Boolean(), nullable=False),
    sa.Column('is_sync_enabled', sa.Boolean(), nullable=False),
    sa.Column('leetcode_enabled', sa.Boolean(), nullable=False),
    sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_sync_status', sa.String(length=100), nullable=True),
    sa.Column('github_created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('github_updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'repo_name', name='uq_repositories_user_repo')
    )
    op.create_index(op.f('ix_repositories_github_repo_id'), 'repositories', ['github_repo_id'], unique=True)
    op.create_index(op.f('ix_repositories_user_id'), 'repositories', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_repositories_user_id'), table_name='repositories')
    op.drop_index(op.f('ix_repositories_github_repo_id'), table_name='repositories')
    op.drop_table('repositories')
