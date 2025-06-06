import pprint
import ntplib
from ipaddress import ip_address
import json
from typing import Optional
import requests

from server.app.models.CustomError import InputError, RipeMeasurementError
from server.app.utils.calculations import ntp_precise_time_to_human_date, convert_float_to_precise_time
from server.app.utils.ip_utils import get_ip_family, ref_id_to_ip_or_name, get_server_ip
from server.app.utils.load_config_data import get_ripe_account_email, get_ripe_api_token, get_ntp_version, \
    get_timeout_measurement_s, get_ripe_number_of_probes_per_measurement, \
    get_ripe_timeout_per_probe_ms, get_ripe_packets_per_probe
from server.app.utils.ripe_probes import get_probes
from server.app.utils.domain_name_to_ip import domain_name_to_ip_list
from server.app.dtos.NtpExtraDetails import NtpExtraDetails
from server.app.dtos.NtpMainDetails import NtpMainDetails
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.dtos.NtpServerInfo import NtpServerInfo
from server.app.dtos.NtpTimestamps import NtpTimestamps
from server.app.dtos.PreciseTime import PreciseTime
from server.app.utils.validate import is_ip_address


def perform_ntp_measurement_domain_name(server_name: str = "pool.ntp.org", client_ip: Optional[str] = None,
                                        ntp_version: int = get_ntp_version()) -> Optional[NtpMeasurement]:
    """
    This method performs a NTP measurement on a NTP server from its domain name. The "other IPs list" of the
    measurement will be an empty list, or it will contain some elements. It would not be None.

    Args:
        server_name (str): the name of the ntp server
        client_ip (str|None): the ip address of the client (if given)
        ntp_version (int): the version of the ntp that you want to use

    Returns:
        Optional[NtpMeasurement]: it returns the NTP measurement object or None if there is a timeout

    Raises:
        Exception: If the domain name is invalid or cannot be converted to an IP list
    """
    domain_ips: list[str] = domain_name_to_ip_list(server_name, client_ip)
    # domain_ips contains a list of ips that are good to use. We can simply use the first one
    ip_str = domain_ips[0]
    try:
        client = ntplib.NTPClient()
        response_from_ntplib = client.request(ip_str, ntp_version, timeout=get_timeout_measurement_s())
        r = convert_ntp_response_to_measurement(response=response_from_ntplib,
                                                server_ip_str=ip_str,
                                                server_name=server_name,
                                                ntp_version=ntp_version)
        if r is None:
            return None
        else:
            return r
    except Exception as e:
        print("Error in measure from name:", e)
        return None


def perform_ntp_measurement_domain_name_list(server_name: str = "pool.ntp.org", client_ip: Optional[str] = None,
                                             ntp_version: int = get_ntp_version()) -> Optional[list[NtpMeasurement]]:
    """
    This method performs a NTP measurement on a NTP server from all the ips got back from its domain name.

    Args:
        server_name (str): the name of the ntp server
        client_ip (str|None): the ip address of the client (if given)
        ntp_version (int): the version of the ntp that you want to use

    Returns:
        Optional[list[NtpMeasurement]]: it returns a list of NTP measurement objects or None if there is a timeout

    Raises:
        Exception: If the domain name is invalid or cannot be converted to an IP list
    """
    domain_ips: list[str] = domain_name_to_ip_list(server_name, client_ip)
    # domain_ips contains a list of ips that are good to use.
    resulted_measurements = []
    for ip_str in domain_ips:
        try:
            client = ntplib.NTPClient()
            response_from_ntplib = client.request(ip_str, ntp_version, timeout=get_timeout_measurement_s())
            r = convert_ntp_response_to_measurement(response=response_from_ntplib,
                                                    server_ip_str=ip_str,
                                                    server_name=server_name,
                                                    ntp_version=ntp_version)

            if r is not None:
                resulted_measurements.append(r)
        except Exception as e:
            print("Error in measure from name:", e)
            continue

    return resulted_measurements if resulted_measurements else None


def perform_ntp_measurement_ip(server_ip_str: str, ntp_version: int = get_ntp_version()) -> Optional[NtpMeasurement]:
    """
    This method performs a NTP measurement on a NTP server from its IP address. The "other IPs list" of the
    measurement will be None.
    empty list of other IPs of the domain name.

    Args:
        server_ip_str (str): the ip address of the ntp server in string format
        ntp_version (int): the version of the ntp that you want to use

    Returns:
        Optional[NtpMeasurement]: it returns the NTP measurement object or None if something wrong happened (usually timeouts).
    """
    if is_ip_address(server_ip_str) is None:
        return None
    # server_name is not available here. We can only use the ip which is initially a string
    try:
        client = ntplib.NTPClient()
        response = client.request(server_ip_str, ntp_version, timeout=get_timeout_measurement_s())
        return convert_ntp_response_to_measurement(response=response,
                                                   server_ip_str=server_ip_str,
                                                   server_name=None,
                                                   ntp_version=ntp_version)
    except Exception as e:
        print("Error in measure from ip:", e)
        return None


