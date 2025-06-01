import json
from typing import Optional
import requests
from server.app.utils.ip_utils import get_ip_network_details, get_prefix_from_ip, get_ip_family
from server.app.utils.load_env_vals import get_ripe_api_token, get_ripe_account_email
from ripe.atlas.cousteau import ProbeRequest


def get_probes(ntp_server_ip: str, probes_requested: int=30) -> list[dict]:
    """
    This method handles all cases regarding what probes we should send.
    This method assumes all inputs are either valid or None. (If there is a type in the input, the measurement
    may be affected)

    Args:
        ntp_server_ip (str): The IP address of the NTP server.
        probes_requested (int): The total number of probes that we will request.

    Returns:
        list[dict]: The list of probes that we will use for the measurement.
    """
    # get the details. (this will take around 150-200ms)
    ip_family: int = get_ip_family(ntp_server_ip)
    ip_asn, ip_country, ip_area = get_ip_network_details(ntp_server_ip)
    ip_prefix = get_prefix_from_ip(ntp_server_ip)
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
                                                ip_area=ip_area, ip_family=ip_family, probes_requested=probes_requested)

    for probe_type, n in best_probe_types.items():
        # instead of a switch, I used a map with lambda methods
        if n > 0:
            # fall back to random probes if the type is invalid
            probes.append(probe_functions.get(probe_type, lambda c: get_random_probes(c))(n))
    return probes


def get_best_probe_types(ip_asn: Optional[str], ip_prefix: Optional[str], ip_country: Optional[str],
               ip_area: Optional[str], ip_family: int, probes_requested: int=30) -> dict[str, int]:
    """
    This method is responsible for getting the best probes for the measurement. It should return probes that
    are near the NTP server.

    Args:
        ip_asn (int): The ASN of the NTP server IP address.
        ip_prefix (str): The prefix of the NTP server IP address.
        ip_country (str): The country of the NTP server IP address.
        ip_area (str): The area of the NTP server IP address.
        ip_family (int): The family of the NTP server IP address. (4 or 6)
        probes_requested (int): The total number of probes that we will request.

    Returns:
        dict[str, int]: The set of probe types and the respective number of probes.
    """
    # for now, we have a default logic! This method is not the final version.
    # the best distribution:
    # 33% 30% 27% 10% 0%
    max_pbs = 100
    # If the limit for a type is reached, we cannot increase the number of the probes of this type.
    limit_reached = {
        "asn": False,
        "prefix": False,
        "country": False,
        "area": False,
        "random": False
    }
    # probes_wanted = {
    #     "asn": int(probes_requested * 33 / 100),
    #     "prefix": int(probes_requested * 30 / 100),
    #     "country": int(probes_requested * 27 / 100),
    #     "area": int(probes_requested * 10 / 100),
    #     "random": 0
    # }
    # distribution_functions = {
    #     "asn": lambda i: ([0,30,50,20,0])[i],
    #     "prefix": lambda i: ([40,0,40,20,0])[i],
    #     "country": lambda i: ([50,30,0,20,0])[i],
    #     "area": lambda i: ([20,0,20,0,60])[i],
    # }
    #daca un field nu e->available of sa fie 0
    #wanted  13.3,  11.3,   10.2,   4
    #available: 9,     2,    606, 100  -> ans: 9,?,?,?
    #ramase:  4.3,   9.3,       0,  0
    #4.3->distribute equally to the others except random
    #wanted     x    12.73   11.63, 5.43
    #ramase:         10.73
    #split 10.73:               5
    #

    #wanted   13.3,  11.3,   10.2,   4
    #available: 15,     2,    606, 100  -> ans: 9,?,?,?
    probes_wanted_percentages=[0.33, 0.3, 0.27, 0.10, 0.0]
    probes_wanted = [13.3, 11.3, 10.27, 4.2, 0.0]

    # "ans" means how many probes of each type we will ask for
    # type 0 is ASN, type 1 is prefix, type 2 is country code, type 3 is area and type 4 is random
    ans: list[float] = [0, 0, 0, 0, 0] # how many probes
    # wanted     0,  11.3,   10.2,   4
    # available: 3,     2,    606, 100  -> ans: 9,?,?,?
    # remains:    0,   9.3,       0,  0
            # 0 11.3 10.27
            # 3   2   606
    ip_type = "ipv" + str(ip_family)
    # see what inputs we received and with what we start:
    probes_available: list[float] = [0, 0, 0, 0, max_pbs]
    # see what is available on RIPE Atlas
    if ip_asn is not None:
        probes_available[0] = get_available_probes_asn(ip_asn, ip_type)
    if ip_prefix is not None:
        probes_available[1] = get_available_probes_prefix(ip_prefix, ip_type)
    if ip_country is not None:
        probes_available[2] = get_available_probes_country(ip_country, ip_type)
    if ip_area is not None:
        probes_available[3] = max_pbs # there are enough probes in an area for sure.
    # for the types that the available number of probes is less than how many we want:
    for i in range(0,len(probes_wanted)):
        print("step: ",i)
        print(probes_wanted)
        print(probes_available)
        print(ans)
        print("===========")
        if probes_wanted[i] > probes_available[i]: # we want more than we have
            # we need probes from other types, but first take what we found in the desired type
            ans[i] += probes_available[i]
            needed: float = probes_wanted[i] - probes_available[i]
            probes_wanted[i] -= probes_available[i]
            probes_available[i] = 0
            # take from other types and update the available probes
            probes_available, ans = take_from_available_probes(needed, probes_available, ans)
            # we take what we needed
            #ans[i] += needed
            probes_wanted[i] = 0
        else:
            # take the desired number of probes as we have enough
            probes_available[i] -= probes_wanted[i]
            ans[i] += probes_wanted[i]
            probes_wanted[i]=0

        print(probes_wanted)
        print(probes_available)
        print(ans)


    #area would probably not fail as it probably contains more than 100 probes
    #we save the time to ping it here.
    print("the answer is:",ans)
    best_probe_types: dict[str, int] = {"random": int(probes_wanted["random"])} # default
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

