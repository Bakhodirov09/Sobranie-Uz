"""empty message

Revision ID: 42c200f66818
Revises: a8689a977795
Create Date: 2024-09-03 17:09:48.394820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42c200f66818'
down_revision: Union[str, None] = 'a8689a977795'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments', sa.Column('lang', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('payments', 'lang')
    # ### end Alembic commands ###
