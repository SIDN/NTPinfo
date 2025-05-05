import pytest
import psycopg
import time

@pytest.fixture(scope="session")
def db_conn():
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
    with conn.cursor() as cur:
        with open("tests/setup-db.sql", "r") as f:
            cur.execute(f.read())
        conn.commit()