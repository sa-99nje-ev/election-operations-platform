"""
Add request_id column to voting_records for idempotency.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '003_add_request_id'
down_revision = '002_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Add request_id column
    op.add_column('voting_records',
        sa.Column('request_id', UUID(as_uuid=True), nullable=True)
    )
    
    # Create unique index on request_id
    op.create_unique_constraint(
        'uq_voting_records_request_id',
        'voting_records',
        ['request_id']
    )
    
    # For existing records, generate UUIDs
    op.execute("""
        UPDATE voting_records 
        SET request_id = gen_random_uuid() 
        WHERE request_id IS NULL
    """)
    
    # Make request_id NOT NULL after populating
    op.alter_column('voting_records', 'request_id',
        existing_type=UUID(as_uuid=True),
        nullable=False
    )


def downgrade():
    op.drop_constraint('uq_voting_records_request_id', 'voting_records', type_='unique')
    op.drop_column('voting_records', 'request_id')