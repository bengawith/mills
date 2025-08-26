"""
Add summary tables for background data processing.

This migration creates tables for pre-computed analytical data
to improve performance of dashboard endpoints.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_summary_tables'
down_revision = '4040160e3420'
branch_labels = None
depends_on = None

def upgrade():
    # Create analytical data summary table
    op.create_table('analytical_data_summary',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('machine_id', sa.String(), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('shift', sa.String(), nullable=True, index=True),
        sa.Column('day_of_week', sa.String(), nullable=True),
        
        # Aggregated metrics
        sa.Column('total_events', sa.Integer(), default=0),
        sa.Column('productive_time_seconds', sa.Float(), default=0),
        sa.Column('downtime_seconds', sa.Float(), default=0),
        sa.Column('setup_time_seconds', sa.Float(), default=0),
        sa.Column('total_cuts', sa.Integer(), default=0),
        
        # Calculated metrics
        sa.Column('utilization_percentage', sa.Float(), default=0),
        sa.Column('oee_percentage', sa.Float(), default=0),
        sa.Column('availability_percentage', sa.Float(), default=0),
        sa.Column('performance_percentage', sa.Float(), default=0),
        sa.Column('quality_percentage', sa.Float(), default=0),
        
        # Maintenance data
        sa.Column('maintenance_tickets_count', sa.Integer(), default=0),
        sa.Column('critical_tickets_count', sa.Integer(), default=0),
        
        # Production data
        sa.Column('production_runs_count', sa.Integer(), default=0),
        sa.Column('products_produced', sa.String(), nullable=True),  # JSON list
        
        # Metadata
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data_quality_score', sa.Float(), default=1.0),
        
        # Ensure unique combinations
        sa.UniqueConstraint('machine_id', 'date', 'shift', name='unique_machine_date_shift')
    )
    
    # Create machine status cache table
    op.create_table('machine_status_cache',
        sa.Column('machine_id', sa.String(), primary_key=True),
        sa.Column('machine_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_status', sa.String(), default='unknown'),  # active, idle, down, maintenance
        sa.Column('last_cut_count', sa.Integer(), default=0),
        sa.Column('daily_cuts', sa.Integer(), default=0),
        sa.Column('daily_utilization', sa.Float(), default=0),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False)
    )
    
    # Create downtime summary table
    op.create_table('downtime_summary',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('machine_id', sa.String(), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('downtime_category', sa.String(), nullable=False, index=True),
        sa.Column('total_downtime_seconds', sa.Float(), default=0),
        sa.Column('event_count', sa.Integer(), default=0),
        sa.Column('average_event_duration', sa.Float(), default=0),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        
        sa.UniqueConstraint('machine_id', 'date', 'downtime_category', name='unique_downtime_summary')
    )

def downgrade():
    op.drop_table('downtime_summary')
    op.drop_table('machine_status_cache')
    op.drop_table('analytical_data_summary')
