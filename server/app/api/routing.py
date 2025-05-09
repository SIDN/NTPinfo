from ipaddress import IPv4Address, IPv6Address

from fastapi import FastAPI, HTTPException
from server.app.main import measure
from server.app.main import fetch_historic_data_with_timestamps
from server.app.models.NtpMeasurement import NtpMeasurement
from datetime import datetime, timezone
from typing import Any, Optional, Coroutine

from ipaddress import ip_address


def ip_to_str(ip: Optional[IPv4Address | IPv6Address]) -> Optional[str]:
    """
    Converts an IP address (either IPv4 or IPv6) to its string representation.

    This function takes an `IPv4Address` or `IPv6Address` object and converts it to
    a string. If the input IP is `None`, it returns `None`.

    Args:
        ip (Optional[IPv4Address | IPv6Address]): The IP address to be converted.
            It can be either an `IPv4Address` or `IPv6Address` object, or `None`.

    Returns:
        Optional[str]: The string representation of the IP address, or `None` if the input is `None`.
    """
    return str(ip) if ip is not None else None


def get_format(measurement: NtpMeasurement) -> dict[str, Any]:
    """
    Format an NTP measurement object into a dictionary suitable for JSON serialization.

    Args:
        measurement (NtpMeasurement): An object representing the NTP measurement result.

    Returns:
        dict: A dictionary containing key measurement details like this:
            - Server info (ntp version, IP, name, reference IP, reference)
            - Timestamps (client sent time, server receive time, server sent time, client receive time)
            - Measurement metrics (offset, delay, stratum, precision, reachability)
            - Extra details (root delay, last sync time, leap indicator)
    """
    return {
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
        "delay": measurement.main_details.delay,
        "stratum": measurement.main_details.stratum,
        "precision": measurement.main_details.precision,
        "reachability": measurement.main_details.reachability,

        "root_delay": measurement.extra_details.root_delay,
        "ntp_last_sync_time": measurement.extra_details.ntp_last_sync_time,
        # if it has value = 3 => invalid
        "leap": measurement.extra_details.leap
    }


app = FastAPI()
"""
Creates a FastAPI application instance.
This instance is used to define all API endpoints and serve the application.
"""


@app.get("/")
def read_root() -> dict[str, str]:
    """
    Root endpoint for basic service health check.

    Returns:
        dict: A simple JSON message {"Hello": "World"}
    """
    return {"Hello": "World"}


@app.post("/measurements/")
async def read_data_measurement(server: str) -> dict[str, Any]:
    """
    Compute a live NTP measurement for a given server (IP or domain).

    This endpoint attempts to measure NTP synchronization metrics for a provided server.
    It uses the `measure()` function to perform the measurement, and returns a formatted
    result using `get_format()`.

    Args:
        server (str): IP address (IPv4/IPv6) or domain name of the NTP server.

    Returns:
        dict: On success, returns {"measurement": <formatted_measurement_dict>}
              On failure, returns {"Error": "Could not perform measurement, dns or ip not reachable."}

    Raises:
        HTTPException: 400 error if `server` parameter is empty.
    """
    if len(server) == 0:
        raise HTTPException(status_code=400, detail="Either 'ip' or 'dn' must be provided")
    result = measure(server)
    if result is not None:
        return {
            "measurement": get_format(result)
        }
    return {
        "Error": "Could not perform measurement, dns or ip not reachable."
    }


@app.get("/measurements/history/")
async def read_historic_data_time(server: str,
                                  start: datetime, end: datetime) -> dict[str, list[dict[str, Any]]]:
    """
    Retrieve historic NTP measurements for a given server and optional time range.

    This endpoint fetches past measurement data for the specified server using the
    `fetch_historic_data_with_timestamps()` function. It can optionally filter results
    based on a time range (start and end datetime).

    Args:
        server (str): IP address or domain name of the NTP server.
        start (datetime, optional): Start timestamp for data filtering.
        end (datetime, optional): End timestamp for data filtering.

    Returns:
        dict: A dictionary containing a list of formatted measurements under "measurements".

    Raises:
        HTTPException: 400 error if `server` parameter is empty.
    """
    if len(server) == 0:
        raise HTTPException(status_code=400, detail="Either 'ip' or 'domain name' must be provided")

    if start >= end:
        raise HTTPException(status_code=400, detail="'start' must be earlier than 'end'")

    if end > datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="'end' cannot be in the future")

    # utc_time_from_9am = datetime(2025, 5, 7, 7, 0, tzinfo=timezone.utc)
    # current_utc_time = datetime(2025, 5, 7, 11, 15, tzinfo=timezone.utc)
    #
    # start_test = utc_time_from_9am
    # end_test = current_utc_time
    result = fetch_historic_data_with_timestamps(server, start, end)
    formatted_results = [get_format(entry) for entry in result]
    return {
        "measurements": formatted_results
    }
