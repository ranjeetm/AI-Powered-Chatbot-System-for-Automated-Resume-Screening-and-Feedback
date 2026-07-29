import logging

from sqlalchemy import text

from backend.db.database import engine
from backend.db.models import Base
from backend.db import auth_models  # noqa: F401


logger = logging.getLogger(__name__)


def initialize_database():

    logger.info(
        "Initializing database schema"
    )

    with engine.connect() as conn:

        conn.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

        conn.commit()

    Base.metadata.create_all(
        bind=engine
    )

    # create_all does not alter existing tables, so keep compatibility fixes
    # here for local databases created before newer model fields existed.
    with engine.connect() as conn:

        conn.execute(
            text(
                "ALTER TABLE candidate_profiles "
                "ADD COLUMN IF NOT EXISTS resume_summary TEXT"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE candidate_profiles "
                "ADD COLUMN IF NOT EXISTS parsed_at TIMESTAMP"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE candidate_profiles "
                "ADD COLUMN IF NOT EXISTS is_shortlisted BOOLEAN NOT NULL DEFAULT FALSE"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE candidate_profiles "
                "ADD COLUMN IF NOT EXISTS shortlist_updated_at TIMESTAMP"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE candidate_profiles "
                "ADD COLUMN IF NOT EXISTS rejection_feedback TEXT"
            )
        )

        conn.commit()

    logger.info(
        "Database schema initialization complete"
    )
