from ipaddress import IPv4Address, IPv6Address

from server.app.models.PreciseTime import PreciseTime
from server.app.models.NtpMeasurement import NtpMeasurement
from psycopg_pool import ConnectionPool
from typing import Any


def insert_measurement(measurement: NtpMeasurement, pool: ConnectionPool) -> None:
    """
    Inserts a new NTP measurement into the database.

    This function stores both the raw timestamps (in the `times` table) and the
    processed measurement data (in the `measurements` table). It uses a connection pool
    for efficiency and wraps operations in a transaction to ensure atomicity.

    Args:
        measurement (NtpMeasurement): The measurement data to store.
        pool: A psycopg `ConnectionPool` used for managing PostgreSQL connections efficiently.

    Notes:
        - Timestamps are stored with both second and fractional parts.
        - A foreign key (`time_id`) is used to link `measurements` to the `times` table.
        - Any failure within the transaction block results in automatic rollback.
    """

    with pool.connection() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO times (client_sent, client_sent_prec,
                                               server_recv, server_recv_prec,
                                               server_sent, server_sent_prec,
                                               client_recv, client_recv_prec)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                            """, (
                                measurement.timestamps.client_sent_time.seconds,
                                measurement.timestamps.client_sent_time.fraction,
                                measurement.timestamps.server_recv_time.seconds,
                                measurement.timestamps.server_recv_time.fraction,
                                measurement.timestamps.server_sent_time.seconds,
                                measurement.timestamps.server_sent_time.fraction,
                                measurement.timestamps.client_recv_time.seconds,
                                measurement.timestamps.client_recv_time.fraction
                            ))

                # used because we have it as a foreign key in the measurements table
                row = cur.fetchone()
                if row is None:
                    raise ValueError("Expected a result from INSERT RETURNING id, but got None")
                time_id = row[0]

            cur.execute("""
                        INSERT INTO measurements(ntp_server_ip, ntp_server_name,
                                                 ntp_version, ntp_server_ref_parent,
                                                 ref_name, time_id,
                                                 time_offset, delay,
                                                 stratum, precision,
                                                 reachability,
                                                 root_delay,
                                                 ntp_last_sync_time,
                                                 root_delay_prec,
                                                 ntp_last_sync_time_prec)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            measurement.server_info.ntp_server_ip, measurement.server_info.ntp_server_name,
                            measurement.server_info.ntp_version, measurement.server_info.ntp_server_ref_parent_ip,
                            measurement.server_info.ref_name, time_id,
                            measurement.main_details.offset, measurement.main_details.delay,
                            measurement.main_details.stratum, measurement.main_details.precision,
                            measurement.main_details.reachability,
                            measurement.extra_details.root_delay.seconds,
                            measurement.extra_details.ntp_last_sync_time.seconds,
                            measurement.extra_details.root_delay.fraction,
                            measurement.extra_details.ntp_last_sync_time.fraction
                        ))


