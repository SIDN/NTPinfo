from typing import TypeVar
from typing import Optional

from server.app.models.CustomError import InputError
from server.app.utils.load_config_data import get_ripe_number_of_probes_per_measurement, get_ripe_max_probes_per_measurement, \
    get_ripe_probes_wanted_percentages
from server.app.utils.ip_utils import get_ip_network_details, get_prefix_from_ip, get_ip_family
from ripe.atlas.cousteau import ProbeRequest


T = TypeVar('T', int, float) # float or int


def get_probes(client_ip: str,
               probes_requested: int=get_ripe_number_of_probes_per_measurement()) -> list[dict]:
    """
    This method handles all cases regarding what probes we should send.
    This method assumes all inputs are either valid or None. (If there is a type in the input, the measurement
    may be affected)

    Args:
        client_ip (str): The IP address of the client.
        probes_requested (int): The total number of probes that we will request.

    Returns:
        list[dict]: The list of probes that we will use for the measurement.

    Raises:
        Exception: If the NTP server IP address is invalid or
    """
    # get the details. (this will take around 150-200ms)
    ip_family: int = get_ip_family(client_ip)
    ip_asn, ip_country, ip_area = get_ip_network_details(client_ip)
    ip_prefix = get_prefix_from_ip(client_ip)
    # settings:
    probes: list[dict] = []
    probe_functions = {
        "asn": lambda c: get_asn_probes(ip_asn, c),
        "prefix": lambda c: get_prefix_probes(ip_prefix, c),
        "country": lambda c: get_country_probes(ip_country, c),
        "area": lambda c: get_area_probes(ip_area, c),
        "random": lambda c: get_random_probes(c)
    }
    # Try to see if we have probes with the same ASN and prefix OR same ASN and same country. They have the highest priority.
    probes_requested, initial_probes_ids = getting_best_probes_with_multiple_attributes(ip_asn=ip_asn, ip_prefix=ip_prefix, ip_country=ip_country,
                                                 ip_family=ip_family, probes_requested=probes_requested)
    # add their IDs.
    if len(initial_probes_ids) > 0:
        probes.append(get_probes_by_ids(initial_probes_ids))
    # we have found our probes -> return
    if probes_requested <= 0:
        return probes

    # if we still need more probes or if the method above failed, continue trying with filters by a single attributes.
    best_probe_types: dict[str, int] = get_best_probe_types(ip_asn=ip_asn, ip_prefix=ip_prefix, ip_country=ip_country,
                                                ip_area=ip_area, ip_family=ip_family, probes_requested=probes_requested)

    for probe_type, n in best_probe_types.items():
        # instead of a switch, I used a map with lambda methods
        if n > 0:
            # fall back to random probes if the type is invalid
            probes.append(probe_functions.get(probe_type, lambda c: get_random_probes(c))(n))
    return probes


def get_best_probe_types(ip_asn: Optional[str], ip_prefix: Optional[str], ip_country: Optional[str],
                         ip_area: Optional[str], ip_family: int,
                         probes_requested: int=get_ripe_number_of_probes_per_measurement()) -> dict[str, int]:
    """
    This method is responsible for getting the best probes for the measurement. It should return probes that
    are near the NTP server.

    Args:
        ip_asn (int): The ASN of the NTP server IP address.
        ip_prefix (str): The prefix of the NTP server IP address.
        ip_country (str): The country of the NTP server IP address.
        ip_area (str): The area of the NTP server IP address.
        ip_family (int): The family of the NTP server IP address. (4 or 6)
        probes_requested (int): The number of probes that we will request.

    Returns:
        dict[str, int]: The set of probe types and the respective number of probes.

    Raises:
        InputError: If the NTP server IP is invalid or if the probes_requested is negative.
    """
    if probes_requested < 0:
        raise InputError("Probe requested cannot be negative")
    ip_type = "ipv" + str(ip_family)
    # the best distribution of probes that we desire at this point:
    probes_wanted_percentages = get_ripe_probes_wanted_percentages()
    max_pbs = get_ripe_max_probes_per_measurement()
    mapping_indexes_to_type = {
        0: "asn",
        1: "prefix",
        2: "country",
        3: "area",
        4: "random"
    }
    # it contains the number of probes for each type (as a float because we would add float numbers to these fields,
    # and we want for example 0.5+0.5 to be 1, not 0)
    probes_wanted: list[float] = [0.0 for _ in range(5)]
    probes_wanted[0] = probes_requested * probes_wanted_percentages[0]
    probes_wanted[1] = probes_requested * probes_wanted_percentages[1]
    probes_wanted[2] = probes_requested * probes_wanted_percentages[2]
    probes_wanted[3] = probes_requested * probes_wanted_percentages[3]
    probes_wanted[4] = probes_requested * probes_wanted_percentages[4]

    # "ans" means how many probes of each type we will ask for, see "mapping_indexes_to_type" for details
    ans: list[float] = [0.0 for _ in range(5)] # how many probes

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

    # we have only one step left. To convert from float to int and to add extra probes if we lost precision from floating points
    probes_to_add: int = probes_requested
    ans_integers: list[int] = [int(i) for i in ans]
    probes_available_integers: list[int] = [int(i) for i in probes_available]
    for x in ans_integers:
        probes_to_add -= x
    # print("probes_to_add: ", probes_to_add)
    probes_available_integers, ans_integers = take_from_available_probes(probes_to_add, probes_available_integers,
                                                                         ans_integers)
    # convert the array into a dictionary
    best_probe_types: dict[str, int] = {}
    for i in range(0, len(ans_integers)):
        best_probe_types[mapping_indexes_to_type[i]] = ans_integers[i]
    return best_probe_types

