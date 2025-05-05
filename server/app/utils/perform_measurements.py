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


def perform_ntp_measurement_ip(server_ip:str="pool.ntp.org",ntp_version:int=3) -> NtpMeasurement | None:
    try:
        client=ntplib.NTPClient()
        response=client.request(server_ip,ntp_version)

        #get the ip from domain name
        info=socket.getaddrinfo(server_ip, None)[0]
        ip_str=info[4][0]
        ip_obj=ip_address(ip_str)

        server_info:NtpServerInfo = NtpServerInfo(
            ntp_version=ntp_version,
            ntp_server_ip=ip_obj,
            ntp_server_name="",
            ntp_server_ref_parent_ip=response.ref_id,
            ref_name=response.ref_id

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
    except Exception as e:
        print("Error", e)
        return None


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
    print(f"Client sent time:      {timestamps.client_sent_time.seconds}.{timestamps.client_sent_time.fraction}")
    print(f"Server recv time:      {timestamps.server_recv_time.seconds}.{timestamps.server_recv_time.fraction}")
    print(f"Server sent time:      {timestamps.server_sent_time.seconds}.{timestamps.server_sent_time.fraction}")
    print(f"Client recv time:      {timestamps.client_recv_time.seconds}.{timestamps.client_recv_time.fraction}")

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


m=perform_ntp_measurement_ip()
print_ntp_measurement(m)