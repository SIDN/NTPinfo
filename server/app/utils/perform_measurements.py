import socket, ntplib
from ipaddress import ip_address, IPv4Address, IPv6Address
from datetime import datetime, timezone
import json

import requests

from app.utils.ip_utils import get_country_asn_from_ip, get_ip_family
from app.utils.load_env_vals import get_ripe_account_email, get_ripe_api_token
from app.utils.ripe_probes import get_probes
from server.app.services.NtpCalculator import NtpCalculator
from server.app.utils.domain_name_to_ip import domain_name_to_ip_default, domain_name_to_ip_close_to_client
from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime
from server.app.utils.validate import is_ip_address


def calculate_jitter_from_measurements(initial_measurement: NtpMeasurement, times: int = 0) -> float:
    """
    For a single measurement, calculates a burst of measurements to calculate the jitter.
    Args:
        initial_measurement (NtpMeasurement): measurement that is actually saved in the DB, serving as the "mean" for the standard deviation.
        times (int): number of measurements performed to calculate jitter.

    Returns:
        float: jitter in seconds.
    """
    offsets = [NtpCalculator.calculate_offset(initial_measurement.timestamps)]
    measurements_done = 0
    for _ in range(times):
        measurement = perform_ntp_measurement_ip(
            str(initial_measurement.server_info.ntp_server_ip),
            initial_measurement.server_info.ntp_version
        )
        if measurement is None:
            break
        offsets.append(NtpCalculator.calculate_offset(measurement.timestamps))
        measurements_done += 1

    return float(NtpCalculator.calculate_jitter(offsets))


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
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:
        return None
    finally:
        s.close()
    try:
        return ip_address(ip)
    except ValueError:
        return None


def perform_ntp_measurement_domain_name(server_name: str = "pool.ntp.org", client_ip: str | None = None,
                                        ntp_version: int = 4) -> NtpMeasurement | None:
    """
    This method performs a NTP measurement on a NTP server from its domain name. The "other IPs list" of the
    measurement will be an empty list, or it will contain some elements. It would not be None.

    Args:
        server_name (str): the name of the ntp server
        client_ip (str|None): the ip address of the client (if given)
        ntp_version (int): the version of the ntp that you want to use

    Returns:
        NtpMeasurement | None: it returns the NTP measurement object or None if something wrong happened (usually timeouts).
    """
    domain_ips: list[str] | None

    if client_ip is None:  # if we do not have the client_ip available, use this server as a "client ip"
        domain_ips = domain_name_to_ip_default(server_name)
    else:
        domain_ips = domain_name_to_ip_close_to_client(server_name, client_ip)

    # if the domain name is invalid
    if domain_ips is None:
        return None
    # in case it is [] (it could not get the IPs for that domain name
    if not domain_ips:
        return None
    # domain_ips contains a list of ips that are good to use. We can simply use the first one
    ip_str = domain_ips[0]
    try:
        client = ntplib.NTPClient()
        response_from_ntplib = client.request(server_name, ntp_version, timeout=6)
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


def perform_ntp_measurement_ip(server_ip_str: str, ntp_version: int = 4) -> NtpMeasurement | None:
    """
    This method performs a NTP measurement on a NTP server from its IP address. The "other IPs list" of the
    measurement will be None.
    empty list of other IPs of the domain name.

    Args:
        server_ip_str (str): the ip address of the ntp server in string format
        ntp_version (int): the version of the ntp that you want to use

    Returns:
        NtpMeasurement | None: it returns the NTP measurement object or None if something wrong happened (usually timeouts).
    """
    if is_ip_address(server_ip_str) is None:
        return None
    # server_name is not available here. We can only use the ip which is initially a string
    try:
        client = ntplib.NTPClient()
        response = client.request(server_ip_str, ntp_version, timeout=6)
        return convert_ntp_response_to_measurement(response=response,
                                                   server_ip_str=server_ip_str,
                                                   server_name=None,
                                                   other_server_ips=None,
                                                   ntp_version=ntp_version)
    except Exception as e:
        print("Error in measure from ip:", e)
        return None