def convert_ntp_response_to_measurement(response: ntplib.NTPStats, server_ip_str: str, server_name: Optional[str],
                                        ntp_version: int = get_ntp_version()) -> Optional[NtpMeasurement]:
    """
    This method converts a NTP response to a NTP measurement object.

    Args:
        response (ntplib.NTPStats): the NTP response to convert
        server_ip_str (str): the ip address of the ntp server in string format
        server_name (Optional[str]): the name of the ntp server
        other_server_ips (Optional[list[str]]): an optional list of IP addresses if the measurement is performed on a domain name
        ntp_version (int): the version of the ntp that you want to use.

    Returns:
        Optional[NtpMeasurement]: it returns a NTP measurement object if converting was successful.
    """
    try:
        vantage_point_ip_temp = get_server_ip()
        if vantage_point_ip_temp is not None:
            vantage_point_ip = vantage_point_ip_temp
        ref_ip, ref_name = ref_id_to_ip_or_name(response.ref_id,
                                                response.stratum)
        server_ip = ip_address(server_ip_str)
        server_info: NtpServerInfo = NtpServerInfo(
            ntp_version=ntp_version,
            ntp_server_ip=server_ip,
            ntp_server_name=server_name,
            ntp_server_ref_parent_ip=ref_ip,
            ref_name=ref_name,
        )

        timestamps: NtpTimestamps = NtpTimestamps(
            client_sent_time=PreciseTime(ntplib._to_int(response.dest_timestamp),
                                         ntplib._to_frac(response.dest_timestamp)),
            server_recv_time=PreciseTime(ntplib._to_int(response.orig_timestamp),
                                         ntplib._to_frac(response.orig_timestamp)),
            server_sent_time=PreciseTime(ntplib._to_int(response.recv_timestamp),
                                         ntplib._to_frac(response.recv_timestamp)),
            client_recv_time=PreciseTime(ntplib._to_int(response.tx_timestamp), ntplib._to_frac(response.tx_timestamp))
        )

        main_details: NtpMainDetails = NtpMainDetails(
            offset=response.offset,
            rtt=response.delay,
            stratum=response.stratum,
            precision=response.precision,
            reachability=""
        )

        extra_details: NtpExtraDetails = NtpExtraDetails(
            root_delay=convert_float_to_precise_time(response.root_delay),
            ntp_last_sync_time=convert_float_to_precise_time(response.ref_timestamp),
            leap=response.leap
        )

        return NtpMeasurement(vantage_point_ip, server_info, timestamps, main_details, extra_details)
    except Exception as e:
        print("Error in convert response to measurement:", e)
        return None


def print_ntp_measurement(measurement: NtpMeasurement) -> bool:
    """
        It prints the ntp measurement in a human-readable format and returns True if the printing was successful.

        Args:
            measurement (NtpMeasurement): the NtpMeasurement object.
    """
    try:
        print("=== NTP Measurement ===")
        print(f"Vantage Point IP:      {measurement.vantage_point_ip}")
        # Server Info
        server = measurement.server_info
        print(f"Server Name:           {server.ntp_server_name}")
        print(f"Server IP:             {server.ntp_server_ip}")
        print(f"NTP Version:           {server.ntp_version}")
        print(f"Reference Parent IP:   {server.ntp_server_ref_parent_ip}")
        print(f"Reference Name (Raw):  {server.ref_name}")

        # Timestamps
        timestamps = measurement.timestamps
        print(
            f"Client sent time:      {ntp_precise_time_to_human_date(timestamps.client_sent_time)} : s: {timestamps.client_sent_time.seconds} f: {timestamps.client_sent_time.fraction}")
        print(
            f"Server recv time:      {ntp_precise_time_to_human_date(timestamps.server_recv_time)} : s: {timestamps.server_recv_time.seconds} f: {timestamps.server_recv_time.fraction}")
        print(
            f"Server sent time:      {ntp_precise_time_to_human_date(timestamps.server_sent_time)} : s: {timestamps.server_sent_time.seconds} f: {timestamps.server_sent_time.fraction}")
        print(
            f"Client recv time:      {ntp_precise_time_to_human_date(timestamps.client_recv_time)} : s: {timestamps.client_recv_time.seconds} f: {timestamps.client_recv_time.fraction}")

        # Main Details
        main = measurement.main_details
        print(f"Offset (s):            {main.offset}")
        print(f"Delay (s):             {main.rtt}")
        print(f"Stratum:               {main.stratum}")
        print(f"Precision:             {main.precision}")
        print(f"Reachability:          {main.reachability}")

        # Extra Details
        extra = measurement.extra_details
        print(f"Root Delay:            {ntplib._to_time(extra.root_delay.seconds, extra.root_delay.fraction)}")
        print(f"Last Sync Time:        {ntp_precise_time_to_human_date(extra.ntp_last_sync_time)}")
        print(f"Leap:                  {extra.leap}")

        print("=========================")
        return True
    except Exception as e:
        print("Error:", e)
        return False


