from dataclasses import dataclass


@dataclass
class NtpMainDetails:
    """
    Represents the main measurements reported by an NTP server.
    
    Fields:
        offset (float): Clock offset between the client and server, in seconds
        rtt (float): Round-trip delay for NTP packet exchange, in seconds
        stratum (int): Stratum level of the serve
        precision (float): Precision of the system clock of the server 
        reachability (str): Reachability register
    """
    offset: float
    rtt: float
    stratum: int
    precision: float
    reachability: str

    def __post_init__(self) -> None:
        if not isinstance(self.offset, (float, int)):
            raise TypeError(f"offset must be float or int, got {type(self.offset).__name__}")
        if not isinstance(self.rtt, (float, int)):
            raise TypeError(f"rtt must be float or int, got {type(self.rtt).__name__}")
        if not isinstance(self.stratum, int):
            raise TypeError(f"stratum must be int, got {type(self.stratum).__name__}")
        if not isinstance(self.precision, (float, int)):
            raise TypeError(f"precision must be float or int, got {type(self.precision).__name__}")
        if not isinstance(self.reachability, str):
            raise TypeError(f"reachability must be str, got {type(self.reachability).__name__}")
