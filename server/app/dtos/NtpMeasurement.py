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

    def __post_init__(self) -> None:
        if not isinstance(self.vantage_point_ip, (IPv4Address, IPv6Address, None)):
            raise TypeError(f"vantage_point_ip must be IPv4, IPv6 or None, got {type(self.vantage_point_ip).__name__}")
        if not isinstance(self.server_info, NtpServerInfo):
            raise TypeError(f"server_info must be NtpServerInfo, got {type(self.server_info).__name__}")
        if not isinstance(self.timestamps, NtpTimestamps):
            raise TypeError(f"timestamps must be NtpTimestamps, got {type(self.timestamps).__name__}")
        if not isinstance(self.main_details, NtpMainDetails):
            raise TypeError(f"main_details must be NtpMainDetails, got {type(self.main_details).__name__}")
        if not isinstance(self.extra_details, NtpExtraDetails):
            raise TypeError(f"extra_details must be NtpExtraDetails, got {type(self.extra_details).__name__}")
