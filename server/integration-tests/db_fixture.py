import pytest
import psycopg
import time
from psycopg_pool import ConnectionPool

@pytest.fixture(scope="session")
def db_conn():
    """
    It connects to a database.
    """
    for _ in range(10):
        try:
            conn = psycopg.connect(
                dbname="test_db",
                user="test_user",
                password="test_password",
                host="localhost",
                port="5433"
            )
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError("PostgreSQL container not ready")

    yield conn

    conn.close()

def create_tables(conn):
    """
    It creates the tables in the database.

    Args:
        conn (psycopg.connect): A database connection.
    """
    with conn.cursor() as cur:
        with open("sql-scripts/setup-db.sql", "r") as f:
            cur.execute(f.read())
        conn.commit()

@pytest.fixture(scope="session")
def db_pool():
    dsn = "postgresql://test_user:test_password@localhost:5433/test_db"
    # dsn = "postgresql://test_user:test_password@db:5432/test_db"
    pool = ConnectionPool(conninfo=dsn, max_size=5)

    for _ in range(10):
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError("PostgreSQL container not ready")

    yield pool

    pool.close()


def create_tables_pool(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            with open("sql-scripts/setup-db.sql", "r") as f:
                cur.execute(f.read())
            conn.commit()

@pytest.fixture(scope="function", autouse=True)
def clean_db_after_each_test(db_pool):
    # fixture to truncate tables after each test
    with db_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE measurements, times RESTART IDENTITY CASCADE;")
            conn.commit()

    yield