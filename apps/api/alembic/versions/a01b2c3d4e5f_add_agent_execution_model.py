"""add agent execution model

Revision ID: a01b2c3d4e5f
Revises: 186a9ec2fd55
Create Date: 2026-08-11 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a01b2c3d4e5f'
down_revision: Union[str, None] = '186a9ec2fd55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create the Enum type first
    op.execute("DROP TYPE IF EXISTS agentexecutionstatus CASCADE")
    # Drop the Enum type first to ensure create_table doesn't fail if it already exists from a failed migration
    op.execute("DROP TYPE IF EXISTS agentexecutionstatus CASCADE")

    op.create_table('agent_executions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('incident_id', sa.UUID(), nullable=False),
        sa.Column('workflow_type', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'TIMED_OUT', 'BLOCKED_BY_POLICY', name='agentexecutionstatus', create_type=False), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requested_by', sa.String(), nullable=True),
        sa.Column('current_step', sa.String(), nullable=True),
        sa.Column('steps_completed', sa.Integer(), nullable=True),
        sa.Column('model_provider', sa.String(), nullable=True),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('prompt_version', sa.String(), nullable=True),
        sa.Column('tool_calls_count', sa.Integer(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('result_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('trace_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_executions_id'), 'agent_executions', ['id'], unique=False)
    op.create_index(op.f('ix_agent_executions_incident_id'), 'agent_executions', ['incident_id'], unique=False)
    op.create_index(op.f('ix_agent_executions_status'), 'agent_executions', ['status'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_agent_executions_status'), table_name='agent_executions')
    op.drop_index(op.f('ix_agent_executions_incident_id'), table_name='agent_executions')
    op.drop_index(op.f('ix_agent_executions_id'), table_name='agent_executions')
    op.drop_table('agent_executions')
    op.execute("DROP TYPE agentexecutionstatus")
