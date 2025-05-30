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

    best_probe_types: dict[str, int] = get_best_probe_types(ip_asn=ip_asn, ip_prefix=ip_prefix, ip_country=ip_country,
                                                            ip_area=ip_area, probes_requested=probes_requested)

    for probe_type, n in best_probe_types.items():
        # instead of a switch, I used a map with lambda methods
        if n > 0:
            # fall back to random probes if the type is invalid
            probes.append(probe_functions.get(probe_type, lambda c: get_random_probes(c))(n))
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
    # the best distribution:
    # 33% 30% 27% 10% 0%
    limit_reached = {
        "asn": False,
        "prefix": False,
        "country": False,
        "area": False,
        "random": False
    }
    probes_wanted = {
        "asn": int(probes_requested * 33 / 100),
        "prefix": int(probes_requested * 30 / 100),
        "country": int(probes_requested * 27 / 100),
        "area": int(probes_requested * 10 / 100),
        "random": 0
    }
    distribution_functions ={
        "asn": lambda i: ([0,30,50,20,0])[i],
        "prefix": lambda i: ([40,0,40,20,0])[i],
        "country": lambda i: ([50,30,0,20,0])[i],
        "area": lambda i: ([20,0,20,0,60])[i],
    }
    # see what inputs we received and with what we start:
    if ip_asn is None:
        limit_reached["asn"] = True
        probes_wanted = distribute_probes_to_others(probes_wanted, limit_reached, distribution_functions["asn"])
    if ip_prefix is not None:
        limit_reached["prefix"] = True
        probes_wanted = distribute_probes_to_others(probes_wanted, limit_reached, distribution_functions["prefix"])
    if ip_country is not None:
        limit_reached["country"] = True
        probes_wanted = distribute_probes_to_others(probes_wanted, limit_reached, distribution_functions["country"])
    if ip_area is not None:
        limit_reached["area"] = True
        probes_wanted = distribute_probes_to_others(probes_wanted, limit_reached, distribution_functions["area"])

    #see what is available on RIPE Atlas
    available_probes_asn = ping_asn_probes(probes_wanted["asn"])
    available_probes_prefix = ping_prefix_probes(probes_wanted["prefix"])
    available_probes_country = ping_country_probes(probes_wanted["country"])

    # prefix (the most expected to fail)
    pbs_to_distribute = probes_wanted["prefix"] - available_probes_prefix
    if pbs_to_distribute > 0:
        # modify probes_wanted
        limit_reached["prefix"] = True
        probes_wanted = distribute_probes_to_others(probes_wanted, limit_reached, lambda: [40,0,40,20,0])
    # asn
    pbs_to_distribute = probes_wanted["asn"] - available_probes_asn
    if pbs_to_distribute > 0:
        # modify probes_wanted
        limit_reached["asn"] = True
        probes_wanted = distribute_probes_to_others(probes_wanted, limit_reached, lambda c: [0,30,50,20,0])
    # country
    pbs_to_distribute = probes_wanted["country"] - available_probes_country
    if pbs_to_distribute > 0:
        # modify probes_wanted
        limit_reached["country"] = True
        probes_wanted = distribute_probes_to_others(probes_wanted, limit_reached, lambda c: [50,30,0,20,0])

    #area would probably not fail as it probably contains more than 100 probes
    #we save the time to ping it here.

    best_probe_types: dict[str, int] = {"random": int(probes_wanted["random"])} # default
    for probe_type, n in probes_wanted.items():
        if n > 0:
            best_probe_types[probe_type] = int(n)
    # if ip_asn is not None:
    #     best_probe_types["asn"] = int(probes_wanted["asn"])
    # if ip_prefix is not None:
    #     best_probe_types["prefix"] = int(probes_wanted["prefix"])
    # if ip_country is not None:
    #     best_probe_types["country"] = int(probes_wanted["country"])
    # if ip_area is not None:
    #     best_probe_types["area"] = int(probes_wanted["area"])

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
def get_area_probes(area: Optional[str], n: int) -> dict:
    """
    This method selects n random probes from all over the world.

    Args:
        area (str): The area of the probes
        n (int): number of probes to select

    Returns:
        dict: the selected probes

    Raises:
        ValueError: If area is not valid
    """
    if area is None:
        raise ValueError("area cannot be None")
    probes = {
        "type": "area",
        "value": area,
        "requested": n
    }
    return probes
def get_asn_probes(ip_asn: Optional[str|int], n: int) -> dict:
    """
    This method selects n probes that belong to the same ASN network.

    Args:
        ip_asn (str|int): the ASN network
        n (int): number of probes to select

    Returns:
        dict: the selected probes

    Raises:
        ValueError: if the ASN network is None
    """
    if ip_asn is None:
        raise ValueError("ip_asn cannot be None")
    probes = {
            "type": "asn",
            "value": ip_asn,
            "requested": n
        }
    return probes
def get_prefix_probes(ip_prefix: Optional[str], n: int) -> dict:
    """
    This method selects n probes that belong to the same ASN network.

    Args:
        ip_prefix (str): the IP prefix family
        n (int): number of probes to select

    Returns:
        dict: the selected probes

    Raises:
        ValueError: if the IP prefix is None
    """
    if ip_prefix is None:
        raise ValueError("ip_prefix cannot be None")
    probes = {
            "type": "prefix",
            "value": ip_prefix,
            "requested": n
        }
    return probes
def get_country_probes(ip_country_code: Optional[str], n: int) -> dict:
    """
    This method selects n probes that belong to the same country.

    Args:
        ip_country_code (str): the country code
        n (int): number of probes to select

    Returns:
        dict: the selected probes

    Raises:
        ValueError: if the country code is None
    """
    if ip_country_code is None:
        raise ValueError("ip_country_code cannot be None")
    probes = {
            "type": "country",
            "value": ip_country_code,
            "requested": n
        }
    return probes

def ping_asn_probes(probes_wanted: int) ->int:
    return 7
def ping_prefix_probes(probes_wanted: int) ->int:
    return 5
def ping_country_probes(probes_wanted: int) ->int:
    return 9

def distribute_probes_to_others(probes_wanted, limited_reach, f) -> dict:
    #asn_pbs+=func(asn_pbs)
    if not limited_reach["asn"]:
        probes_wanted["asn"] += f(0)
    return probes_wanted
#use cases:
# import pprint
# pprint.pprint(get_probes("AS15169","192.2.3.0/8","IT", "West",20))
#ex of output:
# [{'requested': 2, 'type': 'area', 'value': 'WW'},
#  {'requested': 10, 'type': 'asn', 'value': 'AS15169'},
#  {'requested': 10, 'type': 'country', 'value': 'IT'}]