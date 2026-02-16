"""add savings goal and transaction fields

Revision ID: 1b2f6f0e9abc
Revises: 9373076bb85f
Create Date: 2026-02-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1b2f6f0e9abc"
down_revision = "9373076bb85f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("savings_goal", sa.Float(), nullable=False, server_default="0"))
    op.add_column("transaction", sa.Column("note", sa.String(length=255), nullable=True))
    op.add_column("transaction", sa.Column("occurred_on", sa.Date(), nullable=True))

    op.execute("UPDATE transaction SET occurred_on = DATE(created_at) WHERE occurred_on IS NULL")
    op.alter_column("transaction", "occurred_on", nullable=False)

    op.alter_column("user", "savings_goal", server_default=None)


def downgrade():
    op.drop_column("transaction", "occurred_on")
    op.drop_column("transaction", "note")
    op.drop_column("user", "savings_goal")
