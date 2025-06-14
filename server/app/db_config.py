from typing import Generator, Any

from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()
"""
Loads environment variables from a `.env` file into the process's environment.

This allows secure configuration of database credentials (e.g., DB_USER, DB_PASSWORD)
without hardcoding them into the source code.
"""
DB_CONFIG = {
    "dbname": os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

"""
Dictionary holding PostgreSQL connection details.

Each value is loaded from environment variables to enhance security and flexibility:
    - DB_NAME: Name of the PostgreSQL database.
    - DB_USER: Username for authentication.
    - DB_PASSWORD: Password for authentication.
    - DB_HOST: Hostname or IP address of the database server.
    - DB_PORT: Port number on which the database server is listening.
    
"""

dsn = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
"""
Constructs a PostgreSQL connection string (DSN) from the `DB_CONFIG` dictionary.

This string follows the format:
    postgresql://<user>:<password>@<host>:<port>/<dbname>
It is required by most PostgreSQL drivers, including `psycopg`, to initiate connections.
"""

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def init_engine() -> Engine:
    """
    Creates the engine necessary for the SQLAlchemy connection, as well as the session maker.
    Returns:
        Engine: The engine for the SQLAlchemy connection (necessary for creating the tables later).
    """
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(dsn)
        _SessionLocal = sessionmaker(bind=_engine)
    return _engine


def get_db() -> Generator[Session, None, None]:
    """
    Returns the current database session.
    Yields:
        Session: The current database session.
    """
    if _SessionLocal is None:
        init_engine()

    assert _SessionLocal is not None
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
