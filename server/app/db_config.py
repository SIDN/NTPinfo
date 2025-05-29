from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
engine = create_engine(dsn, pool_size=20, max_overflow=10)
"""
Creates the engine for the SQLAlchemy connection.
This is where the connection starts, the engine allows us to create a session.
"""
SessionLocal = sessionmaker(bind=engine)