# def convert_timestamp_to_precise_time(t: float) -> PreciseTime:
#     """
#     This method converts a timestamp to precise time.
#
#     Args:
#         t (float): the timestamp
#
#     Returns:
#         PreciseTime: the precise time
#     """
#     return PreciseTime(ntplib._to_int(t), ntplib._to_frac(t))


def convert_ntp_response_to_measurement(response: ntplib.NTPStats, server_ip_str: str, server_name: str | None,
                                        other_server_ips: list[str] | None,
                                        ntp_version: int = 4, ) -> NtpMeasurement | None:
    """
    This method converts a NTP response to a NTP measurement object.

    Args:
        response (ntplib.NTPStats): the NTP response to convert
        server_ip_str (str): the ip address of the ntp server in string format
        server_name (str|None): the name of the ntp server
        ntp_version (int): the version of the ntp that you want to use
        other_server_ips (list[str] | None): an optional list of IP addresses if the measurement is performed on a domain name.

    Returns:
        NtpMeasurement | None: it returns a NTP measurement object if converting was successful.
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
    print(ref_id)
    if 0 <= stratum <= 1:  # we can get the name
        return None, ntplib.ref_id_to_text(ref_id, stratum)
    else:
        if stratum < 256:  # we can get an IP address
            return ip_address(socket.inet_ntoa(ref_id.to_bytes(4, 'big'))), None  # 'big' is from big endian
        else:
            return None, None  # invalid stratum!!


def ntp_precise_time_to_human_date(t: PreciseTime) -> str:
    """
    Converts a PreciseTime object to a human-readable time string in UTC. (ex:'2025-05-05 14:30:15.123456 UTC')
    We need to shift from ntp time to unix time so we need to subtract all the seconds from 1900 to 1970

    Args:
        t (PreciseTime): The PreciseTime object.

    Returns:
        str: the date in UTC format or empty, depending on whether the PreciseTime object could be converted to UTC.
    """
    try:
        timestamp = ntplib._to_time(t.seconds - ntplib.NTP.NTP_DELTA, t.fraction)
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f UTC")
    except Exception as e:
        print(e)
        return ""


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


def perform_ripe_measurement_ip(ntp_server_ip: str) -> int:
    """
    This method performs a RIPE measurement and returns the code of the measurement.

    Args:
        ntp_server_ip (str): The NTP server IP.

    Returns:
        int: The code of the measurement.
    """

    ip_family = get_ip_family(ntp_server_ip)

    api_key = get_ripe_api_token()
    packets_count = 2
    ripe_account_email = get_ripe_account_email()

    try:
        ip_country, ip_asn = get_country_asn_from_ip(ntp_server_ip)
    except Exception as e:
        # fall back to other probe options
        ip_country, ip_asn = None, None
        print("error")
        #return

    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    content = {"definitions": [
        {
            "type": "ntp",
            "af": ip_family,
            "resolve_on_probe": True,
            "description": f"NTP measurement to {ntp_server_ip}",
            "packets": packets_count,
            "timeout": 4000,
            "skip_dns_check": False,
            "target": ntp_server_ip
        }
    ],
        "is_oneoff": True,
        "bill_to": ripe_account_email,
        "probes": get_probes(ip_asn, ip_country)
    }
    response = requests.post(
        "https://atlas.ripe.net/api/v2/measurements/",
        headers=headers,
        data=json.dumps(content)
    )
    print("Status Code:", response.status_code)
    print("Response:", response.json())

    data = response.json()
    return data["measurements"][0]

#m=perform_ntp_measurement_domain_name("time.google.com")
# m=perform_ntp_measurement_domain_name("ro.pool.ntp.org","83.25.24.10")
# print_ntp_measurement(m)
# import time
#
# start = time.time()
# print(perform_ripe_measurement_ip("89.46.74.148"))
# end = time.time()
#
# print(end - start)