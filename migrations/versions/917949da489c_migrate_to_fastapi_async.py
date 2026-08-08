"""migrate_to_fastapi_async

Revision ID: 917949da489c
Revises: 003_add_request_id
Create Date: 2026-08-04 20:32:56.862347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '917949da489c'
down_revision = '002_performance_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema to this revision."""
    pass


def downgrade() -> None:
    """Downgrade database schema to previous revision."""
    pass
