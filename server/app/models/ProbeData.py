from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import Tuple


@dataclass
class ProbeLocation:
    country_code: str
    coordinates: Tuple[float, float]


@dataclass
class ProbeData:
    probe_id: str
    probe_addr: Tuple[IPv4Address, IPv6Address]
    probe_location: ProbeLocation
