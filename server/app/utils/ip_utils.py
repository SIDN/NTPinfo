import socket
from ipaddress import ip_address, IPv4Address, IPv6Address
from typing import Optional
import ntplib
import requests
from server.app.utils.load_config_data import get_ipinfo_lite_api_token, get_edns_default_servers
from server.app.utils.validate import is_ip_address


def ref_id_to_ip_or_name(ref_id: int, stratum: int) \
        -> tuple[None, str] | tuple[IPv4Address | IPv6Address, None] | tuple[None, None]:
    """
    Represents a method that converts the reference id to the reference ip or reference name.
    If the stratum is 0 or 1 then we can convert the reference id to it's name (ex: Geostationary Orbit Environment Satellite).
    If the stratum is between 1 and 256 then we can convert the reference id to it's ip.
    If the stratum is greater than 255, then we have an invalid stratum.

    Args:
        ref_id (int): the reference id of the ntp server
        stratum (int): the stratum level of the ntp server

    Returns:
        a tuple of the ip and name of the ntp server. At least one of them is None. If both are None then the stratum is invalid.
    """
    if 0 <= stratum <= 1:  # we can get the name
        # from ntplib, but without "Unidentified reference source" part
        fields = (ref_id >> 24 & 0xff, ref_id >> 16 & 0xff,
                  ref_id >> 8 & 0xff, ref_id & 0xff)
        text = "%c%c%c%c" % fields
        if text in ntplib.NTP.REF_ID_TABLE:
            return None, ntplib.NTP.REF_ID_TABLE[text]
        else:
            return None, text  # ntplib.ref_id_to_text(ref_id, stratum)
    else:
        if stratum < 256:  # we can get an IP address
            return ip_address(socket.inet_ntoa(ref_id.to_bytes(4, 'big'))), None  # 'big' is from big endian
        else:
            return None, None  # invalid stratum!!


def get_ip_family(ip_str: str) -> int:
    """
    This method returns the ip family of the given ip address. It returns 4 if we have an IPv4, and
    it returns 6 if we have an IPv6 address. Otherwise, it raises an exception

    Args:
        ip_str: The ip address

    Returns:
        int: The ip family or an exception if we do not get an IP address

    Raises:
        Exception: If the IP provided is not an IPv4 or IPv6 address.
    """
    ans = is_ip_address(ip_str)
    if ans is None:
        raise Exception("ip_str is not an IP address")
    if ans == "ipv4":
        return 4
    return 6


def get_ip_network_details(ip_str: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    This method gets the ASN, the country code and the continent code of an IP address.

    Args:
        ip_str: The ip address

    Returns:
        tuple[Optional[str], Optional[str], Optional[str]]: the ASN, the country code and the continent
        of an IP address if they can be taken.
    """
    try:
        token: str = get_ipinfo_lite_api_token()
        response = requests.get(f"https://api.ipinfo.io/lite/{ip_str}?token={token}")
        data = response.json()
        asn: str = data.get("asn", None)
        country: str = data.get("country_code", None)
        continent: str = data.get("continent_code", None)
        return asn, country, get_area_of_ip(country, continent)
    except Exception as e:
        print(e)
        return None, None, None


def get_area_of_ip(ip_country: str, ip_continent: Optional[str]) -> str:
    """
    This method tries to get the area of an IP address based on its country and continent.

    Args:
        ip_country (str): The country code of the IP address.
        ip_continent (str): The continent code of the IP address.

    Returns:
        str: The area of an IP address
    """
    # default is WW (world wide)
    if ip_continent is None:
        return "WW"
    area_map = {
        "EU": "North-Central",
        "AF": "South-Central",
        "NA": "West",
        "SA": "West",
        "OC": "South-East"
    }
    # According to RIPE Atlas map, for Asia most of the countries are in South-East, but some are in North-East.
    north_east_countries = ["RU", "KZ", "MN"]
    if ip_continent in area_map:
        return area_map[ip_continent]
    # For Asia
    if ip_country in north_east_countries:
        return "North-East"
    return "South-East"


def get_prefix_from_ip(ip_str: str) -> Optional[str]:
    """
    This method returns the prefix of an IP address.

    Args:
        ip_str: The ip address.

    Returns:
        str: the prefix of an IP address.
    """
    try:
        response = requests.get(f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip_str}")
        response.raise_for_status()
        data = response.json()["data"]
        prefix: str = data.get("resource", None)
        return prefix
    except Exception as e:
        print(e)
        return None


def ip_to_str(ip: Optional[IPv4Address | IPv6Address]) -> Optional[str]:
    """
    Converts an IP address (either IPv4 or IPv6) to its string representation.
    This function takes an `IPv4Address` or `IPv6Address` object and converts it to
    a string. If the input IP is `None`, it returns `None`.

    Args:
        ip (Optional[IPv4Address | IPv6Address]): The IP address to be converted.
            It can be either an `IPv4Address` or `IPv6Address` object, or `None`.

    Returns:
        Optional[str]: The string representation of the IP address, or `None` if the input is `None`.
    """
    return str(ip) if ip is not None else None


def ip_to_location(ip_str: str) -> tuple[float, float]:
    """
    This method returns the latitude and longitude of an IP address by making an API call.
    This method also works with a domain name, but it is recommended to use an IP address.
    (These API calls are unlimited)

    Args:
        ip_str: The IP address.

    Returns:
        tuple[float, float]: latitude and longitude of the provided IP address.

    Raises:
        Exception: If the IP provided is invalid
    """
    response = requests.get(f"https://ipwhois.app/json/{ip_str}")
    data = response.json()
    latitude: float = data.get("latitude", None)
    longitude: float = data.get("longitude", None)
    return latitude, longitude


# import time

# start = time.time()
# print(get_ip_network_details("80.211.238.247"))
# print(get_prefix_from_ip("80.211.238.247"))
# end = time.time()

def get_server_ip() -> IPv4Address | IPv6Address | None:
    """
    Determines the outward-facing IP address of the server by opening a
    dummy UDP connection to a well-known external host (Google DNS).

    Returns:
        Optional[Union[IPv4Address, IPv6Address]]: The server's external IP address
        as an IPv4Address or IPv6Address object, or None if detection fails.

    Raises:
        ValueError: If the detected IP address is not a valid IPv4 or IPv6 address.
    """
    # use a dummy connection to get the outward-facing IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((get_edns_default_servers()[0], 80))
        ip = s.getsockname()[0]
    except Exception as e:
        return None
    finally:
        s.close()
    try:
        return ip_address(ip)
    except ValueError:
        return None
