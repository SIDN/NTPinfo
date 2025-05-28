import os
from typing import Optional

from dotenv import load_dotenv
import requests

from app.utils.validate import is_ip_address


def get_ip_family(ip_str: str) -> int:
    ans = is_ip_address(ip_str)
    if ans is None:
        raise Exception("ip_str is not an IP address")
    if ans == "ipv4":
        return 4
    return 6


load_dotenv()
def get_country_from_ip(ip: str) -> str:
    """
    It makes a call to IPinfo to get the country code from this IP.
    This method is for debugging purposes only. (It provides real details, but we use them only to verify the countries)

    Args:
        ip (str): The IP address in string format.

    Returns:
        str: The country code or "Unknown" if IPinfo could not find the country code.
    """
    try:
        token: str = os.getenv('IPINFO_LITE_API_TOKEN')
        response = requests.get(f"https://api.ipinfo.io/lite/{ip}?token={token}")
        data = response.json()
        #print(data)
        ans: str = data.get("country", "Unknown")
        return ans
    except Exception as e:
        print(e)
        return "Problem"

def get_country_asn_from_ip(ip: str) -> Optional[tuple[str, str]]:
    try:
        token: str = os.getenv('IPINFO_LITE_API_TOKEN')
        response = requests.get(f"https://api.ipinfo.io/lite/{ip}?token={token}")
        data = response.json()
        country: str = data.get("country_code", "Unknown")
        asn: str = data.get("asn", "Unknown")
        return country, asn
    except Exception as e:
        print(e)
        return None

def get_routing_info(ip):
    response = requests.get(f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}")
    data = response.json()
    print(data)
    asn = data["data"].get("asns", [None])[0]
    prefix = data["data"].get("prefix")
    country = data["data"].get("located_resources", [{}])[0].get("country")

    return asn, prefix, country


def get_routing_info2(ip):
    response = requests.get(f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}")
    data = response.json()

    asn = data["data"].get("asns", [{}])[0].get("asn")
    prefix = data["data"].get("resource")  # Use the aligned prefix
    country = data["data"].get("located_resources", [{}])[0].get("country")

    return asn, prefix, country
#print(get_routing_info2("83.25.24.10"))