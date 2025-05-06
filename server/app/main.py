from ipaddress import IPv4Address, IPv6Address

from app.models.NtpExtraDetails import NtpExtraDetails
from app.models.NtpMainDetails import NtpMainDetails
from app.models.NtpMeasurement import NtpMeasurement
from app.models.NtpServerInfo import NtpServerInfo
from app.models.NtpTimestamps import NtpTimestamps
from app.models.PreciseTime import PreciseTime

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
