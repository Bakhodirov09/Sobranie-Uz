"""empty message

Revision ID: 6e27ba9f07f1
Revises: 48fcb707c4d1
Create Date: 2024-02-23 21:51:26.858716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e27ba9f07f1'
down_revision: Union[str, None] = '48fcb707c4d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location_name', sa.String(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('chat_id', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('locations')
    # ### end Alembic commands ###
