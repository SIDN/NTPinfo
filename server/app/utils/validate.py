import ipaddress
from datetime import datetime, timezone


def is_ip_address(ip_str: str) -> str | None:
    """
    It verifies if the given string is a valid IPv4 or IPv6 address. If not, it returns None.
    args:
        ip_str (str): ip address
    returns:
        str | None
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        if isinstance(ip, ipaddress.IPv4Address):
            return "ipv4"
        else:
            if isinstance(ip, ipaddress.IPv6Address):
                return "ipv6"
        # this part is unreachable (Well, at least another ip version would be created
        # return None
    except ValueError:
        return None


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        print(f"Valid IP: {ip} (Version {ip.version})")
        return ip
    except ValueError:
        print("Invalid IP address")
        return None
