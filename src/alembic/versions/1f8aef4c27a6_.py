"""empty message

Revision ID: 1f8aef4c27a6
Revises: 34381bdb0580
Create Date: 2024-11-15 13:34:43.427703

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f8aef4c27a6"
down_revision: Union[str, None] = "34381bdb0580"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_groups_id", table_name="groups")
    op.drop_table("groups")
    op.drop_table("group_members")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "group_members",
        sa.Column("group_id", sa.INTEGER(), nullable=False),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("group_id", "user_id"),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("curator_id", sa.INTEGER(), nullable=False),
        sa.Column("course", sa.INTEGER(), nullable=False),
        sa.Column("facult", sa.VARCHAR(length=50), nullable=False),
        sa.Column("subgroup", sa.INTEGER(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["curator_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_groups_id", "groups", ["id"], unique=False)
    # ### end Alembic commands ###
