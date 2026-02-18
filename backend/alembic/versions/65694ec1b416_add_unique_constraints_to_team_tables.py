"""add unique constraints to team tables

Revision ID: 65694ec1b416
Revises: 3a7d774e3c02
Create Date: 2026-02-07 21:13:52.760068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '65694ec1b416'
down_revision: Union[str, None] = '3a7d774e3c02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add unique constraints to team tables to enforce data integrity.

    - team_members: Ensure a user can only have one membership per team
    - task_shares: Ensure a task can only be shared once with each user
    - teams: Ensure team names are unique (already exists via index)
    """
    # Add unique constraint to team_members (team_id, user_id)
    # This prevents duplicate memberships
    op.create_unique_constraint(
        'uq_team_user',
        'team_members',
        ['team_id', 'user_id']
    )

    # Add unique constraint to task_shares (task_id, shared_with_user_id)
    # This prevents sharing the same task multiple times with the same user
    op.create_unique_constraint(
        'uq_task_share',
        'task_shares',
        ['task_id', 'shared_with_user_id']
    )


def downgrade() -> None:
    """
    Remove unique constraints from team tables.
    """
    # Remove unique constraint from task_shares
    op.drop_constraint('uq_task_share', 'task_shares', type_='unique')

    # Remove unique constraint from team_members
    op.drop_constraint('uq_team_user', 'team_members', type_='unique')
