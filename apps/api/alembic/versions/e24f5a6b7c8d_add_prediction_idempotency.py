"""Add durable prediction idempotency.

Revision ID: e24f5a6b7c8d
Revises: d13e4f5a6b7c
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa


revision = "e24f5a6b7c8d"
down_revision = "d13e4f5a6b7c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Preserve historical rows, including previously duplicated predictions. They
    # receive unique legacy identities; all new writes use canonical SHA-256 keys.
    op.add_column("predictions", sa.Column("input_fingerprint", sa.String(length=64), nullable=True))
    op.execute("UPDATE predictions SET input_fingerprint = md5('legacy:' || id::text) WHERE input_fingerprint IS NULL")
    op.alter_column("predictions", "input_fingerprint", nullable=False)
    op.create_unique_constraint(
        "uq_predictions_logical_input",
        "predictions",
        ["incident_id", "model_name", "model_version", "attack_version", "input_fingerprint"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_predictions_logical_input", "predictions", type_="unique")
    op.drop_column("predictions", "input_fingerprint")
