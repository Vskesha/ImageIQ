"""add

Revision ID: 2e2e44ea0bab
Revises: 0eec8704bd23
Create Date: 2023-12-28 16:03:36.212987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e2e44ea0bab'
down_revision: Union[str, None] = '0eec8704bd23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE TYPE role as ENUM('admin', 'moderator', 'user')")
    op.add_column('users', sa.Column('role', sa.Enum('admin', 'moderator', 'user', name='role'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    op.execute("DROP TYPE role")
    # ### end Alembic commands ###
