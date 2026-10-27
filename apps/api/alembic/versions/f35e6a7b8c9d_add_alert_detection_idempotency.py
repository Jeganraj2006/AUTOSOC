"""Add stable detection identities to alerts.

Revision ID: f35e6a7b8c9d
Revises: e24f5a6b7c8d
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f35e6a7b8c9d"
down_revision = "e24f5a6b7c8d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("alerts", sa.Column("detection_id", postgresql.UUID(as_uuid=True), nullable=True))
    # Keep all historical alerts. Each receives a deterministic legacy UUID
    # derived from its primary key before the uniqueness constraint is added.
    op.execute(
        """
        UPDATE alerts
        SET detection_id = (
          substr(md5('legacy-alert:' || id::text), 1, 8) || '-' ||
          substr(md5('legacy-alert:' || id::text), 9, 4) || '-' ||
          substr(md5('legacy-alert:' || id::text), 13, 4) || '-' ||
          substr(md5('legacy-alert:' || id::text), 17, 4) || '-' ||
          substr(md5('legacy-alert:' || id::text), 21, 12)
        )::uuid
        WHERE detection_id IS NULL
        """
    )
    op.alter_column("alerts", "detection_id", nullable=False)
    op.create_unique_constraint("uq_alerts_detection_id", "alerts", ["detection_id"])
    op.create_index("ix_alerts_detection_id", "alerts", ["detection_id"])


def downgrade() -> None:
    op.drop_index("ix_alerts_detection_id", table_name="alerts")
    op.drop_constraint("uq_alerts_detection_id", "alerts", type_="unique")
    op.drop_column("alerts", "detection_id")
