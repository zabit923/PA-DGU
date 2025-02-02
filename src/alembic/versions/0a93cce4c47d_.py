"""empty message

Revision ID: 0a93cce4c47d
Revises: 7901827def70
Create Date: 2025-01-02 21:51:47.275571

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0a93cce4c47d"
down_revision: Union[str, None] = "7901827def70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("questions", "order", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("questions", "order", existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###
