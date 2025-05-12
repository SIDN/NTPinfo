import socket, ntplib
from ipaddress import ip_address, IPv4Address, IPv6Address
from datetime import datetime, timezone

from server.app.utils.domain_name_to_ip import domain_name_to_ip_default, domain_name_to_ip_close_to_client
from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime
from server.app.utils.validate import is_ip_address


def perform_ntp_measurement_domain_name(server_name: str = "pool.ntp.org", client_ip: str|None=None,
                                        ntp_version: int = 3) -> NtpMeasurement | None:
    """
    This method performs a NTP measurement on a NTP server from its domain name.

    Args:
        server_name (str): the name of the ntp server
        client_ip (str|None): the ip address of the client (if given)
        ntp_version (int): the version of the ntp that you want to use

    Returns:
        NtpMeasurement | None: it returns the NTP measurement object or None if something wrong happened (usually timeouts).
    """
    domain_ips: list[str] | None

    if client_ip is None:  #if we do not have the client_ip available, use this server as a "client ip"
        domain_ips = domain_name_to_ip_default(server_name)
    else:
        domain_ips = domain_name_to_ip_close_to_client(server_name, client_ip)

    if domain_ips is None:
        return None
    #domain_ips contains a list of ips that are good to use. We can simply use the first one
    ip_str = domain_ips[0]
    try:
        client = ntplib.NTPClient()
        response = client.request(server_name, ntp_version, timeout=6)
        return convert_ntp_response_to_measurement(response=response,
                                                   server_ip_str=ip_str,
                                                   server_name=server_name,
                                                   ntp_version=ntp_version)
    except Exception as e:
        print("Error in measure from name:", e)
        return None


def perform_ntp_measurement_ip(server_ip_str: str, ntp_version: int = 3) -> NtpMeasurement | None:
    """
    This method performs a NTP measurement on a NTP server from its IP address.

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
                                                   ntp_version=ntp_version)
    except Exception as e:
        print("Error in measure from ip:", e)
        return None


def convert_timestamp_to_precise_time(t: float) -> PreciseTime:
    """
    This method converts a timestamp to precise time.

    Args:
        t (float): the timestamp

    Returns:
        PreciseTime: the precise time
    """
    return PreciseTime(ntplib._to_int(t), ntplib._to_frac(t))


def convert_ntp_response_to_measurement(response: ntplib.NTPStats, server_ip_str: str, server_name: str | None,
                                        ntp_version: int = 3) -> NtpMeasurement | None:
    """
    This method converts a NTP response to a NTP measurement object.

    Args:
        response (ntplib.NTPStats): the NTP response to convert
        server_ip_str (str): the ip address of the ntp server in string format
        server_name (str|None): the name of the ntp server
        ntp_version (int): the version of the ntp that you want to use

    Returns:
        NtpMeasurement | None: it returns a NTP measurement object if converting was successful.
    """
    try:
        ref_ip, ref_name = ref_id_to_ip_or_name(response.ref_id,
                                                response.stratum)
        server_ip = ip_address(server_ip_str)
        server_info: NtpServerInfo = NtpServerInfo(
            ntp_version=ntp_version,
            ntp_server_ip=server_ip,
            ntp_server_name=server_name,
            ntp_server_ref_parent_ip=ref_ip,
            ref_name=ref_name
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

        return NtpMeasurement(server_info, timestamps, main_details, extra_details)
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

# m=perform_ntp_measurement_domain_name("77.175.129.186",3)
# m=perform_ntp_measurement_domain_name("pool.ntp.org","83.25.24.10")
# print_ntp_measurement(m)
