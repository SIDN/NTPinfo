from typing import Any, Optional
from sqlalchemy.orm import Session
from server.app.utils.ip_utils import ip_to_str
from server.app.utils.validate import ensure_utc, is_ip_address, parse_ip
from server.app.services.NtpCalculator import NtpCalculator

from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Optional, Coroutine

from server.app.utils.ripe_fetch_data import check_all_measurements_scheduled
from server.app.utils.perform_measurements import perform_ripe_measurement_domain_name
from server.app.utils.validate import ensure_utc, is_ip_address, parse_ip
from server.app.services.NtpCalculator import NtpCalculator
from server.app.utils.perform_measurements import perform_ntp_measurement_ip, perform_ntp_measurement_domain_name, \
    perform_ripe_measurement_ip
from server.app.utils.perform_measurements import human_date_to_ntp_precise_time, ntp_precise_time_to_human_date, \
    calculate_jitter_from_measurements
from datetime import datetime
from server.app.dtos.ProbeData import ProbeLocation
from server.app.dtos.RipeMeasurement import RipeMeasurement
from server.app.utils.ripe_fetch_data import parse_data_from_ripe_measurement, get_data_from_ripe_measurement
from server.app.db.connection import insert_measurement
from server.app.db.connection import get_measurements_timestamps_ip, get_measurements_timestamps_dn

from server.app.dtos.NtpMainDetails import NtpMainDetails
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.dtos.NtpServerInfo import NtpServerInfo
from server.app.dtos.NtpTimestamps import NtpTimestamps
from server.app.dtos.PreciseTime import PreciseTime
from server.app.dtos.NtpExtraDetails import NtpExtraDetails

def get_format(measurement: NtpMeasurement, jitter: float | None = None) -> dict[str, Any]:
    """
    Format an NTP measurement object into a dictionary suitable for JSON serialization.

    Args:
        measurement (NtpMeasurement): An object representing the NTP measurement result.
        jitter (float|None): Optional jitter value if multiple measurements are performed.

    Returns:
        dict: A dictionary containing key measurement details like this:
            - Server info (ntp version, IP, name, reference IP, reference)
            - Timestamps (client sent time, server receive time, server sent time, client receive time)
            - Measurement metrics (offset, delay, stratum, precision, reachability)
            - Extra details (root delay, last sync time, leap indicator)
    """
    return {
        # "vantage": ip_to_str(measurement.vantage_point_ip),
        "ntp_version": measurement.server_info.ntp_version,
        "ntp_server_ip": ip_to_str(measurement.server_info.ntp_server_ip),
        "ntp_server_name": measurement.server_info.ntp_server_name,
        "ntp_server_ref_parent_ip": ip_to_str(measurement.server_info.ntp_server_ref_parent_ip),
        "ref_name": measurement.server_info.ref_name,

        "client_sent_time": measurement.timestamps.server_sent_time,
        "server_recv_time": measurement.timestamps.server_recv_time,
        "server_sent_time": measurement.timestamps.server_sent_time,
        "client_recv_time": measurement.timestamps.client_recv_time,

        "offset": measurement.main_details.offset,
        "rtt": measurement.main_details.delay,
        "stratum": measurement.main_details.stratum,
        "precision": measurement.main_details.precision,
        "reachability": measurement.main_details.reachability,

        "root_delay": NtpCalculator.calculate_float_time(measurement.extra_details.root_delay),
        "ntp_last_sync_time": measurement.extra_details.ntp_last_sync_time,
        # if it has value = 3 => invalid
        "leap": measurement.extra_details.leap,
        # if the server has multiple IPs addresses we should show them to the client
        "other_server_ips": measurement.server_info.other_server_ips,
        "jitter": jitter
    }

