from dataclasses import dataclass
from server.app.models import NtpServerInfo, NtpTimestamps, NtpMainDetails, NtpExtraDetails

@dataclass
class NtpMeasurement:
    server_info: NtpServerInfo
    timestamps: NtpTimestamps
    main_details: NtpMainDetails
    extra_details: NtpExtraDetails
