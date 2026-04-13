"""Initial authentication tables

Revision ID: 001
Revises:
Create Date: 2026-02-15 18:20:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_auth table
    op.create_table(
        "user_auth",
        sa.Column("uid", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("uid"),
    )

    # Create indexes for user_auth
    op.create_index("idx_user_auth_uid", "user_auth", ["uid"])

    # Create refresh_tokens table
    op.create_table(
        "refresh_tokens",
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("uid", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("token_hash"),
    )

    # Create indexes for refresh_tokens
    op.create_index("idx_refresh_tokens_uid", "refresh_tokens", ["uid"])
    op.create_index(
        "idx_refresh_tokens_uid_token", "refresh_tokens", ["uid", "token_hash"]
    )
    op.create_index("idx_refresh_tokens_expires", "refresh_tokens", ["expires_at"])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("idx_refresh_tokens_expires", table_name="refresh_tokens")
    op.drop_index("idx_refresh_tokens_uid_token", table_name="refresh_tokens")
    op.drop_index("idx_refresh_tokens_uid", table_name="refresh_tokens")
    op.drop_index("idx_user_auth_uid", table_name="user_auth")

    # Drop tables
    op.drop_table("refresh_tokens")
    op.drop_table("user_auth")
