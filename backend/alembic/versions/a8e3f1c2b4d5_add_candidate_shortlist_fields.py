"""add candidate shortlist fields

Revision ID: a8e3f1c2b4d5
Revises: 7f4c2d9a1b8e
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "a8e3f1c2b4d5"
down_revision: Union[str, Sequence[str], None] = "7f4c2d9a1b8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE candidate_profiles "
        "ADD COLUMN IF NOT EXISTS is_shortlisted BOOLEAN NOT NULL DEFAULT FALSE"
    )
    op.execute(
        "ALTER TABLE candidate_profiles "
        "ADD COLUMN IF NOT EXISTS shortlist_updated_at TIMESTAMP"
    )
    op.execute(
        "ALTER TABLE candidate_profiles "
        "ADD COLUMN IF NOT EXISTS rejection_feedback TEXT"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE candidate_profiles "
        "DROP COLUMN IF EXISTS rejection_feedback"
    )
    op.execute(
        "ALTER TABLE candidate_profiles "
        "DROP COLUMN IF EXISTS shortlist_updated_at"
    )
    op.execute(
        "ALTER TABLE candidate_profiles "
        "DROP COLUMN IF EXISTS is_shortlisted"
    )
