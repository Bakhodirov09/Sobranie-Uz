"""empty message

Revision ID: 55f977005ab6
Revises: c14c15592e20
Create Date: 2024-02-10 19:45:44.752317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55f977005ab6'
down_revision: Union[str, None] = 'c14c15592e20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('logo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('photo', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('logo')
    # ### end Alembic commands ###
