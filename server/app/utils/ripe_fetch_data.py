from ipaddress import ip_address, IPv4Address, IPv6Address

import requests
import os
from dotenv import load_dotenv

from server.app.models.PreciseTime import PreciseTime
from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.ProbeData import ProbeLocation, ProbeData
from server.app.models.RipeMeasurement import RipeMeasurement
from server.app.utils.perform_measurements import convert_float_to_precise_time
from typing import Any, cast

load_dotenv()


def check_all_measurements_scheduled(measurement_id: str) -> bool:
    """
    Check if all RIPE Atlas probes for a given measurement have been scheduled.

    This function compares the number of probes requested with the number of probes successfully
    scheduled. If all requested probes are scheduled, it returns True. Otherwise,
    it returns False

    Args:
        measurement_id (str): The ID of the RIPE Atlas measurement to check

    Returns:
        bool: True if all requested probes have been scheduled, False otherwise

    Raises:
        ValueError: If the RIPE API returns an error or if the probe count data
                    is missing or invalid
    """
    url = f"https://atlas.ripe.net/api/v2/measurements/{measurement_id}/"

    headers = {
        "Authorization": f"Key {os.getenv('RIPE_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    json_data = response.json()
    if isinstance(json_data, dict) and 'error' in json_data:
        raise ValueError(
            f"RIPE API error: {json_data['error']['title']} - {json_data['error']['detail']}")
    probes_requested: int = json_data.get("probes_requested", -1)
    probes_scheduled: int = json_data.get("probes_scheduled", -1)
    # status = json_data["status"].get("name", "No status")
    if probes_requested == -1:
        raise ValueError(
            f"RIPE API error: The number of scheduled probes is negative")
    return probes_requested == probes_scheduled  # and status == "Stopped"


def get_data_from_ripe_measurement(measurement_id: str) -> list[dict[str, Any]]:
    """
    Fetches raw measurement results from the RIPE Atlas API.

    This function queries the RIPE Atlas v2 API using the provided measurement ID,
    authenticates with an API key stored in the RIPE_KEY environment variable, and
    returns the parsed JSON response as a list of dictionaries.

    Args:
        measurement_id (str): The RIPE Atlas measurement ID to fetch results for

    Returns:
        list[dict[str, Any]]: A list of measurement result entries as dictionaries

    Raises:
        requests.RequestException: If the HTTP request fails.
        ValueError: If the response cannot be parsed as JSON.

    Notes:
        - Requires the `RIPE_KEY` environment variable to be set with a valid API key.
    """
    url = f"https://atlas.ripe.net/api/v2/measurements/{measurement_id}/results/"

    headers = {
        "Authorization": f"Key {os.getenv('RIPE_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    json_data = response.json()
    if isinstance(json_data, dict) and 'error' in json_data:
        raise ValueError(
            f"RIPE API error: {json_data['error']['title']} - {json_data['error']['detail']}")

    # print("Status Code:", response.status_code)
    # print("Response JSON:", response.json())
    return cast(list[dict[str, Any]], response.json())


def get_probe_data_from_ripe_by_id(probe_id: str) -> dict[str, Any]:
    """
    Retrieves detailed information about a specific RIPE Atlas probe by its ID.

    This function sends a GET request to the RIPE Atlas API to fetch metadata
    about the specified probe. The request is authenticated using the RIPE API key
    stored in the RIPE_KEY environment variable.

    Args:
        probe_id (str): The ID of the RIPE Atlas probe to fetch information for

    Returns:
        dict[str, Any]: A dictionary containing metadata about the probe

    Raises:
        requests.RequestException: If the HTTP request fails
        ValueError: If the response is not valid JSON or is unexpected

    Notes:
        - Requires the `RIPE_KEY` environment variable to be set with a valid API key.
    """
    url = f"https://atlas.ripe.net/api/v2/probes/{probe_id}/"

    headers = {
        "Authorization": f"Key {os.getenv('RIPE_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    # print("Status Code:", response.status_code)
    # print("Response JSON:", response.json())
    return cast(dict[str, Any], response.json())


def parse_probe_data(probe_response: dict) -> ProbeData:
    """
    Parses probe metadata received from the RIPE Atlas API into a ProbeData object.

    This function extracts relevant information such as the probe ID, IP addresses,
    country code, and coordinates from the API response.

    Args:
        probe_response (dict): The raw dictionary response from the RIPE Atlas probe lookup API

    Returns:
        ProbeData: The data about the probe

    Notes:
        - If an error is present in the response, a default `ProbeData` with dummy values is returned.
        - Coordinates default to `[0.0, 0.0]` if not provided.
        - Country code defaults to `"NO COUNTRY CODE"` if not found.
    """
    if probe_response.get('error'):
        return ProbeData(probe_id="-1", probe_addr=(None, None), probe_location=None)

    probe_id = probe_response.get('id', '-1')
    # print(probe_response.get('address_v4'))
    # print(probe_response.get('address_v6'))
    v4 = probe_response.get('address_v4')
    v6 = probe_response.get('address_v6')

    ipv4 = ip_address(v4) if v4 is not None else None
    if ipv4 is not None and not isinstance(ipv4, IPv4Address):
        ipv4 = None
    ipv6 = ip_address(v6) if v6 is not None else None
    if ipv6 is not None and not isinstance(ipv6, IPv6Address):
        ipv6 = None
    probe_addr: tuple[IPv4Address | None, IPv6Address | None] = (ipv4, ipv6)

    country_code = probe_response.get('country_code', "NO COUNTRY CODE")

    geometry = probe_response.get('geometry')
    coordinates = geometry.get('coordinates', [0.0, 0.0]) if geometry else [0.0, 0.0]

    probe_location = ProbeLocation(country_code=country_code,
                                   coordinates=coordinates)
    return ProbeData(probe_id=probe_id, probe_addr=probe_addr, probe_location=probe_location)


def is_failed_measurement(entry: dict[str, Any]) -> bool:
    """
    Determines if a RIPE measurement entry has failed.

    A measurement is considered failed if all result entries contain the key "x" with value "*",
    which typically indicates a failed probe response.

    Args:
        entry (dict[str, Any]): A dictionary representing a single measurement entry from the RIPE API

    Returns:
        bool: True if all entries in the result indicate failure, False otherwise.
    """
    result = entry.get("result", [])
    return all(r.get("x") == "*" for r in result)


def successful_measurement(entry: dict[str, Any]) -> int | None:
    """
    Identifies the index of the successful measurement with the lowest offset.

    A successful measurement is one that contains the "origin-ts" field,
    indicating a valid timestamp. Among all such entries, the one with the
    lowest absolute offset value is considered the most successful.

    Args:
        entry (dict[str, Any]): A dictionary representing a single measurement entry from the RIPE API

    Returns:
        int | None: The index of the result entry with the lowest offset, or None if no valid entries exist
    """
    result = entry.get("result", [])
    min_offset = float("inf")
    min_index = None

    for i, r in enumerate(result):
        if "origin-ts" in r and "offset" in r:
            try:
                offset = abs(float(r["offset"]))
                if offset < min_offset:
                    min_offset = offset
                    min_index = i
            except (ValueError, TypeError):
                continue

    return min_index


def parse_data_from_ripe_measurement(data_measurement: list[dict]) -> list[RipeMeasurement]:
    """
    Parses raw RIPE Atlas measurement data into a list of RipeMeasurement objects.

    This function:
      - Determines whether each measurement entry failed or succeeded.
      - Extracts NTP-related server and timing information.
      - Converts timestamps and metrics into structured internal representations.
      - Adds probe-specific metadata fetched from the RIPE API.

    Args:
        data_measurement (list[dict]): A list of dictionaries representing raw measurement entries from the RIPE Atlas API

    Returns:
        list[RipeMeasurement]: A list of parsed and structured RipeMeasurement objects.

    Notes:
        - Measurements that are marked as failed are still processed, but filled with default values.
        - Probe metadata is fetched using the probe ID (`prb_id`) in each measurement.
        - Timestamps are converted using `convert_float_to_precise_time`.
    """
    ripe_measurements = []
    for measurement in data_measurement:
        # check for result if ok
        failed = is_failed_measurement(measurement)
        idx = successful_measurement(measurement) if not failed else None

        from_ip = measurement.get('from')
        vantage_point_ip = ip_address(from_ip) if from_ip is not None else None
        version = measurement.get('version', -1)
        dst_addr = measurement.get('dst_addr')
        dst_name = measurement.get('dst_name')

        server_info = NtpServerInfo(
            ntp_version=version,
            ntp_server_ip=ip_address(dst_addr) if dst_addr is not None else None,
            ntp_server_name=dst_name,
            ntp_server_ref_parent_ip=None,
            ref_name=None,
            other_server_ips=None
        )

        if not failed and idx is not None:
            result = measurement['result'][idx]
            timestamps = NtpTimestamps(
                client_sent_time=convert_float_to_precise_time(result.get('origin-ts', -1.0)),
                server_recv_time=convert_float_to_precise_time(result.get('receive-ts', -1.0)),
                server_sent_time=convert_float_to_precise_time(result.get('transmit-ts', -1.0)),
                client_recv_time=convert_float_to_precise_time(result.get('final-ts', -1.0))
            )
            offset = result.get('offset', -1.0)
            delay = result.get('rtt', -1.0)
        else:
            timestamps = NtpTimestamps(*(PreciseTime(-1, 0) for _ in range(4)))
            offset = delay = -1

        stratum = measurement.get('stratum', -1)
        precision = measurement.get('precision', -1)

        main_details = NtpMainDetails(offset=offset,
                                      delay=delay,
                                      stratum=stratum,
                                      precision=precision,
                                      reachability="")

        root_delay = measurement.get('root-delay', -1.0)

        extra_details = NtpExtraDetails(root_delay=convert_float_to_precise_time(root_delay),
                                        ntp_last_sync_time=convert_float_to_precise_time(-1.0),
                                        leap=0)
        ntp_measurement = NtpMeasurement(vantage_point_ip=vantage_point_ip, server_info=server_info,
                                         timestamps=timestamps, main_details=main_details,
                                         extra_details=extra_details)

        time_to_result = measurement.get('ttr', -1.0)
        poll = measurement.get('poll', -1)

        root_dispersion = measurement.get('root-dispersion', -1.0)
        ref_id = measurement.get('ref-id', 'NO REFERENCE')
        measurement_id = measurement.get('msm_id', -1)

        ripe_measurement = RipeMeasurement(
            measurement_id=measurement_id,
            ntp_measurement=ntp_measurement,
            probe_data=parse_probe_data(get_probe_data_from_ripe_by_id(measurement['prb_id'])),
            time_to_result=time_to_result, poll=poll,
            root_dispersion=root_dispersion,
            ref_id=ref_id
        )
        ripe_measurements.append(ripe_measurement)
    #     print(ripe_measurement)
    # print(len(ripe_measurements))
    return ripe_measurements

# print(len(parse_data_from_ripe_measurement(get_data_from_ripe_measurement("105960562"))))
# print(parse_data_from_ripe_measurement(get_data_from_ripe_measurement("106323686")))
# parse_data_from_ripe_measurement(get_data_from_ripe_measurement("106125660"))
# print(parse_probe_data(get_probe_data_from_ripe_by_id("7304")))
# print(check_all_measurements_scheduled("107134561"))
