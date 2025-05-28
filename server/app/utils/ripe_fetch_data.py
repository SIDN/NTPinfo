import requests
import os
from dotenv import load_dotenv

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
    probe_id = probe_response['id']
    probe_addr = probe_response['address_v4'], probe_response['address_v6']
    probe_location = ProbeLocation(country_code=probe_response['country_code'],
                                   coordinates=probe_response['geometry']['coordinates'])
    return ProbeData(probe_id=probe_id, probe_addr=probe_addr, probe_location=probe_location)


def parse_data_from_ripe_measurement(data_measurement: list[dict]) -> list[RipeMeasurement]:
    ripe_measurements = []
    for measurement in data_measurement:
        # check for result if ok
        vantage_point_ip = measurement['from']
        server_info = NtpServerInfo(ntp_version=measurement['version'], ntp_server_ip=measurement['dst_addr'],
                                    ntp_server_name=measurement['dst_name'], ntp_server_ref_parent_ip=None,
                                    ref_name=None, other_server_ips=None)

        timestamps = NtpTimestamps(
            client_sent_time=convert_float_to_precise_time(measurement['result'][0]['origin-ts']),
            server_recv_time=convert_float_to_precise_time(measurement['result'][0]['receive-ts']),
            server_sent_time=convert_float_to_precise_time(measurement['result'][0]['transmit-ts']),
            client_recv_time=convert_float_to_precise_time(measurement['result'][0]['final-ts']))
        main_details = NtpMainDetails(offset=measurement['result'][0]['offset'],
                                      delay=measurement['result'][0]['rtt'],
                                      stratum=measurement['stratum'],
                                      precision=measurement['precision'],
                                      reachability="")
        extra_details = NtpExtraDetails(root_delay=convert_float_to_precise_time(measurement['root-delay']),
                                        ntp_last_sync_time=convert_float_to_precise_time(0.0),
                                        leap=0)
        ntp_measurement = NtpMeasurement(vantage_point_ip=vantage_point_ip, server_info=server_info,
                                         timestamps=timestamps, main_details=main_details, extra_details=extra_details)

        ripe_measurement = RipeMeasurement(ntp_measurement=ntp_measurement,
                                           probe_data=parse_probe_data(
                                               get_probe_data_from_ripe_by_id(measurement['prb_id'])),
                                           time_to_result=measurement['ttr'])
        ripe_measurements.append(ripe_measurement)
        print(ripe_measurement)
    return ripe_measurements


parse_data_from_ripe_measurement(get_data_from_ripe_measurement("105960562"))
# print(parse_probe_data(get_probe_data_from_ripe_by_id("7304")))