def perform_ripe_measurement_domain_name(server_name: str, client_ip: str,
                                         probes_requested: int =
                                         get_ripe_number_of_probes_per_measurement()) -> int:
    """
    This method performs a RIPE measurement on a domain name. It lets the RIPE atlas probe to

    Args:
        server_name (str): The domain name of the NTP server.
        client_ip (str): The IP address of the NTP server.
        probes_requested (int): The number of probes requested.

    Returns:
        int: It returns the ID of the measurement and the list of IPs of the domain name.
                               You can find in the measurement what IP it used.

    Raises:
        InputError: If the conversion could not be performed.
        RipeMeasurementError: If the ripe measurement could not be performed.
    """

    if probes_requested <= 0:
        raise InputError("Probes requested must be greater than 0.")
    # domain_ips: list[str] = domain_name_to_ip_list(server_name, client_ip)
    # same IP family as the client
    ip_family: int = get_ip_family(client_ip)
    # we will make an NTP measurement from probes to the domain name.

    # measurement settings
    headers, request_content = get_request_settings(ip_family_of_ntp_server=ip_family, ntp_server=server_name,
                                                    client_ip=client_ip, probes_requested=probes_requested)
    # perform the measurement
    response = requests.post(
        "https://atlas.ripe.net/api/v2/measurements/",
        headers=headers,
        data=json.dumps(request_content)
    )

    data = response.json()
    # the answer has a list of measurements, but we only did one measurement so we send one.
    pprint.pprint(data)
    try:
        ans: int = data["measurements"][0]
    except Exception as e:
        if "error" in data:
            raise RipeMeasurementError(data["error"])
        else:
            raise RipeMeasurementError(f"Ripe measurement failed:{e}")
    return ans


def perform_ripe_measurement_ip(ntp_server_ip: str, client_ip: str,
                                probes_requested: int = get_ripe_number_of_probes_per_measurement()) -> int:
    """
    This method performs a RIPE measurement and returns the code of the measurement.

    Args:
        ntp_server_ip (str): The NTP server IP.
        client_ip (str): The IP of the client.
        probes_requested (int): The number of probes requested.

    Returns:
        int: The ID of the measurement.

    Raises:
        InputError: If the NTP server IP is not valid, probe requested is negative
        RipeMeasurementError: If the ripe measurement could not be performed.
    """

    if probes_requested <= 0:
        raise InputError("Probes requested must be greater than 0.")
    get_ip_family(client_ip)  # this will throw an exception if the client_ip is not an IP address

    ip_family = get_ip_family(ntp_server_ip)  # this will throw an exception if the ntp_server_ip is not an IP address

    # measurement settings
    headers, request_content = get_request_settings(ip_family_of_ntp_server=ip_family, ntp_server=ntp_server_ip,
                                                    client_ip=client_ip, probes_requested=probes_requested)
    # perform the measurement
    response = requests.post(
        "https://atlas.ripe.net/api/v2/measurements/",
        headers=headers,
        data=json.dumps(request_content)
    )

    data = response.json()
    # the answer has a list of measurements, but we only did one measurement so we send one.
    try:
        ans: int = data["measurements"][0]
    except Exception as e:
        if "error" in data:
            raise RipeMeasurementError(data["error"])
        else:
            raise RipeMeasurementError(f"Ripe measurement failed:{e}")
    return ans


def get_request_settings(ip_family_of_ntp_server: int, ntp_server: str, client_ip: str,
                         probes_requested: int = get_ripe_number_of_probes_per_measurement()) -> tuple[dict, dict]:
    """
    This method gets the RIPE measurement settings for the performing a RIPE measurement.
    Args:
        ip_family_of_ntp_server (int): The IP family of the NTP server. (4 or 6)
        ntp_server (str): The NTP server IP address or domain name
        client_ip (str): The IP address of the client
        probes_requested (int): The number of probes requested.

    Returns:
        tuple[dict,dict]: Returns the RIPE measurement settings for the performing a RIPE measurement.

    Raises:
        InputError: If the input is invalid.
        RipeMeasurementError: If the ripe measurement could not be performed.
        Exception: If something else failed. TODO
    """
    headers = {
        "Authorization": f"Key {get_ripe_api_token()}",
        "Content-Type": "application/json"
    }
    request_content = {"definitions": [
        {
            "type": "ntp",
            "af": ip_family_of_ntp_server,
            "resolve_on_probe": True,
            "description": f"NTP measurement to {ntp_server}",
            "packets": get_ripe_packets_per_probe(),
            "timeout": get_ripe_timeout_per_probe_ms(),
            "skip_dns_check": False,
            "target": ntp_server
        }
    ],
        "is_oneoff": True,
        "bill_to": get_ripe_account_email(),
        "probes": get_probes(client_ip, probes_requested)  # we want probes close to the client
    }
    return headers, request_content
# m=perform_ntp_measurement_domain_name("time.google.com")
# m=perform_ntp_measurement_domain_name("ro.pool.ntp.org","83.25.24.10")
# print_ntp_measurement(m)
import time

start = time.time()
print(perform_ripe_measurement_domain_name("time.apple.com","145.94.210.165")) #("89.46.74.148"))
end = time.time()

print(end - start)
