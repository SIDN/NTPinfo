import socket
from ipaddress import ip_address

import ntplib
from time import ctime

from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime

def perform_ntp_measurement_domain_name(server_name:str="pool.ntp.org",ntp_version:int=3) -> NtpMeasurement | None:
    #get the ip from domain name, the DNS of the server is used
    info=socket.getaddrinfo(server_name, None)[0]
    ip_str=info[4][0]
    server_ip=ip_address(ip_str)
    try:
        client = ntplib.NTPClient()
        response = client.request(server_name, ntp_version, timeout=11)
        return convert_ntp_response_to_measurement(server_ip=server_ip,server_name=server_name,ntp_version=ntp_version,response=response)
    except Exception as e:
        print("Error:", e)
        return None

def perform_ntp_measurement_ip(server_ip:str,ntp_version:int=3) -> NtpMeasurement | None:
    #server_name is not available here
    try:
        client = ntplib.NTPClient()
        response = client.request(server_ip, ntp_version, timeout=11)
        return convert_ntp_response_to_measurement(server_ip=server_ip,server_name="",ntp_version=ntp_version,response=response)
    except Exception as e:
        print("Error:", e)
        return None

def convert_ntp_response_to_measurement(response: ntplib.NTPStats, server_ip, server_name:str, ntp_version:int=3) -> NtpMeasurement | None:
    server_info:NtpServerInfo = NtpServerInfo(
        ntp_version=ntp_version,
        ntp_server_ip=server_ip,
        ntp_server_name=server_name,
        ntp_server_ref_parent_ip=response.ref_id,
        ref_name=ntplib.ref_id_to_text(response.ref_id,response.stratum)

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

# def ref_id_to_ip(ref_id:str,stratum) -> str | None:
#     fields = (ref_id >> 24 & 0xff, ref_id >> 16 & 0xff,
#               ref_id >> 8 & 0xff, ref_id & 0xff)
#     if 0 <= stratum <= 1:
#         ip = "%c%c%c%c" % fields
#         return ip
def print_ntp_measurement(measurement: NtpMeasurement):
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

m=perform_ntp_measurement_domain_name()
print_ntp_measurement(m)