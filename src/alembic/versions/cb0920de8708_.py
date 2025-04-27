"""empty message

Revision ID: cb0920de8708
Revises: 3776da73fe13
Create Date: 2025-04-26 17:37:15.647428

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cb0920de8708"
down_revision: Union[str, None] = "3776da73fe13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("groups", sa.Column("methodist_id", sa.Integer(), nullable=True))

    op.execute("UPDATE groups SET methodist_id = 1")

    op.alter_column("groups", "methodist_id", nullable=False)

    op.drop_constraint("groups_curator_id_fkey", "groups", type_="foreignkey")
    op.create_foreign_key(None, "groups", "users", ["methodist_id"], ["id"])
    op.drop_column("groups", "curator_id")


def downgrade() -> None:
    op.add_column("groups", sa.Column("curator_id", sa.Integer(), nullable=False))
    op.drop_constraint(None, "groups", type_="foreignkey")
    op.create_foreign_key(
        "groups_curator_id_fkey", "groups", "users", ["curator_id"], ["id"]
    )
    op.drop_column("groups", "methodist_id")
