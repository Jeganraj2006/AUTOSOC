"""Persist node-level agent execution telemetry.

Revision ID: g46f7b8c9d0e
Revises: f35e6a7b8c9d
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa


revision = "g46f7b8c9d0e"
down_revision = "f35e6a7b8c9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agent_executions", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("agent_executions", sa.Column("node_statuses", sa.JSON(), nullable=True))
    op.add_column("agent_executions", sa.Column("node_timestamps", sa.JSON(), nullable=True))
    op.add_column("agent_executions", sa.Column("error_info", sa.JSON(), nullable=True))
    op.add_column("agent_executions", sa.Column("evidence_references", sa.JSON(), nullable=True))
    op.alter_column("agent_executions", "retry_count", server_default=None)


def downgrade() -> None:
    op.drop_column("agent_executions", "evidence_references")
    op.drop_column("agent_executions", "error_info")
    op.drop_column("agent_executions", "node_timestamps")
    op.drop_column("agent_executions", "node_statuses")
    op.drop_column("agent_executions", "retry_count")
