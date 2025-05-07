from ipaddress import IPv4Address, IPv6Address

from fastapi import FastAPI, HTTPException
from server.app.main import measure
from server.app.main import fetch_historic_data_with_timestamps
from server.app.models.NtpMeasurement import NtpMeasurement
from datetime import datetime, timezone


def get_format(measurement: NtpMeasurement):
    return {
        "ntp_version": measurement.server_info.ntp_version,
        "ntp_server_ip": measurement.server_info.ntp_server_ip,
        "ntp_server_name": measurement.server_info.ntp_server_name,
        "ntp_server_ref_parent_ip": measurement.server_info.ntp_server_ref_parent_ip,
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


"""
API endpoint
args:
    time (PreciseTime): A single PreciseTime object, representing a single timestamp

returns:
    float: Time in seconds
"""


@app.post("/measurements/")
async def read_data_measurement(server: str):
    # the case in which none of them are mentioned
    if len(server) == 0:
        raise HTTPException(status_code=400, detail="Either 'ip' or 'dn' must be provided")
    result = measure(server)
    if result != None:
        return {
            "measurement": get_format(result)
        }
    return {
        "Error": "Could not perform measurement, dns or ip not reachable."
    }


@app.get("/measurements/history/")
async def read_historic_data_time(server: str,
                                  start: datetime = None, end: datetime = None):
    if len(server) == 0:
        raise HTTPException(status_code=400, detail="Either 'ip' or 'domain name' must be provided")

    utc_time_from_9am = datetime(2025, 5, 7, 7, 0, tzinfo=timezone.utc)
    current_utc_time = datetime(2025, 5, 7, 11, 15, tzinfo=timezone.utc)

    start_test = utc_time_from_9am
    end_test = current_utc_time

    result = fetch_historic_data_with_timestamps(server, start, end)
    formatted_results = [get_format(entry) for entry in result]
    return {
        "measurements": formatted_results
    }
