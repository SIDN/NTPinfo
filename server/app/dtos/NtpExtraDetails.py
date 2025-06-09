from dataclasses import dataclass
from server.app.dtos.PreciseTime import PreciseTime


@dataclass
class NtpExtraDetails:
    """
    Represents additional measurements for a given NTP server. 

    Fields:
        root_delay (PreciseTime): Total round-trip delay to the primary reference source
        poll (int): The poll interval (seconds) used by the probe during the measurement
        root_dispersion (PreciseTime): An estimate (seconds) of the maximum error due to clock frequency stability
        ntp_last_sync_time (PreciseTime): Last time the server was synchronized
        leap (int): 2-bit leap indicator; A value of 3 (11 in binary) represents an unsynchronized clock
    """
    root_delay: PreciseTime
    poll: int
    root_dispersion: PreciseTime
    ntp_last_sync_time: PreciseTime
    leap: int