def getting_best_probes_with_multiple_attributes(ip_asn: Optional[str], ip_prefix: Optional[str], ip_country: Optional[str],
                          ip_family: int,
                         probes_requested: int=get_ripe_number_of_probes_per_measurement()) -> tuple[int, list[int]]:
    """
    This method tries to get probes that has the same ASN and prefix OR the same ASN and country and subtract them
    from the probes_requested. These probes have the highest priority as they have multiple attributes as the client IP
    (same ASN and same prefix OR same ASN or same country)

    Args:
        ip_asn (int): The ASN of the NTP server IP address.
        ip_prefix (str): The prefix of the NTP server IP address.
        ip_country (str): The country of the NTP server IP address.
        ip_family (int): The family of the NTP server IP address. (4 or 6)
        probes_requested (int): The total number of probes that we will request.

    Returns:
        tuple[int, list[int]]: The updated number of requested probes still needed and
                               a list of the IDs of the probes that we found until now.

    Raises:
        InputError: If the input is invalid or probes_requested is negative.
    """
    if probes_requested < 0:
        raise InputError("Probe requested cannot be negative")

    ip_type = "ipv" + str(ip_family)
    probes_ids_set: set[int] = set()
    # see if we can get enough probes from probes with the same ASN and same prefix:
    count, ids = get_available_probes_asn_and_prefix(ip_asn, ip_prefix, ip_type) if (
                ip_asn is not None and ip_prefix is not None) else (0, [])
    for pb in ids:
        if pb not in probes_ids_set:
            probes_ids_set.add(pb)
            probes_requested -= 1
            if probes_requested <= 0:
                return 0, list(probes_ids_set)
    # try with the probes from the same ASN and country
    count, ids = get_available_probes_asn_and_country(ip_asn, ip_country, ip_type) if (
                ip_asn is not None and ip_country is not None) else (0, [])
    for pb in ids:
        if pb not in probes_ids_set:
            probes_ids_set.add(pb)
            probes_requested -= 1
            if probes_requested <= 0:
                return 0, list(probes_ids_set)
    return probes_requested, list(probes_ids_set)

