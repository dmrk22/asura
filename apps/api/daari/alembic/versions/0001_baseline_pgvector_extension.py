"""baseline: enable pgvector extension

Revision ID: 0001_baseline
Revises:
Create Date: 2026-09-18

No tables yet — P2 autogenerates those from SQLAlchemy models. This baseline
only makes `vector` available for when it does.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
