"""add error to indexstatus enum

Revision ID: 4219645c3a36
Revises: f89598ca91e2
Create Date: 2025-06-05 06:43:24.316892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4219645c3a36'
down_revision = 'f89598ca91e2'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE indexstatus ADD VALUE IF NOT EXISTS 'error'")
    pass


def downgrade():
    pass