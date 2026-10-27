"""Repair the data-source type enum introduced by the Phase 6 migration.

Revision ID: c02d3e4f5a6b
Revises: b01c2d3e4f5g
Create Date: 2026-10-25
"""

from alembic import op


revision = "c02d3e4f5a6b"
down_revision = "b01c2d3e4f5g"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Replace the legacy three-label enum without discarding source records."""
    op.execute(
        """
        CREATE TYPE datasource_type_enum_v2 AS ENUM (
            'SYNTHETIC', 'HTTP_JSON', 'LINUX_SYSLOG', 'NETWORK_FLOW',
            'WINDOWS_EVENT', 'KUBERNETES_AUDIT', 'AWS_CLOUDTRAIL'
        );
        """
    )
    op.execute(
        """
        ALTER TABLE data_sources
        ALTER COLUMN source_type TYPE datasource_type_enum_v2
        USING (
            CASE source_type::text
                WHEN 'SYSLOG' THEN 'LINUX_SYSLOG'
                WHEN 'API' THEN 'HTTP_JSON'
                WHEN 'AGENT' THEN 'SYNTHETIC'
                ELSE source_type::text
            END
        )::datasource_type_enum_v2;
        """
    )
    op.execute("DROP TYPE datasource_type_enum;")
    op.execute("ALTER TYPE datasource_type_enum_v2 RENAME TO datasource_type_enum;")


def downgrade() -> None:
    """Restore the legacy labels, retaining rows through deterministic mapping."""
    op.execute("CREATE TYPE datasource_type_enum_v1 AS ENUM ('SYSLOG', 'API', 'AGENT');")
    op.execute(
        """
        ALTER TABLE data_sources
        ALTER COLUMN source_type TYPE datasource_type_enum_v1
        USING (
            CASE source_type::text
                WHEN 'LINUX_SYSLOG' THEN 'SYSLOG'
                WHEN 'HTTP_JSON' THEN 'API'
                ELSE 'AGENT'
            END
        )::datasource_type_enum_v1;
        """
    )
    op.execute("DROP TYPE datasource_type_enum;")
    op.execute("ALTER TYPE datasource_type_enum_v1 RENAME TO datasource_type_enum;")
