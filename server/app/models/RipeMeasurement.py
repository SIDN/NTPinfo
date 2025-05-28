from dataclasses import dataclass
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.ProbeData import ProbeData


@dataclass
class RipeMeasurement:
    """
    Represents the complete set of measurements for a given NTP server.

    Fields:
        vantage_point_ip (IPv4Address | IPv6Address): IP address of the vantage point where measurement happens
        server_info (NtpServerInfo): Metadata about the NTP server
        timestamps (NtpTimestamps): NTP timestamps from the exchange
        main_details (NtpMainDetails): Key metrics
        extra_details (NtpExtraDetails): Additional fields
    """
    ntp_measurement: NtpMeasurement
    probe_data: ProbeData
    time_to_result: float
