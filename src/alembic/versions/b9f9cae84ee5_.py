"""empty message

Revision ID: b9f9cae84ee5
Revises: c082b4606181
Create Date: 2024-12-10 22:37:55.308336

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b9f9cae84ee5"
down_revision: Union[str, None] = "c082b4606181"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "personalrooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_personalrooms_id"), "personalrooms", ["id"], unique=False)
    op.create_table(
        "personalmessages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.TEXT(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["personalrooms.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_personalmessages_id"), "personalmessages", ["id"], unique=False
    )
    op.create_table(
        "room_participants",
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["personalrooms.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("room_id", "user_id"),
    )
    op.create_table(
        "groupmessages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.TEXT(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_groupmessages_id"), "groupmessages", ["id"], unique=False)
    op.drop_index("ix_messages_id", table_name="messages")
    op.drop_table("messages")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "messages",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("sender_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("recipient_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("text", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["group_id"], ["groups.id"], name="messages_group_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["recipient_id"], ["users.id"], name="messages_recipient_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"], ["users.id"], name="messages_sender_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="messages_pkey"),
    )
    op.create_index("ix_messages_id", "messages", ["id"], unique=False)
    op.drop_index(op.f("ix_groupmessages_id"), table_name="groupmessages")
    op.drop_table("groupmessages")
    op.drop_table("room_participants")
    op.drop_index(op.f("ix_personalmessages_id"), table_name="personalmessages")
    op.drop_table("personalmessages")
    op.drop_index(op.f("ix_personalrooms_id"), table_name="personalrooms")
    op.drop_table("personalrooms")
    # ### end Alembic commands ###
