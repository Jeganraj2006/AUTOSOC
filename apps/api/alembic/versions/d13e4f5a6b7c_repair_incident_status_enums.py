"""Repair incident enums left at their Phase 5 labels.

Revision ID: d13e4f5a6b7c
Revises: c02d3e4f5a6b
Create Date: 2026-10-25
"""

from alembic import op


revision = "d13e4f5a6b7c"
down_revision = "c02d3e4f5a6b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Use the labels declared by the current incident models, preserving rows."""
    op.execute(
        "CREATE TYPE incident_status_enum_v2 AS ENUM "
        "('NEW', 'TRIAGED', 'INVESTIGATING', 'AWAITING_APPROVAL', "
        "'CONTAINED', 'RESOLVED', 'CLOSED', 'FALSE_POSITIVE');"
    )
    op.execute(
        """
        ALTER TABLE incidents ALTER COLUMN status TYPE incident_status_enum_v2
        USING (CASE status::text
            WHEN 'TRIAGE' THEN 'TRIAGED'
            WHEN 'CONTAINMENT' THEN 'CONTAINED'
            WHEN 'ERADICATION' THEN 'INVESTIGATING'
            WHEN 'RECOVERY' THEN 'RESOLVED'
            ELSE status::text
        END)::incident_status_enum_v2;
        """
    )
    op.execute("DROP TYPE incident_status_enum;")
    op.execute("ALTER TYPE incident_status_enum_v2 RENAME TO incident_status_enum;")
    op.execute("CREATE TYPE incident_severity_enum_v2 AS ENUM ('INFORMATIONAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL');")
    op.execute(
        "ALTER TABLE incidents ALTER COLUMN severity TYPE incident_severity_enum_v2 "
        "USING severity::text::incident_severity_enum_v2;"
    )
    op.execute("DROP TYPE incident_severity_enum;")
    op.execute("ALTER TYPE incident_severity_enum_v2 RENAME TO incident_severity_enum;")


def downgrade() -> None:
    """Restore the original Phase 5 labels if an explicit downgrade is required."""
    op.execute("CREATE TYPE incident_status_enum_v1 AS ENUM ('NEW', 'TRIAGE', 'CONTAINMENT', 'ERADICATION', 'RECOVERY', 'CLOSED', 'FALSE_POSITIVE');")
    op.execute(
        """
        ALTER TABLE incidents ALTER COLUMN status TYPE incident_status_enum_v1
        USING (CASE status::text
            WHEN 'TRIAGED' THEN 'TRIAGE'
            WHEN 'AWAITING_APPROVAL' THEN 'TRIAGE'
            WHEN 'CONTAINED' THEN 'CONTAINMENT'
            WHEN 'INVESTIGATING' THEN 'ERADICATION'
            WHEN 'RESOLVED' THEN 'RECOVERY'
            ELSE status::text
        END)::incident_status_enum_v1;
        """
    )
    op.execute("DROP TYPE incident_status_enum;")
    op.execute("ALTER TYPE incident_status_enum_v1 RENAME TO incident_status_enum;")
    op.execute("CREATE TYPE incident_severity_enum_v1 AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');")
    op.execute(
        "ALTER TABLE incidents ALTER COLUMN severity TYPE incident_severity_enum_v1 "
        "USING (CASE severity::text WHEN 'INFORMATIONAL' THEN 'LOW' ELSE severity::text END)::incident_severity_enum_v1;"
    )
    op.execute("DROP TYPE incident_severity_enum;")
    op.execute("ALTER TYPE incident_severity_enum_v1 RENAME TO incident_severity_enum;")
