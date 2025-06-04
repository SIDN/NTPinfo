import socket, ntplib
from ipaddress import ip_address, IPv4Address, IPv6Address
from datetime import datetime, timezone
import json
from typing import Optional

import requests

from server.app.utils.calculations import ntp_precise_time_to_human_date
from server.app.utils.ip_utils import get_ip_family, ref_id_to_ip_or_name
from server.app.utils.load_config_data import get_ripe_account_email, get_ripe_api_token, get_ntp_version, \
    get_edns_default_servers, get_timeout_measurement_s, get_ripe_number_of_probes_per_measurement, \
    get_ripe_timeout_per_probe_ms, get_ripe_packets_per_probe
from server.app.utils.ripe_probes import get_probes
from server.app.services.NtpCalculator import NtpCalculator
from server.app.utils.domain_name_to_ip import domain_name_to_ip_list
from server.app.dtos.NtpExtraDetails import NtpExtraDetails
from server.app.dtos.NtpMainDetails import NtpMainDetails
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.dtos.NtpServerInfo import NtpServerInfo
from server.app.dtos.NtpTimestamps import NtpTimestamps
from server.app.dtos.PreciseTime import PreciseTime
from server.app.utils.validate import is_ip_address


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
        return ip_address(ip)
    except ValueError:
        return None


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
        response_from_ntplib = client.request(server_name, ntp_version, timeout=get_timeout_measurement_s())
        r = convert_ntp_response_to_measurement(response=response_from_ntplib,
                                                server_ip_str=ip_str,
                                                server_name=server_name,
                                                other_server_ips=domain_ips,
                                                ntp_version=ntp_version)
        if r is None:
            return None
        else:
            return r
    except Exception as e:
        print("Error in measure from name:", e)
        return None


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
                                                   other_server_ips=None,
                                                   ntp_version=ntp_version)
    except Exception as e:
        print("Error in measure from ip:", e)
        return None


def convert_ntp_response_to_measurement(response: ntplib.NTPStats, server_ip_str: str, server_name: Optional[str],
                                        other_server_ips: Optional[list[str]],
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
            other_server_ips=other_server_ips
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
            delay=response.delay,
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


def convert_float_to_precise_time(value: float) -> PreciseTime:
    """
    Converts a float value to a PreciseTime object.

    Args:
        value (float): the float value to convert

    Returns:
        a PreciseTime object
    """
    seconds = int(value)
    fraction = ntplib._to_frac(value)  # by default, a second is split into 2^32 parts
    return PreciseTime(seconds, fraction)


def human_date_to_ntp_precise_time(dt: datetime) -> PreciseTime:
    """
    Converts a UTC datetime object to a PreciseTime object in NTP time.

    Args:
        dt (datetime): A timezone-aware datetime object in UTC.

    Returns:
        PreciseTime: The corresponding NTP time.
    """
    if dt.tzinfo is None:
        raise ValueError("Input datetime must be timezone-aware (UTC)")

    unix_timestamp = dt.timestamp()
    ntp_timestamp = unix_timestamp + ntplib.NTP.NTP_DELTA

    ntp_seconds = int(ntp_timestamp)
    ntp_fraction = int((ntp_timestamp - ntp_seconds) * (2 ** 32))

    return PreciseTime(ntp_seconds, ntp_fraction)


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
        print(f"Delay (s):             {main.delay}")
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

def perform_ripe_measurement_domain_name(server_name: str, client_ip: Optional[str] = None,
                                         probes_requested: int =
                                         get_ripe_number_of_probes_per_measurement()) -> tuple[int, list[str]]:
    """
    This method performs a RIPE measurement on a domain name. It transforms the domain name of the NTP server into
    an IP address, and then it uses perform_ripe_measurement_ip method.

    Args:
        server_name (str): The domain name of the NTP server.
        client_ip (Optional[str]): The IP address of the NTP server.
        probes_requested (int): The number of probes requested.

    Returns:
        tuple[int, list[str]]: It returns the ID of the measurement and the list of IPs of the domain name.
                               You can find in the measurement what IP it used.

    Raises:
        Exception: If the conversion could not be performed or if the measurement failed.
    """
    domain_ips: list[str] = domain_name_to_ip_list(server_name, client_ip)
    # take one IP address from the list
    ip_str = domain_ips[0]
    return perform_ripe_measurement_ip(ip_str, probes_requested), domain_ips


def perform_ripe_measurement_ip(ntp_server_ip: str,
                                probes_requested: int=get_ripe_number_of_probes_per_measurement()) -> int:
    """
    This method performs a RIPE measurement and returns the code of the measurement.

    Args:
        ntp_server_ip (str): The NTP server IP.
        probes_requested (int): The number of probes requested.

    Returns:
        int: The ID of the measurement.

    Raises:
        Exception: If the NTP server IP is not valid, probe requested is negative or if the measurement could not be performed.
    """

    if probes_requested <= 0:
        raise Exception("Probe requested must be greater than 0.")

    # measurement settings
    ip_family = get_ip_family(ntp_server_ip) # this will throw an exception if the ntp_server_ip is not an IP address
    api_key = get_ripe_api_token()
    packets_count = get_ripe_packets_per_probe()
    ripe_account_email = get_ripe_account_email()

    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    request_content = {"definitions": [
        {
            "type": "ntp",
            "af": ip_family,
            "resolve_on_probe": True,
            "description": f"NTP measurement to {ntp_server_ip}",
            "packets": packets_count,
            "timeout": get_ripe_timeout_per_probe_ms(),
            "skip_dns_check": False,
            "target": ntp_server_ip
        }
    ],
        "is_oneoff": True,
        "bill_to": ripe_account_email,
        "probes": get_probes(ntp_server_ip, probes_requested)
    }

    # perform the measurement
    response = requests.post(
        "https://atlas.ripe.net/api/v2/measurements/",
        headers=headers,
        data=json.dumps(request_content)
    )

    # print("Status Code:", response.status_code)
    # print("Response:", response.json())

    data = response.json()
    # the answer has a list of measurements, but we only did one measurement so we send one.
    ans: int = data["measurements"][0]
    return ans

# m=perform_ntp_measurement_domain_name("time.google.com")
# m=perform_ntp_measurement_domain_name("ro.pool.ntp.org","83.25.24.10")
# print_ntp_measurement(m)
# import time
#
# start = time.time()
# print(perform_ripe_measurement_ip("31.25.10.207")) #("89.46.74.148"))
# end = time.time()
#
# print(end - start)