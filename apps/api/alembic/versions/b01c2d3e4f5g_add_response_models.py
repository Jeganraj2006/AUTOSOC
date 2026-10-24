"""add response models

Revision ID: b01c2d3e4f5g
Revises: a01b2c3d4e5f
Create Date: 2026-08-11 12:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b01c2d3e4f5g'
down_revision = 'a01b2c3d4e5f'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # response_recommendations
    op.create_table(
        'response_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('playbook_id', sa.String(), nullable=False),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_reference', sa.String(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('expected_benefit', sa.Text(), nullable=True),
        sa.Column('evidence_references', sa.JSON(), nullable=True),
        sa.Column('impact', sa.String(), nullable=False),
        sa.Column('reversibility', sa.String(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True, default=3),
        sa.Column('approval_required', sa.Boolean(), nullable=True, default=True),
        sa.Column('rollback_available', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='proposed'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # response_approvals
    op.create_table(
        'response_approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('requested_by', sa.String(), nullable=False),
        sa.Column('reviewer', sa.String(), nullable=True),
        sa.Column('decision', sa.String(), nullable=False, default='pending'),
        sa.Column('decision_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('expiration', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['recommendation_id'], ['response_recommendations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # response_executions
    op.create_table(
        'response_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approval_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('playbook_id', sa.String(), nullable=False),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('mode', sa.String(), nullable=False),
        sa.Column('target', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='queued'),
        sa.Column('executor', sa.String(), nullable=False),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('verification_status', sa.String(), nullable=True),
        sa.Column('rollback_status', sa.String(), nullable=True),
        sa.Column('error_category', sa.String(), nullable=True),
        sa.Column('idempotency_key', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['approval_id'], ['response_approvals.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recommendation_id'], ['response_recommendations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('idempotency_key')
    )

def downgrade() -> None:
    op.drop_table('response_executions')
    op.drop_table('response_approvals')
    op.drop_table('response_recommendations')
