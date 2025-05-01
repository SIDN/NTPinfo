from dataclasses import dataclass
from server.app.models.PreciseTime import PreciseTime

@dataclass
class NtpExtraDetails:
    root_delay: PreciseTime
    ntp_last_sync_time: PreciseTime
    leap: int

    #according to ntp, leap has only 2 bits and if it's value is 3 then it is invalid
    def is_valid(self) -> bool:
        if self.leap==3:
            return False
        return True