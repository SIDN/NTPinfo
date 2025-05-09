from ipaddress import IPv4Address, IPv6Address

from server.app.utils.validate import is_ip_address
from server.app.utils.validate import ensure_utc
from server.app.utils.validate import parse_ip
from datetime import datetime, timezone, tzinfo, timedelta


def test_validate():
    assert is_ip_address("1.2.3") is None
    assert is_ip_address("adfsdgh") is None
    assert is_ip_address("0.0.0.0.0.0") is None
    assert is_ip_address("123.45.67.89") == "ipv4"
    assert is_ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == "ipv6"
    assert is_ip_address("2001:db8:85a3::8a2e:370:7334") == "ipv6"


def test_ensure_utc():
    assert (ensure_utc(datetime(2025, 7, 31, 10, 20))
            == datetime(2025, 7, 31, 10, 20, tzinfo=timezone.utc))
    assert (ensure_utc(datetime(2025, 7, 31, 10, 20, tzinfo=timezone(timedelta(hours=2))))
            == datetime(2025, 7, 31, 8, 20, tzinfo=timezone.utc))
    assert (ensure_utc(datetime(2025, 7, 31, 10, 20, tzinfo=timezone(timedelta(hours=-4))))
            == datetime(2025, 7, 31, 14, 20, tzinfo=timezone.utc))


def test_parse_ip():
    assert parse_ip("123.45.67.89") == IPv4Address("123.45.67.89")
    assert parse_ip("2001:db8:85a3::8a2e:370:7334") == IPv6Address("2001:db8:85a3::8a2e:370:7334")
    assert parse_ip("123.45.67.89.69") is None
    assert parse_ip("2001:db8:85a3::8a2e:370:7334::3442") is None
