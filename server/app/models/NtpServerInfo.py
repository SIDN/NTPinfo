from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address

@dataclass
class NtpServerInfo:
    ntp_version: int
    ntp_server_ip: IPv4Address | IPv6Address
    ntp_server_name: str
    ntp_server_ref_parent_ip: IPv4Address | IPv6Address
    ref_name: str