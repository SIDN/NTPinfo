from ipaddress import IPv4Address, IPv6Address

from sqlalchemy import Row
from sqlalchemy.orm import Session

from server.app.dtos.NtpExtraDetails import NtpExtraDetails
from server.app.dtos.NtpMainDetails import NtpMainDetails
from server.app.dtos.NtpServerInfo import NtpServerInfo
from server.app.dtos.NtpTimestamps import NtpTimestamps
from server.app.utils.ip_utils import ip_to_str
from server.app.models.Measurement import Measurement
from server.app.models.Time import Time
from server.app.dtos.PreciseTime import PreciseTime
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.models.CustomError import InvalidMeasurementDataError
from server.app.models.CustomError import DatabaseInsertError
from server.app.models.CustomError import MeasurementQueryError
from typing import Any


def row_to_dict(m: Measurement, t: Time) -> dict[str, Any]:
    """
    Converts a Measurement and Time SQLAlchemy row into a dictionary.

    Args:
        m (Measurement): The measurement row containing NTP measurement data
        t (Time): The time row containing timestamp data for the measurement

    Returns:
        dict[str, Any]: A dictionary representation of the combined measurement and timestamp data
    """
    return {
        "id": m.id,
        "vantage_point_ip": m.vantage_point_ip,
        "ntp_server_ip": m.ntp_server_ip,
        "ntp_server_name": m.ntp_server_name,
        "ntp_version": m.ntp_version,
        "ntp_server_ref_parent_ip": m.ntp_server_ref_parent,
        "ref_name": m.ref_name,
        "offset": m.time_offset,
        "RTT": m.rtt,
        "stratum": m.stratum,
        "precision": m.precision,
        "reachability": m.reachability,
        "root_delay": m.root_delay,
        "root_delay_prec": m.root_delay_prec,
        "poll": m.poll,
        "root_dispersion": m.root_dispersion,
        "root_dispersion_prec": m.root_dispersion_prec,
        "ntp_last_sync_time": m.ntp_last_sync_time,
        "ntp_last_sync_time_prec": m.ntp_last_sync_time_prec,
        "client_sent": t.client_sent,
        "client_sent_prec": t.client_sent_prec,
        "server_recv": t.server_recv,
        "server_recv_prec": t.server_recv_prec,
        "server_sent": t.server_sent,
        "server_sent_prec": t.server_sent_prec,
        "client_recv": t.client_recv,
        "client_recv_prec": t.client_recv_prec
    }


def rows_to_dicts(rows: list[Row[tuple[Measurement, Time]]]) -> list[dict[str, Any]]:
    """
    Converts a list of Measurement-Time row tuples into a list of dictionaries.

    Args:
        rows (list[Row[tuple[Measurement, Time]]]): List of database rows containing Measurement and Time

    Returns:
        list[dict[str, Any]]: A list of dictionaries where each dictionary contains combined data from Measurement and Time
    """
    return [row_to_dict(row.Measurement, row.Time) for row in rows]


