from typing import Optional


def get_probes(ip_asn: Optional[str], ip_prefix: Optional[str], ip_country: Optional[str],
               ip_area: Optional[str], probes_requested: int=30) -> list[dict]:
    """
    This method handles all cases regarding what probes we should send.
    This method assumes all inputs are either valid or None. (If there is a type in the input, the measurement
    may be affected)

    Args:
        ip_asn (int): The ASN of the IP address.
        ip_prefix (str): The prefix of the IP address.
        ip_country (str): The country of the IP address.
        ip_area (str): The area of the IP address.
        probes_requested (int): The total number of probes that we will request.

    Returns:
        list[dict]: The list of probes that we will use for the measurement.
    """
    # settings:
    probes: list[dict] = []
    probe_functions = {
        "asn": lambda c: get_asn_probes(ip_asn, c),
        "prefix": lambda c: get_prefix_probes(ip_prefix, c),
        "country": lambda c: get_country_probes(ip_country, c),
        "area": lambda c: get_area_probes(ip_area, c),
        "random": lambda c: get_random_probes(c)
    }

    # the types of probes that we will use. We will use the input parameters to determine which probe types to use.
    # But for now we use a default order. We would change this logic in future

    best_probe_types: dict[str, int] = get_best_probe_types(ip_country, ip_prefix, ip_area,
                                                            ip_country, probes_requested)

    for probe_type, n in best_probe_types.items():
        # instead of a switch, I used a map with lambda methods
        if n > 0:
            probes.append(probe_functions.get(probe_type)(n))
    return probes


def get_best_probe_types(ip_asn: Optional[str], ip_prefix: Optional[str], ip_country: Optional[str],
               ip_area: Optional[str], probes_requested: int=30) -> dict[str, int]:
    """
    This method is responsible for getting the best probes for the measurement. It should return probes that
    are near the NTP server.

    Args:
        ip_asn (int): The ASN of the NTP server IP address.
        ip_prefix (str): The prefix of the NTP server IP address.
        ip_country (str): The country of the NTP server IP address.
        ip_area (str): The area of the NTP server IP address.
        probes_requested (int): The total number of probes that we will request.

    Returns:
        dict[str, int]: The set of probe types and the respective number of probes.
    """
    # for now, we have a default logic! This method is not the final version.
    best_probe_types: dict[str, int] = {"random": 2} # default
    if ip_asn is not None:
        best_probe_types["asn"] = 10
    if ip_prefix is not None:
        best_probe_types["prefix"] = 0
    if ip_country is not None:
        best_probe_types["country"] = 10
    if ip_area is not None:
        best_probe_types["area"] = 0

    return best_probe_types


def get_random_probes(n: int) -> dict:
    """
    This method selects n random probes from all over the world.

    Args:
        n (int): number of probes to select

    Returns:
        dict: the selected probes
    """
    return get_area_probes("WW", n)
def get_area_probes(area: str, n: int) -> dict:
    """
    This method selects n random probes from all over the world.

    Args:
        area (str): The area of the probes
        n (int): number of probes to select

    Returns:
        dict: the selected probes
    """
    probes = {
        "type": "area",
        "value": area,
        "requested": n
    }
    return probes
def get_asn_probes(ip_asn: str|int, n: int) -> dict:
    """
    This method selects n probes that belong to the same ASN network.

    Args:
        ip_asn (str|int): the ASN network
        n (int): number of probes to select

    Returns:
        dict: the selected probes
    """
    probes = {
            "type": "asn",
            "value": ip_asn,
            "requested": n
        }
    return probes
def get_prefix_probes(ip_prefix: str, n: int) -> dict:
    """
    This method selects n probes that belong to the same ASN network.

    Args:
        ip_prefix (str): the IP prefix family
        n (int): number of probes to select

    Returns:
        dict: the selected probes
    """
    probes = {
            "type": "prefix",
            "value": ip_prefix,
            "requested": n
        }
    return probes
def get_country_probes(ip_country_code: str, n: int) -> dict:
    """
    This method selects n probes that belong to the same country.

    Args:
        ip_country_code (str): the country code
        n (int): number of probes to select

    Returns:
        dict: the selected probes
    """
    probes = {
            "type": "country",
            "value": ip_country_code,
            "requested": n
        }
    return probes

#use cases:
# import pprint
# pprint.pprint(get_probes("AS15169","192.2.3.0/8","IT", "West",20))
#ex of output:
# [{'requested': 2, 'type': 'area', 'value': 'WW'},
#  {'requested': 10, 'type': 'asn', 'value': 'AS15169'},
#  {'requested': 10, 'type': 'country', 'value': 'IT'}]