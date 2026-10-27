"""Add indexes for paged audit and response read models.

Revision ID: h57g8c9d0e1f
Revises: g46f7b8c9d0e
Create Date: 2026-10-26
"""

from alembic import op


revision = "h57g8c9d0e1f"
down_revision = "g46f7b8c9d0e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_audit_logs_created_at_id", "audit_logs", ["created_at", "id"])
    op.create_index("ix_audit_logs_action_created_at", "audit_logs", ["action", "created_at"])
    op.create_index("ix_response_recommendations_status_created_at", "response_recommendations", ["status", "created_at"])
    op.create_index("ix_response_recommendations_created_by_created_at", "response_recommendations", ["created_by", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_response_recommendations_created_by_created_at", table_name="response_recommendations")
    op.drop_index("ix_response_recommendations_status_created_at", table_name="response_recommendations")
    op.drop_index("ix_audit_logs_action_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_created_at_id", table_name="audit_logs")
