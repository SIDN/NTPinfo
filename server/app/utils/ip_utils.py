import socket
from ipaddress import ip_address, IPv4Address, IPv6Address
from typing import Optional
import ntplib
import requests
from server.app.utils.load_env_vals import get_ipinfo_lite_api_token
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
    #print(ref_id)
    if 0 <= stratum <= 1:  # we can get the name
        return None, ntplib.ref_id_to_text(ref_id, stratum)
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

def get_country_from_ip(ip: str) -> Optional[str]:
    """
    It makes a call to IPinfo to get the country code from this IP.
    This method is for debugging purposes only. (It provides real details, but we use them only to verify the countries)

    Args:
        ip (str): The IP address in string format.

    Returns:
        Optional[str]: The country code or None if IPinfo could not find the country code.
    """
    try:
        token: str = get_ipinfo_lite_api_token()
        response = requests.get(f"https://api.ipinfo.io/lite/{ip}?token={token}")
        data = response.json()
        #print(data)
        ans: str = data.get("country")
        return ans
    except Exception as e:
        print(e)
        return None

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
        return asn, country, continent
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

import time

start = time.time()
print(get_ip_network_details("80.211.238.247"))
print(get_prefix_from_ip("80.211.238.247"))
end = time.time()
#
# print(end - start)
# def ceva():
#     response = requests.get(f"https://stat.ripe.net/measurements/106548996/")
#     data = response.json()
#     pprint.pprint(data)
#
# ceva