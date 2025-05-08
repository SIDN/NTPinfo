from dataclasses import dataclass
from server.app.models.PreciseTime import PreciseTime


@dataclass
class NtpTimestamps:
    """
    The four key timestamps used in NTP (Network Time Protocol) exchange
    between a client and a server

    Fields:
        client_sent_time (PreciseTime): Time when the request was sent by the client (t1)
        server_recv_time (PreciseTime): Time when the request was received by the server (t2)
        server_sent_time (PreciseTime): Time when the response was sent by the server (t3)
        client_recv_time (PreciseTime): Time when the response was received by the client (t4)
    """
    client_sent_time: PreciseTime  # t1
    server_recv_time: PreciseTime  # t2
    server_sent_time: PreciseTime  # t3
    client_recv_time: PreciseTime  # t4
