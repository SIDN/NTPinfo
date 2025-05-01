from dataclasses import dataclass
from server.app.models.PreciseTime import PreciseTime

@dataclass
class NtpTimestamp:
    client_sent_time: PreciseTime
    server_recv_time: PreciseTime
    server_sent_time: PreciseTime
    client_recv_time: PreciseTime