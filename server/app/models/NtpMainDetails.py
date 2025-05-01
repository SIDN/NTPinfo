from dataclasses import dataclass

@dataclass
class NtpMainDetails:
    offset: float #this is what ntplib use
    delay: float
    stratum: int
    precision: float
    reachability: str