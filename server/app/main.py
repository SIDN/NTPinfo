from ipaddress import IPv4Address, IPv6Address

from server.app.db.connection import insert_measurement
from server.app.db.connection import get_measurements_timestamps_ip, get_measurements_timestamps_dn
from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime
from server.app.db.config import pool
from server.app.utils.perform_measurements import perform_ntp_measurement_ip
from server.app.utils.perform_measurements import human_date_to_ntp_precise_time
from server.app.utils.perform_measurements import perform_ntp_measurement_domain_name
from server.app.utils.validate import is_ip_address
from server.app.utils.validate import ensure_utc
from server.app.utils.validate import parse_ip
from datetime import datetime


def measure(server: str) -> NtpMeasurement | None:
    # t1 = PreciseTime(10000, 0)
    # t2 = PreciseTime(10002, 2 ** 27)
    # t3 = PreciseTime(10003, 10000)
    # t4 = PreciseTime(10004, 10000)
    # server_details = NtpServerInfo(3, IPv4Address('192.0.2.1'), "local", IPv6Address('2001:db8::1'), "reference")
    # times = NtpTimestamps(t1, t2, t3, t4)
    # main_details = NtpMainDetails(0.009, 0, 1, 0, "stable")
    # extra = NtpExtraDetails(PreciseTime(100000, 0), PreciseTime(100000, 0), 0)
    #
    # m = NtpMeasurement(server_details, times, main_details, extra
    try:
        if is_ip_address(server) is not None:
            m = perform_ntp_measurement_ip(server)
            insert_measurement(m, pool)
            return m
        else:
            m = perform_ntp_measurement_domain_name(server)
            insert_measurement(m, pool)
            return m
    except Exception as e:
        print("Performing measurement error message:", e)
        return None


def fetch_historic_data_with_timestamps(server: str, start: datetime, end: datetime):
    start_pt = human_date_to_ntp_precise_time(ensure_utc(start))
    end_pt = human_date_to_ntp_precise_time(ensure_utc(end))
    print(start_pt)
    print(end_pt)
    # start_pt = PreciseTime(450, 20)
    # end_pt = PreciseTime(1200, 100)
    # raw_data = get_measurements_timestamps_ip(pool, ip, start_pt, end_pt)
    raw_data = None
    if is_ip_address(server) is not None:
        raw_data = get_measurements_timestamps_ip(pool, parse_ip(server), start_pt, end_pt)
    else:
        raw_data = get_measurements_timestamps_dn(pool, server, start_pt, end_pt)

    measurements = []
    for entry in raw_data:
        server_info = NtpServerInfo(entry['ntp_version'], entry['ntp_server_ip'], entry['ntp_server_name'],
                                    entry['ntp_server_ref_parent_ip'], entry['ref_name'])
        extra_details = NtpExtraDetails(PreciseTime(entry['root_delay'], entry['root_delay_prec']),
                                        PreciseTime(entry['ntp_last_sync_time'], entry['ntp_last_sync_time_prec']),
                                        0)
        main_details = NtpMainDetails(entry['offset'], entry['delay'], entry['stratum'],
                                      entry['precision'], entry['reachability'])
        time_stamps = NtpTimestamps(PreciseTime(entry['client_sent'], entry['client_sent_prec']),
                                    PreciseTime(entry['server_recv'], entry['server_recv_prec']),
                                    PreciseTime(entry['server_sent'], entry['server_sent_prec']),
                                    PreciseTime(entry['client_recv'], entry['client_recv_prec']),
                                    )
        measurement = NtpMeasurement(server_info, time_stamps, main_details, extra_details)
        measurements.append(measurement)
    return measurements
