from dotenv import load_dotenv
import os
from psycopg_pool import ConnectionPool

load_dotenv()

DB_CONFIG = {
    "dbname" : os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}
# convert DB_CONFIG (a dict) to a connection string
dsn = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
# max_size represents the maximum number of simultaneous database connections
# the pool is allowed to open and manage at once
# additional requests will wait (block) until a connection becomes available, unless a timeout is reached
pool = ConnectionPool(conninfo=dsn, max_size=5)