def get_probes_by_ids(probe_ids: list[int]) -> dict:
    """
        This method selects probes by their IDs.

        Args:
            probe_ids (list[int]): The IDs of the probes.

        Returns:
            dict: the selected probes

        Raises:
            InputError: If the input is invalid
        """
    if len(probe_ids) == 0:
        raise InputError("probe_ids cannot be empty")
    list_str = [str(p) for p in probe_ids]
    formatted_list = ','.join(list_str)
    #print(formatted_list)
    probes = {
        "type": "probes",
        "value": formatted_list,
        "requested": len(probe_ids)
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
        InputError: if the ASN network is None
    """
    if ip_asn is None:
        raise InputError("ip_asn cannot be None")
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
        InputError: if the IP prefix is None
    """
    if ip_prefix is None:
        raise InputError("ip_prefix cannot be None")
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
        InputError: if the country code is None
    """
    if ip_country_code is None:
        raise InputError("ip_country_code cannot be None")
    probes = {
            "type": "country",
            "value": ip_country_code,
            "requested": n
        }
    return probes
def get_area_probes(area: Optional[str], n: int) -> dict:
    """
    This method selects n random probes from all over the world.

    Args:
        area (str): The area of the probes
        n (int): number of probes to select

    Returns:
        dict: the selected probes

    Raises:
        InputError: If area is not valid
    """
    if area is None:
        raise InputError("area cannot be None")
    probes = {
        "type": "area",
        "value": area,
        "requested": n
    }
    return probes
def get_random_probes(n: int) -> dict:
    """
    This method selects n random probes from all over the world.

    Args:
        n (int): number of probes to select

    Returns:
        dict: the selected probes
    """
    return get_area_probes("WW", n)
def get_available_probes_asn_and_prefix_and_country(ip_asn: str, ip_prefix: str,
                                                    ip_country_code: str, ip_type: str) -> tuple[int, list[int]]:
    """
    This method gets how many probes that has the same ASN and same prefix as the IP are available.
    These probes should also support ipv4 or ipv6, it depends on the type.

    Args:
        ip_asn (str): the ASN of the searched network
        ip_prefix(str): the prefix of the respective IP
        ip_country_code(str): the country code of the respective IP
        ip_type (str): the IP type (ipv4 or ipv6). (not case-sensitive)

    Returns:
        tuple[int, list[str]]: the number of available probes and the list with the IPs of the probes

    Raises:
        Exception: If the input is invalid
    """
    ip_asn_number = int(ip_asn[2:])
    prefix_type: str = "prefix_v4" if ip_type == "ipv4" else "prefix_v6"
    filters = {
       "asn": ip_asn_number,
        prefix_type: ip_prefix,
        "country_code": ip_country_code,
        "status": 1,  # Connected probes
        "tags": f"system-{ip_type.lower()}-works",
    }
    probes = ProbeRequest(
        return_objects=True,
        fields="id",
        page_size=200,
        **filters,
    )
    probe_ids_list: list[int] = []
    for p in probes:
        probe_ids_list.append(p.id)

    #print(probe_ids_list)
    ans: int = len(probe_ids_list)
    return ans, probe_ids_list
def get_available_probes_asn_and_prefix(ip_asn: str, ip_prefix: str, ip_type: str) -> tuple[int, list[int]]:
    """
    This method gets how many probes that has the same ASN and same prefix as the IP are available.
    These probes should also support ipv4 or ipv6, it depends on the type.

    Args:
        ip_asn (str): the ASN of the searched network
        ip_prefix(str): the prefix of the respective IP
        ip_type (str): the IP type (ipv4 or ipv6). (not case-sensitive)

    Returns:
        tuple[int, list[str]]: the number of available probes and the list with the IPs of the probes

    Raises:
        Exception: If the input is invalid
    """
    ip_asn_number = int(ip_asn[2:])
    prefix_type: str = "prefix_v4" if ip_type == "ipv4" else "prefix_v6"
    filters = {
       "asn": ip_asn_number,
        prefix_type: ip_prefix,
        "status": 1,  # Connected probes
        "tags": f"system-{ip_type.lower()}-works",
    }
    probes = ProbeRequest(
        return_objects=True,
        fields="id",
        page_size=200,
        **filters,
    )
    probe_ids_list: list[int] = []
    for p in probes:
        probe_ids_list.append(p.id)

    #print(probe_ids_list)
    ans: int = len(probe_ids_list)
    return ans, probe_ids_list
def get_available_probes_asn_and_country(ip_asn: str, ip_country_code: str, ip_type: str) -> tuple[int, list[int]]:
    """
    This method gets how many probes that has the same ASN and same country code as the IP are available.
    These probes should also support ipv4 or ipv6, it depends on the type.

    Args:
        ip_asn (str): the ASN of the searched network
        ip_country_code(str): the country code of the respective IP
        ip_type (str): the IP type (ipv4 or ipv6). (not case-sensitive)

    Returns:
        tuple[int, list[str]]: the number of available probes and the list with the IPs of the probes

    Raises:
        Exception: If the input is invalid
    """
    ip_asn_number = int(ip_asn[2:])
    filters = {
       "asn": ip_asn_number,
        "country_code": ip_country_code,
        "status": 1,  # Connected probes
        "tags": f"system-{ip_type.lower()}-works",
    }
    probes = ProbeRequest(
        return_objects=True,
        fields="id",
        page_size=200,
        **filters,
    )
    probe_ids_list: list[int] = []
    for p in probes:
        probe_ids_list.append(p.id)

    #print(probe_ids_list)
    ans: int = len(probe_ids_list)
    return ans, probe_ids_list
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

# prefixx = get_prefix_from_ip("89.46.74.148")
# print(prefixx)
# import time
# start = time.time()
# print(get_probes("89.46.74.148", 20))
# a,b=get_available_probes_asn_and_prefix("AS15435","149.143.64.0/18","ipv4")
# print(a,b)
# c=get_probes_by_ids(b)
# print(c)
# print(get_available_probes_asn_and_country("AS15435","BL","ipv4"))
# print(get_available_probes_asn("AS9009","ipv4"))
# print(get_available_probes_prefix(prefixx,"ipv4"))
# print(get_available_probes_country("NL","ipv4"))
# print(get_best_probe_types("AS9009", "80.211.224.0/20", "NL", "da", 4, 40))
# end = time.time()
# print(end - start)