def get_available_probes_asn(ip_asn: str, ip_type: str) -> int:
    """
    This method selects n probes that has the same prefix and supports ipv4 or ipv6, it depends on the type.
    Args:
        ip_asn (str): the ASN of the searched network
        ip_type (str): the IP type (ipv4 or ipv6). (not case-sensitive)
    Returns:
        int: the number of available probes
    """
    # in wsl, this command would be for example:
    # ripe-atlas probe-search --prefix NL --status 1 --tag system-ipv4-works
    ip_asn_number=int(ip_asn[2:])
    print("asn number:", ip_asn_number)
    filters = {
        "asn": ip_asn_number,
        "status": 1,  # Connected probes
        "tags": f"system-{ip_type.lower()}-works",
    }
    probes = ProbeRequest(
        return_objects=False,
        page_size=1, # we are only interested in the number. If you want the id of the probes, use 100 here
        **filters,
    )
    try:
        #this fetches after the first request
        next(probes) # we need to trigger the probes because "probes" does not get populated immediately.
    except StopIteration:
        return 0 # error
    ans: int = probes.total_count
    return ans
def get_available_probes_prefix(ip_prefix: str, ip_type: str) -> int:
    """
    This method selects n probes that has the same prefix and supports ipv4 or ipv6, it depends on the type.
    Args:
        ip_prefix (str): the ip_prefix of the searched network
        ip_type (str): the IP type (ipv4 or ipv6). It should be lowercase.
    Returns:
        int: the number of available probes
    """
    # in wsl, this command would be for example:
    # ripe-atlas probe-search --prefix NL --status 1 --tag system-ipv4-works
    prefix_type="prefix_v4" if ip_type == "ipv4" else "prefix_v6"
    filters = {
        prefix_type: ip_prefix,
        "status": 1,  # Connected probes
        "tags": f"system-{ip_type.lower()}-works",
    }
    probes = ProbeRequest(
        return_objects=False,
        page_size=1, # we are only interested in the number. If you want the id of the probes, use 100 here
        **filters,
    )
    try:
        #this fetches after the first request
        next(probes) # we need to trigger the probes because "probes" does not get populated immediately.
    except StopIteration:
        return 0 # error
    ans: int = probes.total_count
    return ans
def get_available_probes_country(country_code: str, ip_type: str) -> int:
    """
    This method selects n probes that belong to the same country and supports ipv4 or ipv6, it depends on the type.
    Args:
        country_code (str): the country code
        ip_type (str): the IP type (ipv4 or ipv6). It should be lowercase.
    Returns:
        int: the number of available probes
    """
    # in wsl, this command would be for example:
    # ripe-atlas probe-search --country NL --status 1 --tag system-ipv4-works
    filters = {
        "country_code": country_code,
        "status": 1,  # Connected probes
        "tags": f"system-{ip_type.lower()}-works",
    }
    probes = ProbeRequest(
        return_objects=False,
        #fields="id",
        page_size=1, # we are only interested in the number. If you want the id of the probes, use 100 here
        **filters,
    )
    try:
        #this fetches after the first request
        next(probes) # we need to trigger the probes because "probes" does not get populated immediately.
    except StopIteration:
        return 0 # error
    # print(probe_list)
    ans: int = probes.total_count
    return ans

def take_from_available_probes(needed: float, probes_available: list[float],
                               ans: list[float]) -> tuple[list[float], list[float]]:
    # for clarity, "needed" means how many probes we need to take from other categories
    ans_for_index=0
    for i in range(0,len(probes_available)):
        # if we have something there that we could take
        if probes_available[i] > 0:
            if probes_available[i] < needed: # if we have less than we want, take everything from that source
                # we will take "probes_available[i]" probes from type i
                ans[i] += probes_available[i]
                # subtract what we found
                needed -= probes_available[i]
                # we emptied this source
                probes_available[i] = 0
            else:
                # we have more than "needed" in probes_available[i]
                # we will take "needed" probes from type i
                ans[i] += needed
                # remove them from available
                probes_available[i] -= needed
                needed=0
                # stop as we finished our job there
                break
    if needed > 0:
        raise Exception("Not enough probes available")
    # ans_for_index would always be the initial value of needed
    return probes_available, ans

import time

start = time.time()
print(get_available_probes_asn("AS9009","ipv4"))
print(get_available_probes_prefix("80.211.224.0/16","ipv4"))
print(get_available_probes_country("NL","ipv4"))
get_best_probe_types("AS9009","80.211.224.0/20","NL","da",4)
end = time.time()
print(end - start)


def ping_asn_probes(ntp_server_ip: str, probes_wanted: int) ->int:
    return 2
def ping_prefix_probes(probes_wanted: int) ->int:
    return 5
def ping_country_probes(probes_wanted: int) ->int:
    return 9


#use cases:
# import pprint
# pprint.pprint(get_probes("AS15169","192.2.3.0/8","IT", "West",20))
#ex of output:
# [{'requested': 2, 'type': 'area', 'value': 'WW'},
#  {'requested': 10, 'type': 'asn', 'value': 'AS15169'},
#  {'requested': 10, 'type': 'country', 'value': 'IT'}]