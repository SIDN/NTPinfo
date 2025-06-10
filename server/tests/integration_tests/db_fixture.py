import pytest
from dotenv import load_dotenv

from server.app.db_config import get_db
from server.app.main import create_app
from server.app.models.Base import Base
from fastapi.testclient import TestClient
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import time

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", "postgres"),
}

TEST_DB_CONFIG = {
    "host": DB_CONFIG["host"],
    "port": DB_CONFIG["port"],
    "user": os.getenv("DB_USER", DB_CONFIG["user"]),
    "password": os.getenv("DB_PASSWORD", DB_CONFIG["password"]),
    "dbname": os.getenv("DB_NAME", "test_db"),
}

def get_connection():
    conn = None
    for _ in range(10):  # retry loop to wait for DB startup
        try:
            conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                dbname="postgres" ,
            )
            conn.autocommit = True
            return conn
        except psycopg2.OperationalError:
            time.sleep(1)
    raise RuntimeError("Could not connect to admin PostgreSQL DB")

@pytest.fixture(scope="session")
def test_db():
    conn = get_connection()
    cur = conn.cursor()

    # Drop and create test database fresh
    cur.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB_CONFIG['dbname']}';")
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['dbname']}")
    cur.execute(f"CREATE DATABASE {TEST_DB_CONFIG['dbname']}")
    cur.close()
    conn.close()

    yield  # test runs here

    # Cleanup after tests
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB_CONFIG['dbname']}';")
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['dbname']}")
    cur.close()
    conn.close()

@pytest.fixture(scope="session")
def engine(test_db):
    url = (
        f"postgresql+psycopg2://{TEST_DB_CONFIG['user']}:"
        f"{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:"
        f"{TEST_DB_CONFIG['port']}/{TEST_DB_CONFIG['dbname']}"
    )
    engine = create_engine(url)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session", autouse=True)
def setup_database(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Clean DB between tests
@pytest.fixture(autouse=True)
def clean_tables(engine):
    # Truncate all tables between tests
    conn = engine.connect()
    trans = conn.begin()
    for table in reversed(Base.metadata.sorted_tables):
        conn.execute(table.delete())
    trans.commit()
    conn.close()

@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    app = create_app(dev=False)
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    app.state.limiter.reset()
    client = TestClient(app)
    yield client
    app.state.limiter.reset()