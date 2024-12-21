"""empty message

Revision ID: e7f33cf4ee90
Revises: 0a3e588d0831
Create Date: 2024-12-21 19:15:19.304220

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7f33cf4ee90"
down_revision: Union[str, None] = "0a3e588d0831"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "is_online", sa.BOOLEAN(), server_default=sa.text("false"), nullable=False
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "is_online")
    # ### end Alembic commands ###