def get_ripe_format(measurement: RipeMeasurement) -> dict[str, Any]:
    """
        Converts a RipeMeasurement object into a standardized dictionary format.

        This function extracts relevant information from the provided RipeMeasurement
        instance—including NTP server info, probe data, timing details, and measurement
        results—and formats it as a plain dictionary.

        Args:
            measurement (RipeMeasurement): The parsed measurement object containing NTP and probe data

        Returns:
            dict[str, Any]:
                A dictionary containing structured measurement data. Keys include:
                - NTP Server info (ntp version, ripe measurement id, IP, name, ref id)
                - Probe data (probe address, probe id in RIPE Atlas, probe location, time to result)
                - Measurement metrics (stratum, poll, precision, root delay, root dispersion, reachability)
                - NTP measurement data (rtt, offset, timestamps)
    """
    probe_location: Optional[ProbeLocation] = measurement.probe_data.probe_location
    return {
        "ntp_version": measurement.ntp_measurement.server_info.ntp_version,
        "ripe_measurement_id": measurement.measurement_id,
        "ntp_server_ip": ip_to_str(measurement.ntp_measurement.server_info.ntp_server_ip),
        "ntp_server_name": measurement.ntp_measurement.server_info.ntp_server_name,
        "probe_addr": {
            "ipv4": ip_to_str(measurement.probe_data.probe_addr[0]),
            "ipv6": ip_to_str(measurement.probe_data.probe_addr[1])
        },
        "probe_id": measurement.probe_data.probe_id,
        "probe_location": {
            "country_code": probe_location.country_code if probe_location else "UNKNOWN",
            "coordinates": probe_location.coordinates if probe_location else (0.0, 0.0)
        },
        "time_to_result": measurement.time_to_result,
        "stratum": measurement.ntp_measurement.main_details.stratum,
        "poll": measurement.poll,
        "precision": measurement.ntp_measurement.main_details.precision,
        "root_delay": measurement.ntp_measurement.extra_details.root_delay,
        "root_dispersion": measurement.root_dispersion,
        "ref_id": measurement.ref_id,
        "probe_count_per_type": {
            'asn': 9,
            'prefix': 1,
            'country': 26,
            'area': 4,
            'random': 0
        },
        "result": [
            {
                "client_sent_time": measurement.ntp_measurement.timestamps.client_sent_time,
                "server_recv_time": measurement.ntp_measurement.timestamps.server_recv_time,
                "server_sent_time": measurement.ntp_measurement.timestamps.server_sent_time,
                "client_recv_time": measurement.ntp_measurement.timestamps.client_recv_time,
                "rtt": measurement.ntp_measurement.main_details.delay,
                "offset": measurement.ntp_measurement.main_details.offset
            }
        ]
    }

def measure(server: str, session: Session, client_ip: Optional[str] = None, jitter_flag: bool = False,
            measurement_no: int = 0) -> tuple[NtpMeasurement, float | None] | None:
    """
    Performs an NTP measurement for a given server (IP or domain name) and stores the result in the database.

    This function determines whether the input is an IP address or a domain name,
    then performs an NTP measurement using the appropriate method. The result is inserted
    into the database and returned.

    Args:
        server (str): A string representing either an IPv4/IPv6 address or a domain name.
        session (Session): The currently active database session.
        client_ip (Optional[str]): The client IP or None if it was not provided.
        jitter_flag (bool): Boolean representing whether the client wants to perform multiple measurements to get the jitter.
        measurement_no (int): How many extra measurements to perform if the jitter_flag is True.

    Returns:
        tuple[NtpMeasurement, float | None] | None:
            - A pair with a populated `NtpMeasurement` object if the measurement is successful, and the jitter if the jitter_flag is True.
            - `None` if an exception occurs during the measurement process.

    Notes:
        - If the server string is empty or improperly formatted, this may raise exceptions internally,
          which are caught and logged to stdout.
        - This function modifies persistent state by inserting a measurement into the database.
    """
    try:
        if is_ip_address(server) is not None:
            m = perform_ntp_measurement_ip(server)
            if m is not None:
                insert_measurement(m, session)
                jitter = calculate_jitter_from_measurements(m, measurement_no) if jitter_flag else None
                return m, jitter
            # the measurement failed
            print("The ntp server " + server + " is not responding.")
            return None
        else:
            ans = perform_ntp_measurement_domain_name(server, client_ip)
            if ans is not None:
                m = ans
                insert_measurement(m, session)

                jitter = calculate_jitter_from_measurements(m, measurement_no) if jitter_flag else None
                return m, jitter
            print("The ntp server " + server + " is not responding.")
            return None
    except Exception as e:
        print("Performing measurement error message:", e)
        return None


