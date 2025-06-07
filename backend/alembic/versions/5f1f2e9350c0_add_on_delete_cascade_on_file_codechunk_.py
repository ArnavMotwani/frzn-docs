"""Add ON DELETE CASCADE on file & codechunk FKs and define ORM relationships

Revision ID: 5f1f2e9350c0
Revises: 4219645c3a36
Create Date: 2025-06-07 09:56:12.077959

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5f1f2e9350c0"
down_revision = "4219645c3a36"
branch_labels = None
depends_on = None


def upgrade():
    # drop the old file→repo FK
    op.drop_constraint("file_repo_id_fkey", "file", type_="foreignkey")
    # re-create with ON DELETE CASCADE
    op.create_foreign_key(
        "file_repo_id_fkey",
        "file",
        "repo",
        ["repo_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # drop the old codechunk→file FK
    op.drop_constraint("codechunk_file_id_fkey", "codechunk", type_="foreignkey")
    # re-create with ON DELETE CASCADE
    op.create_foreign_key(
        "codechunk_file_id_fkey",
        "codechunk",
        "file",
        ["file_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    # drop the cascade FKs
    op.drop_constraint("codechunk_file_id_fkey", "codechunk", type_="foreignkey")
    op.drop_constraint("file_repo_id_fkey", "file", type_="foreignkey")

    # restore the original file→repo FK
    op.create_foreign_key(
        "file_repo_id_fkey",
        "file",
        "repo",
        ["repo_id"],
        ["id"],
    )
    # restore the original codechunk→file FK
    op.create_foreign_key(
        "codechunk_file_id_fkey",
        "codechunk",
        "file",
        ["file_id"],
        ["id"],
    )