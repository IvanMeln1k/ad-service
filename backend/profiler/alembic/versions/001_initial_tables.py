"""initial tables

Revision ID: 001
Revises:
Create Date: 2026-04-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = sa.Enum("MODERATOR", "ADMIN", name="role_enum")


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("user_id", sa.String(255), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "profile_roles",
        sa.Column(
            "user_id",
            sa.String(255),
            sa.ForeignKey("profiles.user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("role", role_enum, primary_key=True, create_constraint=True),
        sa.Column(
            "assigned_at",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "profile_avatars",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(255),
            sa.ForeignKey("profiles.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("s3_key", sa.String(1024), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_profile_avatars_user_id", "profile_avatars", ["user_id"])

    op.create_table(
        "user_emails",
        sa.Column(
            "user_id",
            sa.String(255),
            sa.ForeignKey("profiles.user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("confirmed_at", sa.DateTime, nullable=True),
    )
    op.create_index("idx_user_emails_email", "user_emails", ["email"])

    op.create_table(
        "email_confirmation_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("token", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime, nullable=False),
    )
    op.create_index(
        "idx_email_confirmation_tokens_token",
        "email_confirmation_tokens",
        ["token"],
    )
    op.create_index(
        "idx_email_confirmation_tokens_user_id",
        "email_confirmation_tokens",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_table("email_confirmation_tokens")
    op.drop_table("user_emails")
    op.drop_table("profile_avatars")
    op.drop_table("profile_roles")
    op.drop_table("profiles")
    role_enum.drop(op.get_bind(), checkfirst=True)
