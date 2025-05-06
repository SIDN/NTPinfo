from dataclasses import dataclass
from app.models.NtpExtraDetails import NtpExtraDetails
from app.models.NtpServerInfo import NtpServerInfo
from app.models.NtpMainDetails import NtpMainDetails
from app.models.NtpTimestamps import NtpTimestamps

@dataclass
class NtpMeasurement:
    """
    Represents the complete set of measurements for a given NTP server.

    Fields:
        server_info (NtpServerInfo): Metadata about the NTP server 
        timestamps (NtpTimestamps): NTP timestamps from the exchange
        main_details (NtpMainDetails): Key metrics 
        extra_details (NtpExtraDetails): Additional fields
    """
    server_info: NtpServerInfo
    timestamps: NtpTimestamps
    main_details: NtpMainDetails
    extra_details: NtpExtraDetails
