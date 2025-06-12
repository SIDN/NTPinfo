from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address


@dataclass
class NtpServerInfo:
    """
    Represents the relevant metadata of an NTP server.

    Fields:
        ntp_version (int): The version of NTP the user chose to use (backwards compatible)
        ntp_server_ip (IPv4Address | IPv6Address | None): The IP of the server, either in IPv4 or IPv6 format
        ntp_server_name (str): The name of the server
        ntp_server_ref_parent_ip (None | IPv4Address | IPv6Address): The IP of the parent server (it is None if it is a root server)
        ref_name (str): The name of the parent (reference) server or None if we can only get the IP
    """
    ntp_version: int
    ntp_server_ip: IPv4Address | IPv6Address | None
    ntp_server_name: str | None
    ntp_server_ref_parent_ip: IPv4Address | IPv6Address | None
    ref_name: None | str

    def __post_init__(self) -> None:
        if not isinstance(self.ntp_server_ip, IPv4Address | IPv6Address | None):
            raise TypeError(f"ntp_server_ip must be IPv4 or IPv6Address, got {type(self.ntp_server_ip).__name__}")
        if not isinstance(self.ntp_server_name, str):
            raise TypeError(f"ntp_server_name must be str, got {type(self.ntp_server_name).__name__}")
        if not isinstance(self.ntp_version, int):
            raise TypeError(f"ntp_version must be int, got {type(self.ntp_version).__name__}")
        if not isinstance(self.ntp_server_ref_parent_ip, IPv4Address | IPv6Address | None):
            raise TypeError(f"ntp_server_ref_parent_ip must be IPv4Address or IPv6Address, got {type(self.ntp_server_ref_parent_ip).__name__}")
        if not isinstance(self.ref_name, str | None):
            raise TypeError(f"ref_name must be str, got {type(self.ref_name).__name__}")

