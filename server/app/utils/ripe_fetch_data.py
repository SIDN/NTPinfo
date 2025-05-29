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

load_dotenv()


def get_data_from_ripe_measurement(measurement_id: str) -> list[dict]:
    url = f"https://atlas.ripe.net/api/v2/measurements/{measurement_id}/results/"

    headers = {
        "Authorization": f"Key {os.getenv('RIPE_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
    return response.json()


def get_probe_data_from_ripe_by_id(probe_id: str) -> dict:
    url = f"https://atlas.ripe.net/api/v2/probes/{probe_id}/"

    headers = {
        "Authorization": f"Key {os.getenv('RIPE_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    # print("Status Code:", response.status_code)
    # print("Response JSON:", response.json())
    return response.json()


def parse_probe_data(probe_response: dict) -> ProbeData:
    if probe_response.get('error'):
        return ProbeData(probe_id="-1", probe_addr=None, probe_location=None)

    probe_id = probe_response.get('id', '-1')
    if probe_response.get('address_v4') is not None or probe_response.get('address_v6') is not None:
        probe_addr = probe_response['address_v4'], probe_response['address_v6']
    else:
        probe_addr = None

    country_code = probe_response.get('country_code', "NO COUNTRY CODE")

    coordinates = probe_response.get('geometry').get('coordinates', [0.0, 0.0])

    probe_location = ProbeLocation(country_code=country_code,
                                   coordinates=coordinates)
    return ProbeData(probe_id=probe_id, probe_addr=probe_addr, probe_location=probe_location)


def is_failed_measurement(entry) -> bool:
    result = entry.get("result", [])
    return all(r.get("x") == "*" for r in result)


def successful_measurement(entry) -> int | None:
    result = entry.get("result", [])
    for i, r in enumerate(result):
        if "origin-ts" in r:
            return i
    return None


def parse_data_from_ripe_measurement(data_measurement: list[dict]) -> list[RipeMeasurement]:
    ripe_measurements = []
    for measurement in data_measurement:
        # check for result if ok
        failed = is_failed_measurement(measurement)
        idx = successful_measurement(measurement) if not failed else None

        vantage_point_ip = measurement.get('from')
        version = measurement.get('version', 0)
        dst_addr = measurement.get('dst_addr')
        dst_name = measurement.get('dst_name')

        server_info = NtpServerInfo(
            ntp_version=version,
            ntp_server_ip=dst_addr,
            ntp_server_name=dst_name,
            ntp_server_ref_parent_ip=None,
            ref_name=None,
            other_server_ips=None
        )

        if not failed and idx is not None:
            result = measurement['result'][idx]
            timestamps = NtpTimestamps(
                client_sent_time=convert_float_to_precise_time(result.get('origin-ts', 0.0)),
                server_recv_time=convert_float_to_precise_time(result.get('receive-ts', 0.0)),
                server_sent_time=convert_float_to_precise_time(result.get('transmit-ts', 0.0)),
                client_recv_time=convert_float_to_precise_time(result.get('final-ts', 0.0))
            )
            offset = result.get('offset', 0)
            delay = result.get('rtt', 0)
        else:
            timestamps = NtpTimestamps(*(PreciseTime(0, 0) for _ in range(4)))
            offset = delay = 0

        stratum = measurement.get('stratum', 0)
        precision = measurement.get('precision', 0)

        main_details = NtpMainDetails(offset=offset,
                                      delay=delay,
                                      stratum=stratum,
                                      precision=precision,
                                      reachability="")

        root_delay = measurement.get('root-delay', 0.0)

        extra_details = NtpExtraDetails(root_delay=convert_float_to_precise_time(root_delay),
                                        ntp_last_sync_time=convert_float_to_precise_time(0.0),
                                        leap=0)
        ntp_measurement = NtpMeasurement(vantage_point_ip=vantage_point_ip, server_info=server_info,
                                         timestamps=timestamps, main_details=main_details,
                                         extra_details=extra_details)

        time_to_result = measurement.get('ttr', 0.0)
        poll = measurement.get('poll', 0)

        root_dispersion = measurement.get('root-dispersion', 0.0)
        ref_id = measurement.get('ref-id', '0')
        measurement_id = measurement.get('msm_id', 0)

        ripe_measurement = RipeMeasurement(
            measurement_id=measurement_id,
            ntp_measurement=ntp_measurement,
            probe_data=parse_probe_data(get_probe_data_from_ripe_by_id(measurement['prb_id'])),
            time_to_result=time_to_result, poll=poll,
            root_dispersion=root_dispersion,
            ref_id=ref_id
        )
        ripe_measurements.append(ripe_measurement)
        print(ripe_measurement)
    print(len(ripe_measurements))
    return ripe_measurements

# parse_data_from_ripe_measurement(get_data_from_ripe_measurement("105960562"))
# parse_data_from_ripe_measurement(get_data_from_ripe_measurement("106323686"))
# parse_data_from_ripe_measurement(get_data_from_ripe_measurement("106125660"))
# print(parse_probe_data(get_probe_data_from_ripe_by_id("7304")))
