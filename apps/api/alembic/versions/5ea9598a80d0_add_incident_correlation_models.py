"""Add incident correlation models

Revision ID: 5ea9598a80d0
Revises: 5cc527ff9ff4
Create Date: 2026-08-10 22:48:27.578311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5ea9598a80d0'
down_revision: Union[str, Sequence[str], None] = '5cc527ff9ff4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Update incidents table
    op.add_column('incidents', sa.Column('risk_score', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('incidents', sa.Column('first_seen', sa.DateTime(timezone=True), nullable=True))
    op.add_column('incidents', sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True))
    op.add_column('incidents', sa.Column('alert_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('incidents', sa.Column('event_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('incidents', sa.Column('primary_entities', sa.JSON(), nullable=True))
    op.add_column('incidents', sa.Column('tags', sa.JSON(), nullable=True))
    op.add_column('incidents', sa.Column('correlation_rule_ids', sa.JSON(), nullable=True))
    op.add_column('incidents', sa.Column('candidate_mitre_references', sa.JSON(), nullable=True))
    op.add_column('incidents', sa.Column('resolution_summary', sa.String(length=4000), nullable=True))
    op.add_column('incidents', sa.Column('closure_reason', sa.String(length=1000), nullable=True))
    op.add_column('incidents', sa.Column('false_positive_reason', sa.String(length=1000), nullable=True))

    # 2. Create incident_alerts
    op.create_table('incident_alerts',
        sa.Column('incident_id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.Column('alert_id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.Column('linked_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('correlation_reason', sa.String(length=1000), nullable=True),
        sa.Column('correlation_score', sa.Float(), nullable=True),
        sa.Column('correlation_rule_id', sa.String(length=255), nullable=True),
        sa.Column('id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_alerts_alert_id'), 'incident_alerts', ['alert_id'], unique=False)
    op.create_index(op.f('ix_incident_alerts_incident_id'), 'incident_alerts', ['incident_id'], unique=False)

    # 3. Create incident_events
    op.create_table('incident_events',
        sa.Column('incident_id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('evidence_role', sa.String(length=255), nullable=True),
        sa.Column('linked_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_events_event_id'), 'incident_events', ['event_id'], unique=False)
    op.create_index(op.f('ix_incident_events_incident_id'), 'incident_events', ['incident_id'], unique=False)

    # 4. Create incident_notes
    op.create_table('incident_notes',
        sa.Column('incident_id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.Column('author_id', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_notes_incident_id'), 'incident_notes', ['incident_id'], unique=False)

    # 5. Create incident_timeline
    op.create_table('incident_timeline',
        sa.Column('incident_id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('id', postgresql.UUID(as_uuid=True) if hasattr(postgresql, 'UUID') else sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_timeline_incident_id'), 'incident_timeline', ['incident_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('incident_timeline')
    op.drop_table('incident_notes')
    op.drop_table('incident_events')
    op.drop_table('incident_alerts')
    
    op.drop_column('incidents', 'false_positive_reason')
    op.drop_column('incidents', 'closure_reason')
    op.drop_column('incidents', 'resolution_summary')
    op.drop_column('incidents', 'candidate_mitre_references')
    op.drop_column('incidents', 'correlation_rule_ids')
    op.drop_column('incidents', 'tags')
    op.drop_column('incidents', 'primary_entities')
    op.drop_column('incidents', 'event_count')
    op.drop_column('incidents', 'alert_count')
    op.drop_column('incidents', 'last_seen')
    op.drop_column('incidents', 'first_seen')
    op.drop_column('incidents', 'risk_score')
