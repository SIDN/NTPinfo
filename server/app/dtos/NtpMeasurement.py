from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address

from server.app.dtos.NtpExtraDetails import NtpExtraDetails
from server.app.dtos.NtpServerInfo import NtpServerInfo
from server.app.dtos.NtpMainDetails import NtpMainDetails
from server.app.dtos.NtpTimestamps import NtpTimestamps


@dataclass
class NtpMeasurement:
    """
    Represents the complete set of measurements for a given NTP server.

    Fields:
        vantage_point_ip (IPv4Address | IPv6Address | None): IP address of the vantage point where measurement is being triggered
        server_info (NtpServerInfo): Metadata about the NTP server 
        timestamps (NtpTimestamps): NTP timestamps from the exchange
        main_details (NtpMainDetails): Key metrics 
        extra_details (NtpExtraDetails): Additional fields
    """
    vantage_point_ip: IPv4Address | IPv6Address | None
    server_info: NtpServerInfo
    timestamps: NtpTimestamps
    main_details: NtpMainDetails
    extra_details: NtpExtraDetails
