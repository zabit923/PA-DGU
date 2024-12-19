"""empty message

Revision ID: 84e2b74de5f5
Revises:
Create Date: 2024-12-14 17:29:54.263956

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "84e2b74de5f5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "privaterooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_privaterooms_id"), "privaterooms", ["id"], unique=False)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.VARCHAR(length=128), nullable=False),
        sa.Column("first_name", sa.VARCHAR(length=128), nullable=False),
        sa.Column("last_name", sa.VARCHAR(length=128), nullable=False),
        sa.Column("email", sa.VARCHAR(length=255), nullable=False),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column(
            "is_superuser",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_teacher", sa.BOOLEAN(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "is_active", sa.BOOLEAN(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("first_name"),
        sa.UniqueConstraint("last_name"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("curator_id", sa.Integer(), nullable=False),
        sa.Column("course", sa.INTEGER(), nullable=False),
        sa.Column("facult", sa.VARCHAR(length=50), nullable=False),
        sa.Column("subgroup", sa.INTEGER(), nullable=True),
        sa.Column("invite_token", sa.VARCHAR(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["curator_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "facult", "course", "subgroup", name="uix_facult_course_subgroup"
        ),
        sa.UniqueConstraint("invite_token"),
    )
    op.create_index(op.f("ix_groups_id"), "groups", ["id"], unique=False)
    op.create_table(
        "privatemessages",
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
            ["privaterooms.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_privatemessages_id"), "privatemessages", ["id"], unique=False
    )
    op.create_table(
        "room_members",
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["privaterooms.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("room_id", "user_id"),
    )
    op.create_table(
        "group_members",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
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
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_groupmessages_id"), table_name="groupmessages")
    op.drop_table("groupmessages")
    op.drop_table("group_members")
    op.drop_table("room_members")
    op.drop_index(op.f("ix_privatemessages_id"), table_name="privatemessages")
    op.drop_table("privatemessages")
    op.drop_index(op.f("ix_groups_id"), table_name="groups")
    op.drop_table("groups")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_privaterooms_id"), table_name="privaterooms")
    op.drop_table("privaterooms")
    # ### end Alembic commands ###