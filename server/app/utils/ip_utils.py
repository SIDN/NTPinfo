import ipaddress
import os
import random
import socket
from ipaddress import ip_address, IPv4Address, IPv6Address
from typing import Optional
import ntplib
import requests

from server.app.utils.load_config_data import get_mask_ipv4, get_mask_ipv6
from server.app.utils.location_resolver import get_asn_for_ip, get_country_for_ip, get_continent_for_ip
from server.app.models.CustomError import InputError
from server.app.utils.load_config_data import get_edns_default_servers
from server.app.utils.validate import is_ip_address
from fastapi import HTTPException, Request


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
    This method returns the IP family of the given IP address. It returns 4 if we have an IPv4, and
    it returns 6 if we have an IPv6 address. Otherwise, it raises an exception.

    Args:
        ip_str: The IP address

    Returns:
        int: The ip family or an exception if we do not get an IP address

    Raises:
        InputError: If the IP provided is not an IPv4 or IPv6 address.
    """
    ans = is_ip_address(ip_str)
    if ans is None:
        raise InputError(f"{ip_str} is not an IP address")
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
        # token: str = get_ipinfo_lite_api_token()
        # response = requests.get(f"https://api.ipinfo.io/lite/{ip_str}?token={token}")
        # data = response.json()
        # asn: str = data.get("asn", None)
        # country: str = data.get("country_code", None)
        # continent: str = data.get("continent_code", None)
        asn: Optional[str] = get_asn_for_ip(ip_str)
        country: Optional[str] = get_country_for_ip(ip_str)
        continent: Optional[str] = get_continent_for_ip(ip_str)
        return asn, country, get_area_of_ip(country, continent)
    except Exception as e:
        print(e)
        return None, None, None


def get_area_of_ip(ip_country: Optional[str], ip_continent: Optional[str]) -> str:
    """
    This method tries to get the area of an IP address based on its country and continent.

    Args:
        ip_country (Optional[str]): The country code of the IP address.
        ip_continent (Optional[str]): The continent code of the IP address.

    Returns:
        str: The area of an IP address
    """
    # default is WW (world wide)
    if ip_continent is None or ip_country is None:
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
        # if it is public
        if get_country_for_ip(ip) is not None:
            return ip_address(ip)
        # if it is private
        ip_public = get_server_ip_from_ipify()
        print(f"fallback to public IP: {ip_to_str(ip_public)}")
        return ip_public
    except ValueError:
        return None


def get_server_ip_from_ipify() -> IPv4Address | IPv6Address | None:
    """
    This method is a fallback to try to get the public IP address of our server from ipify.org

    Returns:
        Optional[IPv4Address | IPv6Address]: The public IP address of our server.
    """
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=3)
        response.raise_for_status()

        data = response.json()
        ip_str: str = data.get("ip", None)
        return ip_address(ip_str.strip())
    except Exception:
        return None


def client_ip_fetch(request: Request) -> str | None:
    """
    Attempts to determine the client's IP address from the request.

    Args:
        request (Request): The FastAPI Request object, containing information
                           about the incoming client request

    Returns:
        str: The determined IP address of the client (or a fallback server IP)
             as a string.

    Raises:
         HTTPException:
            - 503: If neither the client's IP from headers/request nor the fallback server IP can be successfully resolved.
    """
    try:
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client is not None else None)
        if client_ip is None:
            client_ip = ip_to_str(get_server_ip())

        return client_ip
    except Exception as e:
        raise HTTPException(status_code=503, detail="Could not resolve client IP or fallback IP.")


def is_this_ip_anycast(searched_ip: Optional[str]) -> bool:
    """
    This method checks whether an IP address is anycast or not, by searching in the local anycast prefix databases.
    This method would never throw an exception. (If the databases don't exist, it will return False)

    Args:
        searched_ip (Optional[str]): The IP address to check.

    Returns:
        bool: Whether the IP address is anycast or not.
    """
    if searched_ip is None:
        return False
    try:
        ip_family = get_ip_family(searched_ip)
        ip = ip_address(searched_ip)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # get the correct database
        if ip_family == 4:
            file_path = os.path.abspath(os.path.join(current_dir, "..", "..", "anycast-v4-prefixes.txt"))
        else:
            file_path = os.path.abspath(os.path.join(current_dir, "..", "..", "anycast-v6-prefixes.txt"))

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                try:
                    whole_network: ipaddress._BaseNetwork
                    if ip_family == 4:
                        whole_network = ipaddress.IPv4Network(line, strict=False)
                    else:
                        whole_network = ipaddress.IPv6Network(line, strict=False)
                    if ip in whole_network:
                        print(line)
                        return True
                except Exception as e:
                    continue
        return False
    except Exception as e:
        print(f"Error (safe) in is anycast: {e}")
        return False


def randomize_ipv4(ip: IPv4Address) -> IPv4Address:
    """
    Randomizes the host bits of an IPv4 address based on a subnet mask length.

    Args:
        ip (IPv4Address): The IPv4 address to randomize.

    Returns:
        IPv4Address: A new IPv4 address with the same network bits and randomized host bits.
    """
    mask_length = get_mask_ipv4()
    ip_int = int(ip)
    network_mask = (2 ** 32 - 1) << (32 - mask_length) & 0xFFFFFFFF
    network_part = ip_int & network_mask
    random_host = random.getrandbits(32 - mask_length)
    randomized_ip_int = network_part | random_host
    return ipaddress.IPv4Address(randomized_ip_int)


def randomize_ipv6(ip: IPv6Address) -> IPv6Address:
    """
    Randomizes the host bits of an IPv6 address based on a subnet mask length.

    Args:
        ip (IPv6Address): The IPv6 address to randomize.

    Returns:
        IPv6Address: A new IPv6 address with the same network bits and randomized host bits.
    """
    mask_length = get_mask_ipv6()
    ip_int = int(ip)
    network_mask = (2 ** 128 - 1) << (128 - mask_length) & (2 ** 128 - 1)
    network_part = ip_int & network_mask
    random_host = random.getrandbits(128 - mask_length)
    randomized_ip_int = network_part | random_host
    return ipaddress.IPv6Address(randomized_ip_int)
