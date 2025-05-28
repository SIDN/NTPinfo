from typing import Optional
import requests

from app.utils.load_env_vals import get_ipinfo_lite_api_token
from app.utils.validate import is_ip_address



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

def get_country_asn_from_ip(ip_str: str) -> Optional[tuple[str, str]]:
    """
    This method returns the country code and the ASN of an IP address.

    Args:
        ip_str: The ip address

    Returns:
        Optional[tuple[str, str]]: the country code and the ASN of an IP address or None if the request fails.
    """
    try:
        token: str = get_ipinfo_lite_api_token()
        response = requests.get(f"https://api.ipinfo.io/lite/{ip_str}?token={token}")
        data = response.json()
        country: str = data.get("country_code")
        asn: str = data.get("asn")
        return country, asn
    except Exception as e:
        print(e)
        return None

def get_prefix_from_ip(ip_str: str) -> str:
    """
    This method returns the prefix of an IP address.

    Args:
        ip_str: The ip address.

    Returns:
        str: the prefix of an IP address.
    """
    response = requests.get(f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip_str}")
    data = response.json()
    prefix = data["data"].get("resource")
    return prefix