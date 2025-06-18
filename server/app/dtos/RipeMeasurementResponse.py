from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional, Union, Dict
from pydantic import BaseModel

from server.app.dtos.PreciseTime import PreciseTime
from server.app.dtos.ProbeData import ServerLocation


class ProbeAddr(BaseModel):
    ipv4: Optional[IPv4Address]
    ipv6: Optional[IPv6Address]


class ProbeCountPerType(BaseModel):
    asn: Optional[int]
    prefix: Optional[str]
    country: Optional[str]
    area: Optional[str]
    random: Optional[int]


class RipeMeasurementResult(BaseModel):
    client_sent_time: PreciseTime
    server_recv_time: PreciseTime
    server_sent_time: PreciseTime
    client_recv_time: PreciseTime
    rtt: float
    offset: float


class RipeResult(BaseModel):
    ntp_version: int
    ripe_measurement_id: int
    vantage_point_ip: Optional[Union[IPv4Address, IPv6Address]]
    ntp_server_ip: Optional[Union[IPv4Address, IPv6Address]]
    ntp_server_name: Optional[str]
    ntp_server_location: ServerLocation
    probe_addr: ProbeAddr
    probe_id: Union[int, str]
    probe_location: ServerLocation
    time_to_result: float
    stratum: int
    poll: int
    precision: float
    root_delay: float
    root_dispersion: float
    ref_id: str
    probe_count_per_type: ProbeCountPerType
    result: List[RipeMeasurementResult]


class RipeMeasurementResponse(BaseModel):
    measurements: List[RipeResult]