def get_all_measurements(pool: ConnectionPool) -> list[tuple]:
    """
    Retrieves all measurements from the database.

    This function performs a join between the `measurements` and `times` tables,
    returning every record in the database without any filtering.

    Args:
        pool: A psycopg `ConnectionPool` used to acquire database connections.

    Returns:
        list: A list of tuples, each representing a full measurement record joined with its timestamps.
    """
    with pool.connection() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT *
                            FROM measurements m
                                     JOIN times t ON m.time_id = t.id
                            """)
                return cur.fetchall()


def get_measurements_timestamps_ip(pool: ConnectionPool, ip: IPv4Address | IPv6Address | None, start: PreciseTime,
                                   end: PreciseTime) -> list[
    dict[str, Any]]:
    """
    Fetches measurements for a specific IP address within a precise time range.

    This function queries the `measurements` table, joined with the `times` table,
    and filters the results by:
        - The NTP server IP (`ntp_server_ip`)
        - The timestamp range (`client_sent` field) between `start` and `end`

    Args:
        pool: A psycopg `ConnectionPool` used to manage PostgreSQL connections.
        ip (IPv4Address | IPv6Address): The IP address of the NTP server.
        start (PreciseTime): The start of the time range to filter on.
        end (PreciseTime): The end of the time range to filter on.

    Returns:
        list[dict]: A list of measurement records (as dictionaries), each including:
            - Measurement metadata (IP, version, stratum, etc.)
            - Timing data (client/server send/receive with fractions)
    """
    with pool.connection() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT m.id,
                                   m.ntp_server_ip,
                                   m.ntp_server_name,
                                   m.ntp_version,
                                   m.ntp_server_ref_parent,
                                   m.ref_name,
                                   m.time_offset,
                                   m.delay,
                                   m.stratum,
                                   m.precision,
                                   m.reachability,
                                   m.root_delay,
                                   m.root_delay_prec,
                                   m.ntp_last_sync_time,
                                   m.ntp_last_sync_time_prec,
                                   t.client_sent,
                                   t.client_sent_prec,
                                   t.server_recv,
                                   t.server_recv_prec,
                                   t.server_sent,
                                   t.server_sent_prec,
                                   t.client_recv,
                                   t.client_recv_prec
                            FROM measurements m
                                     JOIN times t ON m.time_id = t.id
                            WHERE m.ntp_server_ip = %(ip)s
                              AND (t.client_sent >= %(start_t)s AND t.client_sent <= %(end_t)s)
                            """, {
                                "ip": ip,
                                "start_t": start.seconds,
                                "start_t_precision": start.fraction,
                                "end_t": end.seconds,
                                "end_t_precision": end.fraction
                            })
                columns = [
                    "id",
                    "ntp_server_ip",
                    "ntp_server_name",
                    "ntp_version",
                    "ntp_server_ref_parent_ip",
                    "ref_name",
                    "offset",
                    "delay",
                    "stratum",
                    "precision",
                    "reachability",
                    "root_delay",
                    "root_delay_prec",
                    "ntp_last_sync_time",
                    "ntp_last_sync_time_prec",
                    "client_sent",
                    "client_sent_prec",
                    "server_recv",
                    "server_recv_prec",
                    "server_sent",
                    "server_sent_prec",
                    "client_recv",
                    "client_recv_prec"
                ]

                return [dict(zip(columns, row)) for row in cur]


def get_measurements_timestamps_dn(pool: ConnectionPool, dn: str, start: PreciseTime, end: PreciseTime) -> list[
    dict[str, Any]]:
    """
    Fetches measurements for a specific domain name within a precise time range.

    Similar to `get_measurements_timestamps_ip`, but filters by `ntp_server_name`
    instead of `ntp_server_ip`.

    Args:
        pool: A psycopg `ConnectionPool` used to manage PostgreSQL connections.
        dn (str): The domain name of the NTP server.
        start (PreciseTime): The start of the time range to filter on.
        end (PreciseTime): The end of the time range to filter on.

    Returns:
        list[dict]: A list of measurement records (as dictionaries), each including:
            - Measurement metadata (domain name, version, etc.)
            - Timing data (client/server send/receive with precision)
    """
    with pool.connection() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT m.id,
                                   m.ntp_server_ip,
                                   m.ntp_server_name,
                                   m.ntp_version,
                                   m.ntp_server_ref_parent,
                                   m.ref_name,
                                   m.time_offset,
                                   m.delay,
                                   m.stratum,
                                   m.precision,
                                   m.reachability,
                                   m.root_delay,
                                   m.root_delay_prec,
                                   m.ntp_last_sync_time,
                                   m.ntp_last_sync_time_prec,
                                   t.client_sent,
                                   t.client_sent_prec,
                                   t.server_recv,
                                   t.server_recv_prec,
                                   t.server_sent,
                                   t.server_sent_prec,
                                   t.client_recv,
                                   t.client_recv_prec
                            FROM measurements m
                                     JOIN times t ON m.time_id = t.id
                            WHERE m.ntp_server_name = %(dn)s
                              AND (t.client_sent >= %(start_t)s AND t.client_sent <= %(end_t)s)
                            """, {
                                "dn": dn,
                                "start_t": start.seconds,
                                # "start_t_precision": start.fraction,
                                "end_t": end.seconds,
                                # "end_t_precision": end.fraction
                            })
                columns = [
                    "id",
                    "ntp_server_ip",
                    "ntp_server_name",
                    "ntp_version",
                    "ntp_server_ref_parent_ip",
                    "ref_name",
                    "offset",
                    "delay",
                    "stratum",
                    "precision",
                    "reachability",
                    "root_delay",
                    "root_delay_prec",
                    "ntp_last_sync_time",
                    "ntp_last_sync_time_prec",
                    "client_sent",
                    "client_sent_prec",
                    "server_recv",
                    "server_recv_prec",
                    "server_sent",
                    "server_sent_prec",
                    "client_recv",
                    "client_recv_prec"
                ]

                return [dict(zip(columns, row)) for row in cur]
