"""empty message

Revision ID: 1ebd792de3dd
Revises: 35c3dec6b06f
Create Date: 2024-03-08 23:44:47.299493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ebd792de3dd'
down_revision: Union[str, None] = '35c3dec6b06f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('history_buys', 'status',
               existing_type=sa.BOOLEAN(),
               type_=sa.String(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('history_buys', 'status',
               existing_type=sa.String(),
               type_=sa.BOOLEAN(),
               existing_nullable=True)
    # ### end Alembic commands ###
