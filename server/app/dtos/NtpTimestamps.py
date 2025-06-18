from dataclasses import dataclass
from server.app.dtos.PreciseTime import PreciseTime


@dataclass
class NtpTimestamps:
    """
    The four key timestamps used in NTP (Network Time Protocol) exchange
    between a client and a server

    Attributes:
        client_sent_time (PreciseTime): Time when the request was sent by the client (t1)
        server_recv_time (PreciseTime): Time when the request was received by the server (t2)
        server_sent_time (PreciseTime): Time when the response was sent by the server (t3)
        client_recv_time (PreciseTime): Time when the response was received by the client (t4)
    """
    client_sent_time: PreciseTime  # t1 Time at the client when the request departed for the server.
    server_recv_time: PreciseTime  # t2 Time at the server when the request arrived from the client.
    server_sent_time: PreciseTime  # t3 Time at the server when the response was transmitted to the client.
    client_recv_time: PreciseTime  # t4 Time at the client when the reply arrived from the server.

    def __post_init__(self) -> None:
        if not isinstance(self.client_sent_time, PreciseTime):
            raise TypeError(f"client_sent_time must be a PreciseTime, got {type(self.client_sent_time).__name__}")
        if not isinstance(self.server_recv_time, PreciseTime):
            raise TypeError(f"server_recv_time must be a PreciseTime, got {type(self.server_recv_time).__name__}")
        if not isinstance(self.server_sent_time, PreciseTime):
            raise TypeError(f"server_sent_time must be a PreciseTime, got {type(self.server_sent_time).__name__}")
        if not isinstance(self.client_recv_time, PreciseTime):
            raise TypeError(f"client_recv_time must be a PreciseTime, got {type(self.client_recv_time).__name__}")