def dict_to_measurement(entry: dict[str, Any]) -> NtpMeasurement:
    """
    Converts a dictionary representation of a measurement into an NtpMeasurement object.

    Args:
        entry (dict[str, Any]): A dictionary containing the keys needed to construct an NtpMeasurement object

    Returns:
        NtpMeasurement: A fully constructed NtpMeasurement using the provided data

    Raises:
        InvalidMeasurementDataError: If required keys are missing or construction fails due to invalid types/values
    """

    required_keys = [
        'vantage_point_ip', 'ntp_server_ip', 'ntp_server_name', 'ntp_version', 'ntp_server_ref_parent_ip',
        'ref_name', 'offset', 'RTT', 'stratum', 'precision', 'reachability',
        'root_delay', 'root_delay_prec', 'poll', 'root_dispersion', 'root_dispersion_prec',
        'ntp_last_sync_time', 'ntp_last_sync_time_prec',
        'client_sent', 'client_sent_prec', 'server_recv', 'server_recv_prec',
        'server_sent', 'server_sent_prec', 'client_recv', 'client_recv_prec'
    ]

    missing = [k for k in required_keys if k not in entry]
    if missing:
        raise InvalidMeasurementDataError(f"Missing required keys: {missing}")

    try:
        vantage_point_ip = entry['vantage_point_ip']
        server_info = NtpServerInfo(entry['ntp_version'], entry['ntp_server_ip'], entry['ntp_server_name'],
                                    entry['ntp_server_ref_parent_ip'], entry['ref_name'])
        extra_details = NtpExtraDetails(PreciseTime(entry['root_delay'], entry['root_delay_prec']),
                                        entry['poll'],
                                        PreciseTime(entry['root_dispersion'], entry['root_dispersion_prec']),
                                        PreciseTime(entry['ntp_last_sync_time'], entry['ntp_last_sync_time_prec']),
                                        0)
        main_details = NtpMainDetails(entry['offset'], entry['RTT'], entry['stratum'],
                                      entry['precision'], entry['reachability'])
        time_stamps = NtpTimestamps(PreciseTime(entry['client_sent'], entry['client_sent_prec']),
                                    PreciseTime(entry['server_recv'], entry['server_recv_prec']),
                                    PreciseTime(entry['server_sent'], entry['server_sent_prec']),
                                    PreciseTime(entry['client_recv'], entry['client_recv_prec']),
                                    )
        return NtpMeasurement(vantage_point_ip, server_info, time_stamps, main_details, extra_details)
    except Exception as e:
        raise InvalidMeasurementDataError(f"Failed to build NtpMeasurement: {e}")


def rows_to_measurements(rows: list[Row[tuple[Measurement, Time]]]) -> list[NtpMeasurement]:
    """
    Converts a list of Measurement-Time row tuples into NtpMeasurement objects.

    Args:
        rows (list[Row[tuple[Measurement, Time]]]): List of database rows containing Measurement and Time data.

    Returns:
        list[NtpMeasurement]: A list of NtpMeasurement objects created from the row data.
    """
    return [dict_to_measurement(d) for d in rows_to_dicts(rows)]


