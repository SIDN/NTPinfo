from ipaddress import IPv6Address, IPv4Address

from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime
from server.app.db.connection import insert_measurement
from server.app.db.connection import get_all_measurements
# from db_fixture import db_conn
# from db_fixture import create_tables
# from db_fixture import db_pool
from app.db.config import pool
from db_fixture import create_tables_pool


# from db_fixture import clean_db_after_each_test


def test_insert_object():
    t1 = PreciseTime(1200, 90)
    t2 = PreciseTime(10002, 2 ** 27)
    t3 = PreciseTime(10003, 10000)
    t4 = PreciseTime(10004, 10000)
    server_details = NtpServerInfo(3, IPv4Address('192.0.2.1'), "local", IPv6Address('2001:db8::1'), "reference")
    times = NtpTimestamps(t1, t2, t3, t4)
    main_details = NtpMainDetails(0.009, 0, 1, 0, "stable")
    extra = NtpExtraDetails(PreciseTime(100000, 0), PreciseTime(100000, 0), 0)

    m = NtpMeasurement(server_details, times, main_details, extra)

    # create_tables_pool(pool)
    insert_measurement(m, pool)

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM measurements")
            count = cur.fetchone()[0]
            assert count == 1

# def test_get_all():
#     print(get_all_measurements())
