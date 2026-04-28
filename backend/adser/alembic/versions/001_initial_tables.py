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

ad_status_enum = sa.Enum("ACTIVE", "CLOSED", name="ad_status_enum")


def upgrade() -> None:
    op.create_table(
        "ads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", ad_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )
    op.create_index("idx_ads_user_id", "ads", ["user_id"])
    op.create_index("idx_ads_status", "ads", ["status"])

    op.create_table(
        "ad_photos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ad_id", UUID(as_uuid=True), sa.ForeignKey("ads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("s3_key", sa.String(1024), nullable=False),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
        sa.Column("uploaded_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_ad_photos_ad_id", "ad_photos", ["ad_id"])

    op.create_table(
        "ad_bans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ad_id", UUID(as_uuid=True), sa.ForeignKey("ads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("moderator_id", sa.String(255), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("banned_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("unbanned_by_id", sa.String(255), nullable=True),
        sa.Column("unban_reason", sa.Text, nullable=True),
        sa.Column("unbanned_at", sa.DateTime, nullable=True),
    )
    op.create_index("idx_ad_bans_ad_id", "ad_bans", ["ad_id"])


def downgrade() -> None:
    op.drop_table("ad_bans")
    op.drop_table("ad_photos")
    op.drop_table("ads")
    ad_status_enum.drop(op.get_bind(), checkfirst=True)
