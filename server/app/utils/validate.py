import ipaddress
from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv6Address
import dns.name

def is_valid_domain_name(domain_name: str) -> bool:
    """
    This method verifies if the given string could be a valid domain name. It verifies the syntax.
    It offers only a basic validation of the syntax. It is just enough for a dns to consider it.

    Args:
        domain_name (str): The string to check.
    Returns:
        bool: True if the string could be a valid domain name, False otherwise.
    """
    try:
        dns.name.from_text(domain_name)
        return True
    except Exception:
        return False

def is_ip_address(ip_str: str) -> str | None:
    """
    It verifies if the given string is a valid IPv4 or IPv6 address. If not, it returns None.

    Args:
        ip_str (str): ip address
    Returns:
        str | None
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        if isinstance(ip, ipaddress.IPv4Address):
            return "ipv4"
        else:
            if isinstance(ip, ipaddress.IPv6Address):
                return "ipv6"
        # this part is unreachable (Well, at least until another ip version would be created)
        # return None
    except ValueError:
        return None


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensures that a given `datetime` object is timezone-aware and in UTC.

    This function checks if the provided datetime is naive (i.e., has no timezone info).
    If so, it assigns UTC as the timezone. If it already has a timezone, it converts it to UTC.

    Args:
        dt (datetime): A Python `datetime` object, either naive or timezone-aware.

    Returns:
        datetime: A timezone-aware `datetime` object in UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_ip(ip_str: str) -> IPv4Address | IPv6Address | None:
    """
    Parses and validates a string as an IPv4 or IPv6 address.

    Attempts to interpret the provided string as a valid IP address using `ipaddress.ip_address()`.
    If successful, prints the IP and its version. If invalid, prints an error message.

    Args:
        ip_str (str): The IP address in string format (e.g., "192.168.0.1" or "::1").

    Returns:
        ipaddress.IPv4Address | ipaddress.IPv6Address | None:
            - A valid `IPv4Address` or `IPv6Address` object if parsing succeeds.
            - `None` if the string is not a valid IP address.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        print(f"Valid IP: {ip} (Version {ip.version})")
        return ip
    except ValueError:
        print("Invalid IP address")
        return None
