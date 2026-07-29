import os
import logging
import socket

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)


load_dotenv(
    override=True
)


def resolve_database_url():

    database_url = os.getenv("DATABASE_URL")

    if not database_url:

        raise RuntimeError(
            "DATABASE_URL environment variable is not configured"
        )

    url = make_url(database_url)

    if url.database == "resume_ai":

        local_database_url = os.getenv(
            "LOCAL_DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5433/ats_db"
        )

        logger.warning(
            "DATABASE_URL points to legacy local database 'resume_ai'; using %s",
            make_url(local_database_url).render_as_string(hide_password=True)
        )

        return make_url(local_database_url)

    if url.host != "postgres":

        return url

    try:

        socket.getaddrinfo(
            url.host,
            url.port or 5432
        )

        return url

    except socket.gaierror:

        local_database_url = os.getenv(
            "LOCAL_DATABASE_URL"
        )

        if local_database_url:

            logger.warning(
                "Database host 'postgres' is not resolvable; using LOCAL_DATABASE_URL"
            )

            return make_url(local_database_url)

        logger.warning(
            "Database host 'postgres' is not resolvable; falling back to localhost:5433"
        )

        return url.set(
            host="localhost",
            port=5433
        )


DATABASE_URL = resolve_database_url()

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
