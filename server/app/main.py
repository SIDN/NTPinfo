from ipaddress import IPv4Address, IPv6Address

from app.db.connection import get_measurements_timestamps
from app.models.NtpExtraDetails import NtpExtraDetails
from app.models.NtpMainDetails import NtpMainDetails
from app.models.NtpMeasurement import NtpMeasurement
from app.models.NtpServerInfo import NtpServerInfo
from app.models.NtpTimestamps import NtpTimestamps
from app.models.PreciseTime import PreciseTime
from app.db.config import pool
from datetime import datetime, timezone

print("Hello World!")


def measure(ip: IPv4Address | IPv6Address, dn: str) -> NtpMeasurement:
    t1 = PreciseTime(10000, 0)
    t2 = PreciseTime(10002, 2 ** 27)
    t3 = PreciseTime(10003, 10000)
    t4 = PreciseTime(10004, 10000)
    server_details = NtpServerInfo(3, IPv4Address('192.0.2.1'), "local", IPv6Address('2001:db8::1'), "reference")
    times = NtpTimestamps(t1, t2, t3, t4)
    main_details = NtpMainDetails(0.009, 0, 1, 0, "stable")
    extra = NtpExtraDetails(PreciseTime(100000, 0), PreciseTime(100000, 0), 0)

    m = NtpMeasurement(server_details, times, main_details, extra)
    return m


def datetime_to_ntp_time(dt: datetime) -> PreciseTime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    ntp_epoch = datetime(1900, 1, 1, tzinfo=timezone.utc)
    delta = (dt - ntp_epoch).total_seconds()  # float

    ntp_seconds = int(delta)
    ntp_fraction = int((delta - ntp_seconds) * (2 ** 32))

    return PreciseTime(ntp_seconds, ntp_fraction)


def fetch_historic_data_with_timestamps(ip: IPv4Address | IPv6Address, dn: str, start: datetime, end: datetime):
    # start_pt = datetime_to_ntp_time(start)
    # end_pt = datetime_to_ntp_time(end)
    start_pt = PreciseTime(450, 20)
    end_pt = PreciseTime(1200, 100)
    return get_measurements_timestamps(pool, ip, start_pt, end_pt)
