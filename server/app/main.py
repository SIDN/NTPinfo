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
    """
    Performs an NTP measurement for a given server (IP or domain name) and stores the result in the database.

    This function determines whether the input is an IP address or a domain name,
    then performs an NTP measurement using the appropriate method. The result is inserted
    into the database and returned.

    Args:
        server (str): A string representing either an IPv4/IPv6 address or a domain name.

    Returns:
        NtpMeasurement | None:
            - A populated `NtpMeasurement` object if the measurement is successful.
            - `None` if an exception occurs during the measurement process.

    Notes:
        - If the server string is empty or improperly formatted, this may raise exceptions internally,
          which are caught and logged to stdout.
        - This function modifies persistent state by inserting a measurement into the database.
    """
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
    """
    Fetches and reconstructs NTP measurements from the database within a specific time range.

    Converts the provided human-readable datetime range into NTP-compatible timestamps,
    queries the database based on whether the server is an IP address or domain name,
    and reconstructs each result as an `NtpMeasurement` object.

    Args:
        server (str): An IPv4/IPv6 address or domain name string for which measurements should be fetched.
        start (datetime): The start of the time range (in local or UTC timezone).
        end (datetime): The end of the time range (in local or UTC timezone).

    Returns:
        list[NtpMeasurement]: A list of `NtpMeasurement` objects representing the historical data
        for the given server within the time window.

    Notes:
        - The input datetimes are converted to UTC before processing.
        - IP addresses are validated using the `is_ip_address()` utility function.
        - Data is fetched using `get_measurements_timestamps_ip` or `get_measurements_timestamps_dn`
          depending on the server type.
        - The `PreciseTime` wrapper is used to reconstruct accurate timestamps from database fields.
    """
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
