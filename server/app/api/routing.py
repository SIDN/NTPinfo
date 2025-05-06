from ipaddress import IPv4Address, IPv6Address

from fastapi import FastAPI, HTTPException
from app.main import measure
from app.models.NtpMeasurement import NtpMeasurement


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
    return {"Hello": "Worlds"}


@app.post("/measurements/")
async def read_item(ip: IPv4Address | IPv6Address = None, dn: str = None):
    # the case in which none of them are mentioned
    if ip == None and dn is None:
        raise HTTPException(status_code=400, detail="Either 'ip' or 'dn' must be provided")
    result = measure(ip, dn)
    return {
        "measurement": get_format(result)
    }
