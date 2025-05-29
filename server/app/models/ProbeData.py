from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import Tuple


@dataclass
class ProbeLocation:
    """
    Represents the geographical location of a RIPE Atlas probe.

    Attributes:
        country_code (str): Two-letter ISO 3166-1 alpha-2 country code (e.g., 'US', 'DE') indicating
            the country where the probe is located
        coordinates (Tuple[float, float]): The latitude and longitude of the probe's physical location
    """
    country_code: str
    coordinates: Tuple[float, float]


@dataclass
class ProbeData:
    """
    Contains identifying and location information about a RIPE Atlas probe.

    Attributes:
        probe_id (str): The unique identifier of the probe
        probe_addr (Tuple[IPv4Address, IPv6Address] | None): The IPv4 and IPv6 addresses of the probe
        probe_location (ProbeLocation | None): Geographic location of the probe
    """
    probe_id: str
    probe_addr: Tuple[IPv4Address, IPv6Address] | None
    probe_location: ProbeLocation | None
