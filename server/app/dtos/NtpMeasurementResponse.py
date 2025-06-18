from ipaddress import IPv4Address, IPv6Address

from pydantic import BaseModel
from typing import List, Optional, Union

from server.app.dtos.PreciseTime import PreciseTime
from server.app.dtos.ProbeData import ServerLocation
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.dtos.NtpMainDetails import NtpMainDetails


class MeasurementResult(BaseModel):
    ntp_version: int
    vantage_point_ip: Optional[Union[IPv4Address, IPv6Address]]
    ntp_server_ip: Optional[Union[IPv4Address, IPv6Address]]
    ntp_server_name: Optional[str]
    ntp_server_location: ServerLocation
    ntp_server_ref_parent_ip: Optional[Union[IPv4Address, IPv6Address]]
    ref_name: Optional[str]
    client_sent_time: PreciseTime
    server_recv_time: PreciseTime
    server_sent_time: PreciseTime
    client_recv_time: PreciseTime
    offset: float
    rtt: float
    stratum: int
    precision: float
    reachability: str
    root_delay: PreciseTime
    poll: int
    root_dispersion: PreciseTime
    ntp_last_sync_time: PreciseTime
    leap: int
    jitter: float
    nr_measurements_jitter: int


class MeasurementResponse(BaseModel):
    measurements: List[MeasurementResult]
