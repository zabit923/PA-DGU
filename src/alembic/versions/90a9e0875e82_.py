"""empty message

Revision ID: 90a9e0875e82
Revises: 6ff923b9734c
Create Date: 2025-01-02 13:48:42.120299

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "90a9e0875e82"
down_revision: Union[str, None] = "6ff923b9734c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "exams", "quantity_questions", existing_type=sa.INTEGER(), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "exams", "quantity_questions", existing_type=sa.INTEGER(), nullable=False
    )
    # ### end Alembic commands ###
