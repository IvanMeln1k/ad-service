"""add price, city, category to ads

Revision ID: 002
Revises: 001
Create Date: 2026-04-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

category_enum = sa.Enum("AUTO", "REALTY", "ELECTRONICS", "CLOTHING", "SERVICES", "OTHER", name="category_enum")


def upgrade() -> None:
    category_enum.create(op.get_bind(), checkfirst=True)

    op.add_column("ads", sa.Column("price", sa.Numeric(12, 2), nullable=True))
    op.add_column("ads", sa.Column("city", sa.String(255), nullable=True))
    op.add_column("ads", sa.Column("category", category_enum, nullable=True))

    op.create_index("idx_ads_category", "ads", ["category"])
    op.create_index("idx_ads_city", "ads", ["city"])
    op.create_index("idx_ads_price", "ads", ["price"])


def downgrade() -> None:
    op.drop_index("idx_ads_price")
    op.drop_index("idx_ads_city")
    op.drop_index("idx_ads_category")

    op.drop_column("ads", "category")
    op.drop_column("ads", "city")
    op.drop_column("ads", "price")

    category_enum.drop(op.get_bind(), checkfirst=True)
