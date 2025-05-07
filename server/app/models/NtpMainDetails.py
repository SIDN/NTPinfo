from dataclasses import dataclass

@dataclass
class NtpMainDetails:
    """
    Represents the main measurements reported by an NTP server.
    
    Fields:
        offset (float): Clock offset between the client and server, in seconds
        delay (float): Round-trip delay for NTP packet exchange, in seconds
        stratum (int): Stratum level of the serve
        precision (float): Precision of the system clock of the server 
        reachability (str): Reachability register
    """
    offset: float 
    delay: float
    stratum: int
    precision: float
    reachability: str