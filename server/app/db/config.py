from dotenv import load_dotenv
import os
from psycopg_pool import ConnectionPool

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

pool = ConnectionPool(conninfo=dsn, max_size = 20)
"""
Creates a PostgreSQL connection pool using `psycopg_pool.ConnectionPool`.

Args:
    conninfo (str): The DSN used to connect to the PostgreSQL server.
    max_size (int): The maximum number of simultaneous database connections allowed.

Details:
    - `max_size=5` limits the number of concurrent active database connections to 5.
    - If more than 5 requests require a connection at the same time, additional requests will wait (block)
      until a connection becomes available or a timeout occurs.
    - This pool improves performance and resource management by reusing connections instead of
      constantly opening/closing new ones.
"""
