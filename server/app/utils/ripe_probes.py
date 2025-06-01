import json
import pprint
from typing import TypeVar, Union, List, Tuple
from typing import Optional
import requests
from server.app.utils.ip_utils import get_ip_network_details, get_prefix_from_ip, get_ip_family
from server.app.utils.load_env_vals import get_ripe_api_token, get_ripe_account_email
from ripe.atlas.cousteau import ProbeRequest


T = TypeVar('T', int, float) # float or int


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

    Raises:
        Exception: If the NTP server IP address is invalid or
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

    Raises:
        Exception: If the NTP server IP is invalid or if the probes_requested is negative.
    """
    if probes_requested < 0:
        raise Exception("Probe requested cannot be negative")
    ip_type = "ipv" + str(ip_family)
    # the best distribution of probes that we desire:
    probes_wanted_percentages = [0.33, 0.3, 0.27, 0.10, 0.0]
    max_pbs = 100
    # type 0 is ASN, type 1 is prefix, type 2 is country code, type 3 is area and type 4 is random
    mapping_indexes_to_type = {
        0: "asn",
        1: "prefix",
        2: "country",
        3: "area",
        4: "random",
    }
    # it contains the number of probes for each type (as a float because we would add float numbers to these fields,
    # and we want for example 0.5+0.5 to be 1, not 0)
    probes_wanted: list[float] = [0.0 for i in range(5)]
    probes_wanted[0] = probes_requested * probes_wanted_percentages[0]
    probes_wanted[1] = probes_requested * probes_wanted_percentages[1]
    probes_wanted[2] = probes_requested * probes_wanted_percentages[2]
    probes_wanted[3] = probes_requested * probes_wanted_percentages[3]
    # probes_wanted[4] = 0.0  #this is just a reminder that we do not want random probes

    # "ans" means how many probes of each type we will ask for, see "mapping_indexes_to_type" for details
    ans: list[float] = [0, 0, 0, 0, 0] # how many probes

    probes_available: list[float] = [0, 0, 0, 0, max_pbs] # random type always has enough probes
    # see what is available on RIPE Atlas
    if ip_asn is not None:
        probes_available[0] = get_available_probes_asn(ip_asn, ip_type)
    if ip_prefix is not None:
        probes_available[1] = get_available_probes_prefix(ip_prefix, ip_type)
    if ip_country is not None:
        probes_available[2] = get_available_probes_country(ip_country, ip_type)
    if ip_area is not None:
        probes_available[3] = max_pbs # there are enough probes in an area for sure.

    # let's see if we have enough probes of each type
    for i in range(0, len(probes_wanted)):
        # print("step: ",i)
        # print(probes_wanted)
        # print(probes_available)
        # print(ans)
        # print("===========")
        if probes_wanted[i] > probes_available[i]: # we want more than we have
            # we need probes from other types, but first take what we found in the desired type
            ans[i] += probes_available[i]
            needed: float = probes_wanted[i] - probes_available[i]
            probes_wanted[i] -= probes_available[i]
            probes_available[i] = 0
            # take from other types and update the available probes and the "ans"
            probes_available, ans = take_from_available_probes(needed, probes_available, ans)
            # we took what we needed
            probes_wanted[i] = 0
        else:
            # take the desired number of probes as we have enough
            probes_available[i] -= probes_wanted[i]
            ans[i] += probes_wanted[i]
            probes_wanted[i] = 0

        # print(probes_wanted)
        # print(probes_available)
        # print(ans)
    # print("/////////////////////")
    # we have only one step left. To convert from float to int and to add extra probes if we lost precision from floating points
    probes_to_add: int = probes_requested
    ans_integers: list[int] = [int(i) for i in ans]
    probes_available_integers: list[int] = [int(i) for i in probes_available]
    for x in ans_integers:
        probes_to_add -= x
    # print("probes_to_add: ", probes_to_add)
    probes_available_integers, ans_integers = take_from_available_probes(probes_to_add, probes_available_integers,
                                                                         ans_integers)
    print("the answer is:",ans)
    print("the answer is:",ans_integers)
    # convert the array into a dictionary
    best_probe_types: dict[str, int] = {}
    for i in range(0, len(ans_integers)):
        best_probe_types[mapping_indexes_to_type[i]] = ans_integers[i]
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

    Raises:
        Exception: If the input is invalid
    """
    # in wsl, this command would be for example:
    # ripe-atlas probe-search --prefix NL --status 1 --tag system-ipv4-works
    ip_asn_number = int(ip_asn[2:])
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

    Raises:
        Exception: If the input is invalid
    """
    # in wsl, this command would be for example:
    # ripe-atlas probe-search --prefix NL --status 1 --tag system-ipv4-works
    prefix_type: str = "prefix_v4" if ip_type == "ipv4" else "prefix_v6"
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

    Raises:
        Exception: If the input is invalid
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

def take_from_available_probes(needed: T, probes_available: list[T],
                               ans: list[T]) -> tuple[list[T], list[T]]:
    """
    This method tries to find "needed" number of probes in the available probes, in the order of their importance.
    For example, ASN probes are better than Country probes. (ASN > prefix > country > area > random)
    It will return the updated available probes and the updated list of the probes that we will request in the end.

    Args:
        needed (T): the needed number of probes to find
        probes_available (list[T]): an array which contains the available probes of each type
        ans (list[T]): an array which tells us how many probes of each type we should request after
                      finding the "needed" number of probes

    Returns:
        tuple[list[T], list[T]]: the updated "probes_available" and updated "ans"

    Raises:
        Exception: If we cannot find the needed number of probes from the available probes.
    """
    if needed <= 0:
        return probes_available, ans

    for i in range(0, len(probes_available)):
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
                needed = 0
                # stop as we finished our job there
                break
    if needed > 0:
        raise Exception("Not enough probes available")
    # ans_for_index would always be the initial value of needed
    return probes_available, ans

# import time
#
# start = time.time()
# # print(get_available_probes_asn("AS9009","ipv4"))
# # print(get_available_probes_prefix("80.211.224.0/16","ipv4"))
# # print(get_available_probes_country("NL","ipv4"))
# print(get_best_probe_types("AS9009", "80.211.224.0/20", "NL", "da", 4, 40))
# end = time.time()
# print(end - start)

#use cases:
# import pprint
# pprint.pprint(get_probes("AS15169","192.2.3.0/8","IT", "West",20))
#ex of output:
# [{'requested': 2, 'type': 'area', 'value': 'WW'},
#  {'requested': 10, 'type': 'asn', 'value': 'AS15169'},
#  {'requested': 10, 'type': 'country', 'value': 'IT'}]