def fetch_historic_data_with_timestamps(server: str, start: datetime, end: datetime, session: Session) -> list[NtpMeasurement]:
    """
    Fetches and reconstructs NTP measurements from the database within a specific time range.

    Converts the provided human-readable datetime range into NTP-compatible timestamps,
    queries the database based on whether the server is an IP address or domain name,
    and reconstructs each result as an `NtpMeasurement` object.

    Args:
        server (str): An IPv4/IPv6 address or domain name string for which measurements should be fetched.
        start (datetime): The start of the time range (in local or UTC timezone).
        end (datetime): The end of the time range (in local or UTC timezone).
        session (Session): The currently active database session.

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
        raw_data = get_measurements_timestamps_ip(session, parse_ip(server), start_pt, end_pt)
    else:
        raw_data = get_measurements_timestamps_dn(session, server, start_pt, end_pt)

    measurements = []
    for entry in raw_data:
        vantage_point_ip = entry['vantage_point_ip']
        server_info = NtpServerInfo(entry['ntp_version'], entry['ntp_server_ip'], entry['ntp_server_name'],
                                    entry['ntp_server_ref_parent_ip'], entry['ref_name'], None)
        extra_details = NtpExtraDetails(PreciseTime(entry['root_delay'], entry['root_delay_prec']),
                                        PreciseTime(entry['ntp_last_sync_time'], entry['ntp_last_sync_time_prec']),
                                        0)
        main_details = NtpMainDetails(entry['offset'], entry['RTT'], entry['stratum'],
                                      entry['precision'], entry['reachability'])
        time_stamps = NtpTimestamps(PreciseTime(entry['client_sent'], entry['client_sent_prec']),
                                    PreciseTime(entry['server_recv'], entry['server_recv_prec']),
                                    PreciseTime(entry['server_sent'], entry['server_sent_prec']),
                                    PreciseTime(entry['client_recv'], entry['client_recv_prec']),
                                    )
        measurement = NtpMeasurement(vantage_point_ip, server_info, time_stamps, main_details, extra_details)
        measurements.append(measurement)
    return measurements

def fetch_ripe_data(measurement_id: str) -> list[dict]:
    """
    Fetches and formats NTP measurement data from RIPE Atlas.

    This function retrieves raw measurement data from the RIPE Atlas API using the given
    measurement ID, parses it into internal data structures, and formats it into a
    standardized dictionary format.

    Args:
        measurement_id (str): The unique ID of the RIPE Atlas measurement to fetch

    Returns:
        list[dict]: A list of dictionaries, each representing a formatted NTP measurement
    """
    measurements = parse_data_from_ripe_measurement(get_data_from_ripe_measurement(measurement_id))
    measurements_formated = []
    for m in measurements:
        measurements_formated.append(get_ripe_format(m))

    return measurements_formated


# print(fetch_ripe_data("106549701"))


def perform_ripe_measurement(server: str, client_ip: Optional[str] = None) -> tuple[str, list]:
    """
    Initiate a RIPE Atlas measurement for a given server (IP or domain name).

    This function determines whether the provided server is an IP address or a domain name,
    and triggers the appropriate RIPE measurement. If the server is an IP address,
    a simple measurement is initiated. If it is a domain name, a list of ips near to the client is also returned.

    Args:
        server (str): The IP address or domain name of the target NTP server
        client_ip (Optional[str]): The IP address of the client requesting the measurement (only for domain names)

    Returns:
        tuple[str, list]: A tuple containing:
            - The RIPE measurement ID (as a string)
            - A list of IP addresses (empty if an IP address was provided)

    Raises:
        ValueError: If the server string is invalid or resolution fails in domain name mode
    """
    try:
        ip_address(server)
        measurement_id = perform_ripe_measurement_ip(server)
        return str(measurement_id), []
    except ValueError:
        measurement_id, ip_list = perform_ripe_measurement_domain_name(server, client_ip)
        return str(measurement_id), ip_list


def check_ripe_measurement_complete(measurement_id: str) -> bool:
    """
    Check if a RIPE Atlas measurement has been fully scheduled.

    This function delegates to `check_all_measurements_scheduled()` to verify that
    all requested probes have been scheduled for the given RIPE measurement ID.

    Args:
        measurement_id (str): The ID of the RIPE measurement to check

    Returns:
        bool: True if all requested probes are scheduled, False otherwise

    Raises:
        ValueError: If the RIPE API returns an error or unexpected data
    """
    return check_all_measurements_scheduled(measurement_id=measurement_id)