def insert_measurement(measurement: NtpMeasurement, session: Session) -> None:
    """
    Inserts a new NTP measurement into the database.

    This function stores both the raw timestamps (in the `times` table) and the
    processed measurement data (in the `measurements` table). It uses a connection pool
    for efficiency and wraps operations in a transaction to ensure atomicity.

    Args:
        measurement (NtpMeasurement): The measurement data to store.
        session (Session): The currently active database session.

    Notes:
        - Timestamps are stored with both second and fractional parts.
        - A foreign key (`time_id`) is used to link `measurements` to the `times` table.
        - Any failure within the transaction block results in automatic rollback.

    Raises:
        DatabaseInsertError: If inserting the measurement or timestamps fails
    """
    try:
        time = Time(
            client_sent=measurement.timestamps.client_sent_time.seconds,
            client_sent_prec=measurement.timestamps.client_sent_time.fraction,
            server_recv=measurement.timestamps.server_recv_time.seconds,
            server_recv_prec=measurement.timestamps.server_recv_time.fraction,
            server_sent=measurement.timestamps.server_sent_time.seconds,
            server_sent_prec=measurement.timestamps.server_sent_time.fraction,
            client_recv=measurement.timestamps.client_recv_time.seconds,
            client_recv_prec=measurement.timestamps.client_recv_time.fraction
        )
        session.add(time)
        session.flush()
        measurement_entry = Measurement(
            vantage_point_ip=ip_to_str(measurement.vantage_point_ip),
            ntp_server_ip=ip_to_str(measurement.server_info.ntp_server_ip),
            ntp_server_name=measurement.server_info.ntp_server_name,
            ntp_version=measurement.server_info.ntp_version,
            ntp_server_ref_parent=ip_to_str(measurement.server_info.ntp_server_ref_parent_ip),
            ref_name=measurement.server_info.ref_name,
            time_id=time.id,
            time_offset=measurement.main_details.offset,
            rtt=measurement.main_details.rtt,
            stratum=measurement.main_details.stratum,
            precision=measurement.main_details.precision,
            reachability=measurement.main_details.reachability,
            root_delay=measurement.extra_details.root_delay.seconds,
            root_delay_prec=measurement.extra_details.root_delay.fraction,
            poll=measurement.extra_details.poll,
            root_dispersion=measurement.extra_details.root_dispersion.seconds,
            root_dispersion_prec=measurement.extra_details.root_dispersion.fraction,
            ntp_last_sync_time=measurement.extra_details.ntp_last_sync_time.seconds,
            ntp_last_sync_time_prec=measurement.extra_details.ntp_last_sync_time.fraction,
            timestamps=time
        )
        session.add(measurement_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        raise DatabaseInsertError(f"Failed to insert measurement: {e}")


def get_measurements_timestamps_ip(session: Session, ip: IPv4Address | IPv6Address | None, start: PreciseTime,
                                   end: PreciseTime) -> list[NtpMeasurement]:
    """
    Fetches measurements for a specific IP address within a precise time range.

    This function queries the `measurements` table, joined with the `times` table,
    and filters the results by:
        - The NTP server IP (`ntp_server_ip`)
        - The timestamp range (`client_sent` field) between `start` and `end`

    Args:
        session (Session): The currently active database session.
        ip (IPv4Address | IPv6Address): The IP address of the NTP server.
        start (PreciseTime): The start of the time range to filter on.
        end (PreciseTime): The end of the time range to filter on.

    Returns:
        list[dict]: A list of measurement records (as dictionaries), each including:
            - Measurement metadata (IP, version, stratum, etc.)
            - Timing data (client/server send/receive with fractions)

    Raises:
        MeasurementQueryError: If the database query fails
    """
    try:
        query = (
            session.query(Measurement, Time)
            .join(Time, Measurement.time_id == Time.id)
            .filter(
                Measurement.ntp_server_ip == str(ip),
                Time.client_sent >= start.seconds,
                Time.client_sent <= end.seconds
            )
        )
        return rows_to_measurements(query.all())
    except Exception as e:
        raise MeasurementQueryError(f"Failed to fetch measurements for IP {ip}: {e}")


def get_measurements_timestamps_dn(session: Session, dn: str, start: PreciseTime, end: PreciseTime) -> list[
    NtpMeasurement]:
    """
    Fetches measurements for a specific domain name within a precise time range.

    Similar to `get_measurements_timestamps_ip`, but filters by `ntp_server_name`
    instead of `ntp_server_ip`.

    Args:
        session (Session): The currently active database session.
        dn (str): The domain name of the NTP server.
        start (PreciseTime): The start of the time range to filter on.
        end (PreciseTime): The end of the time range to filter on.

    Returns:
        list[dict]: A list of measurement records (as dictionaries), each including:
            - Measurement metadata (domain name, version, etc.)
            - Timing data (client/server send/receive with precision)

    Raises:
        MeasurementQueryError: If the database query fails
    """
    try:
        query = (
            session.query(Measurement, Time)
            .join(Time, Measurement.time_id == Time.id)
            .filter(
                Measurement.ntp_server_name == dn,
                Time.client_sent >= start.seconds,
                Time.client_sent <= end.seconds
            )
        )
        return rows_to_measurements(query.all())
    except Exception as e:
        raise MeasurementQueryError(f"Failed to fetch measurements for domain name: {dn}: {e}")


def get_measurements_for_jitter_ip(session: Session, ip: IPv4Address | IPv6Address | None, number: int = 7) -> list[
    NtpMeasurement]:
    """
    Fetches the last specified number (default 7) of measurements for specific IP address for calculating the jitter.

    This function queries the `measurements` table, joined with the `times` table,
    and filters the results by: The NTP server IP (`ntp_server_ip`) and limits the result to the number specified.

    Args:
        session (Session): The currently active database session.
        ip (IPv4Address | IPv6Address): The IP address of the NTP server.
        number (int): The number of measurements to get

    Returns:
        list[dict]: A list of measurement records (as dictionaries), each including
            - Measurement metadata (IP, version, stratum, etc.)
            - Timing data (client/server send/receive with fractions)

    Raises:
        MeasurementQueryError: If the database query fails
    """
    try:
        query = (
            session.query(Measurement, Time)
            .join(Time, Measurement.time_id == Time.id)
            .filter(
                Measurement.ntp_server_ip == str(ip)
            )
            .limit(number)
        )
        return rows_to_measurements(query.all())
    except Exception as e:
        raise MeasurementQueryError(f"Failed to fetch measurements for jitter for IP {ip}: {e}")
