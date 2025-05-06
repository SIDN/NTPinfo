import socket
from ipaddress import ip_address, IPv4Address, IPv6Address

import ntplib

from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime

def perform_ntp_measurement_domain_name(server_name:str="pool.ntp.org",ntp_version:int=3) -> NtpMeasurement | None:
    """
    This method performs a NTP measurement on a NTP server from it's domain name.
    args:
        server_name (str): the name of the ntp server
        ntp_version (int): the version of the ntp that you want to use
    returns:
        NtpMeasurement | None: it returns the NTP measurement object or None if something wrong happened (usually timeouts)
    """
    #get the ip from domain name, the DNS of the server is used
    info=socket.getaddrinfo(server_name, None)[0]
    ip_str=info[4][0]
    #server_ip=ip_address(ip_str)
    try:
        client = ntplib.NTPClient()
        response = client.request(server_name, ntp_version, timeout=6)
        return convert_ntp_response_to_measurement(response=response,server_ip_str=ip_str,server_name=server_name,ntp_version=ntp_version)
    except Exception as e:
        print("Error:", e)
        return None

def perform_ntp_measurement_ip(server_ip_str:str,ntp_version:int=3) -> NtpMeasurement | None:
    """
    This method performs a NTP measurement on a NTP server from it's IP address
    args:
        server_ip_str (str): the ip address of the ntp server in string format
        ntp_version (int): the version of the ntp that you want to use
    returns:
        NtpMeasurement | None: it returns the NTP measurement object or None if something wrong happened (usually timeouts)
    """
    #server_name is not available here. We can only use the ip which is initially a string
    try:
        client = ntplib.NTPClient()
        response = client.request(server_ip_str, ntp_version, timeout=6)
        return convert_ntp_response_to_measurement(response=response,server_ip_str=server_ip_str,server_name="",ntp_version=ntp_version)
    except Exception as e:
        print("Error:", e)
        return None

def convert_ntp_response_to_measurement(response: ntplib.NTPStats, server_ip_str:str, server_name:str, ntp_version:int=3) -> NtpMeasurement | None:
    ref_ip,ref_name=ref_id_to_ip_or_name(response.ref_id,response.stratum)
    server_ip=ip_address(server_ip_str)
    server_info:NtpServerInfo = NtpServerInfo(
        ntp_version=ntp_version,
        ntp_server_ip=server_ip,
        ntp_server_name=server_name,
        ntp_server_ref_parent_ip=ref_ip,
        ref_name=ref_name
    )

    timestamps:NtpTimestamps = NtpTimestamps(
        client_sent_time=PreciseTime(ntplib._to_int(response.ref_timestamp),ntplib._to_frac(response.ref_timestamp)),
        server_recv_time=PreciseTime(ntplib._to_int(response.orig_timestamp),ntplib._to_frac(response.orig_timestamp)),
        server_sent_time=PreciseTime(ntplib._to_int(response.recv_timestamp),ntplib._to_frac(response.recv_timestamp)),
        client_recv_time=PreciseTime(ntplib._to_int(response.tx_timestamp),ntplib._to_frac(response.tx_timestamp))
    )

    main_details:NtpMainDetails = NtpMainDetails(
        offset=response.offset,
        delay=response.delay,
        stratum=response.stratum,
        precision=response.precision,
        reachability=""
    )
    extra_details:NtpExtraDetails = NtpExtraDetails(
        root_delay=response.root_delay,
        ntp_last_sync_time=response.ref_timestamp,
        leap=response.leap
    )
    return NtpMeasurement(server_info, timestamps, main_details, extra_details)

def ref_id_to_ip_or_name(ref_id: int, stratum: int) -> tuple[None, str] | tuple[IPv4Address | IPv6Address, None] | tuple[None, None]:
    """
        Represents a method that converts the reference id to the reference ip or reference name.
        If the stratum is 0 or 1 then we can convert the reference id to it's name (ex: Geostationary Orbit Environment Satellite)
        If the stratum is between 1 and 16 then we can convert the reference id to it's ip
        If the stratum is greater than 15, then we have an invalid stratum.

        args:
            ref_id (int): the reference id of the ntp server
            stratum (int): the stratum level of the ntp server
        returns:
            a tuple of the ip and name of the ntp server. At least one of them is None. If both are None then the stratum is invalid
        """
    if 0 <= stratum <= 1: #we can get the name
        return None,ntplib.ref_id_to_text(ref_id,stratum)
    else:
        if stratum<=15: #we can get an IP address
            return ip_address(socket.inet_ntoa(ref_id.to_bytes(4,'big'))),None #'big' is from big endian
        else:
            return None,None #invalid stratum!!

def print_ntp_measurement(measurement: NtpMeasurement) -> bool:
    """
        It prints the ntp measurement in a human-readable format and returns True if the printing was successful.
    """
    try:
        print("=== NTP Measurement ===")

        #Server Info
        server=measurement.server_info
        print(f"Server Name:           {server.ntp_server_name}")
        print(f"Server IP:             {server.ntp_server_ip}")
        print(f"NTP Version:           {server.ntp_version}")
        print(f"Reference Parent IP:   {server.ntp_server_ref_parent_ip}")
        print(f"Reference Name (Raw):  {server.ref_name}")

        #Timestamps
        timestamps=measurement.timestamps
        print(f"Client sent time:      {ntplib._to_time(timestamps.client_sent_time.seconds,timestamps.client_sent_time.fraction)} :  {timestamps.client_sent_time.seconds} {timestamps.client_sent_time.fraction}")
        print(f"Server recv time:      {ntplib._to_time(timestamps.server_recv_time.seconds,timestamps.server_recv_time.fraction)} :  {timestamps.server_recv_time.seconds} {timestamps.server_recv_time.fraction}")
        print(f"Server sent time:      {ntplib._to_time(timestamps.server_sent_time.seconds,timestamps.server_sent_time.fraction)} :  {timestamps.server_sent_time.seconds} {timestamps.server_sent_time.fraction}")
        print(f"Client recv time:      {ntplib._to_time(timestamps.client_recv_time.seconds,timestamps.client_recv_time.fraction)} :  {timestamps.client_recv_time.seconds} {timestamps.client_recv_time.fraction}")

        #Main Details
        main=measurement.main_details
        print(f"Offset (s):            {main.offset}")
        print(f"Delay (s):             {main.delay}")
        print(f"Stratum:               {main.stratum}")
        print(f"Precision:             {main.precision}")
        print(f"Reachability:          {main.reachability}")

        # Extra Details
        extra=measurement.extra_details
        print(f"Root Delay:            {extra.root_delay}")
        print(f"Last Sync Time:        {extra.ntp_last_sync_time}")
        print(f"Leap:                  {extra.leap}")

        print("=========================")
        return True
    except Exception as e:
        print("Error:", e)
        return False

m=perform_ntp_measurement_domain_name()
print_ntp_measurement(m)