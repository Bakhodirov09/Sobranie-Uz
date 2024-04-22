"""empty message

Revision ID: 59b24acf523f
Revises: 8664468821c4
Create Date: 2024-04-22 15:58:28.626308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59b24acf523f'
down_revision: Union[str, None] = '8664468821c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('history_buys', 'is_waiting')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history_buys', sa.Column('is_waiting', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
