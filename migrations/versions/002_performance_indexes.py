"""
Alembic migration for adding composite and foreign key indexes.
Optimizes lookup performance for candidate, voter, booth, and voting queries.

Revision ID: 002_performance_indexes
Revises: 001_initial
Create Date: 2026-08-02
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_performance_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Composite Index for candidate lookups by constituency and party
    op.create_index(
        'idx_candidates_constituency_party',
        'candidates',
        ['constituency_id', 'party'],
        unique=False
    )

    # 2. Composite Index for active voters by constituency
    op.create_index(
        'idx_voters_constituency_status',
        'voters',
        ['constituency_id', 'status'],
        unique=False
    )

    # 3. Composite Index for polling booths by constituency and operational status
    op.create_index(
        'idx_polling_booths_constituency_status',
        'polling_booths',
        ['constituency_id', 'status'],
        unique=False
    )

    # 4. Composite Index for voting record tallying by booth and candidate
    op.create_index(
        'idx_voting_records_booth_candidate',
        'voting_records',
        ['booth_id', 'candidate_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_voting_records_booth_candidate', table_name='voting_records')
    op.drop_index('idx_polling_booths_constituency_status', table_name='polling_booths')
    op.drop_index('idx_voters_constituency_status', table_name='voters')
    op.drop_index('idx_candidates_constituency_party', table_name='candidates')