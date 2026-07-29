"""add resume summary

Revision ID: 7f4c2d9a1b8e
Revises: 3d6aaf64610d
Create Date: 2026-05-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "7f4c2d9a1b8e"
down_revision: Union[str, Sequence[str], None] = "3d6aaf64610d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE candidate_profiles "
        "ADD COLUMN IF NOT EXISTS resume_summary TEXT"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE candidate_profiles "
        "DROP COLUMN IF EXISTS resume_summary"
    )
