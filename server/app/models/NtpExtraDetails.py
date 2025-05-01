from dataclasses import dataclass
from server.app.models.PreciseTime import PreciseTime

@dataclass
class NtpExtraDetails:
    root_delay: PreciseTime
    ntp_last_sync_time: PreciseTime
    leap: int