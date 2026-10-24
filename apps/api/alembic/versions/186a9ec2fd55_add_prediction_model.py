"""Add Prediction model

Revision ID: 186a9ec2fd55
Revises: 8c3534cfb8cb
Create Date: 2026-08-11 10:32:56.653493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '186a9ec2fd55'
down_revision: Union[str, Sequence[str], None] = '8c3534cfb8cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'predictions',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('incidents.id'), index=True, nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('is_stale', sa.Boolean(), nullable=True, default=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('attack_version', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('observed_techniques', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('predicted_next_techniques', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('predicted_target', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('path_continuation', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('escalation_risk_score', sa.Float(), nullable=True),
        sa.Column('evidence_summary', sa.String(), nullable=True),
        sa.Column('limitations', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('predictions')
