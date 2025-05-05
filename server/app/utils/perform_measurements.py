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
            client_sent_time=PreciseTime(ntplib._to_int(response.ref_timestamp),ntplib._to_time(response.ref_timestamp)),
            server_recv_time=PreciseTime(ntplib._to_int(response.orig_timestamp),ntplib._to_time(response.orig_timestamp)),
            server_sent_time=PreciseTime(ntplib._to_int(response.recv_timestamp),ntplib._to_time(response.recv_timestamp)),
            client_recv_time=PreciseTime(ntplib._to_int(response.tx_timestamp),ntplib._to_time(response.tx_timestamp))
        )


        main_details:NtpMainDetails = NtpMainDetails(
            offset=response.offset(),
            delay=response.delay(),
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