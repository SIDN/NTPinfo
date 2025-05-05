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
    client_sent_time: PreciseTime #t1
    server_recv_time: PreciseTime #t2
    server_sent_time: PreciseTime #t3
    client_recv_time: PreciseTime #t4
    
    def calculate_offset(self)->float:
        # ((t2-t1)+(t3-t4))/2=(a+b)/2
        a=PreciseTime(self.server_recv_time.seconds - self.client_sent_time.seconds,
                      self.server_recv_time.fraction - self.client_sent_time.fraction)
        b=PreciseTime(self.server_sent_time.seconds - self.client_recv_time.seconds,
                      self.server_sent_time.fraction - self.client_recv_time.fraction)

        offset_seconds=(a.seconds + b.seconds)/2.0
        offset_fraction=(a.fraction + b.fraction)/2.0

        return offset_seconds+offset_fraction/(2**32)

    def calculate_delay(self)->float:
        # (t4-t1)-(t3-t2)=a-b
        a=PreciseTime(self.client_recv_time.seconds - self.client_sent_time.seconds,
                        self.client_recv_time.fraction - self.client_sent_time.fraction)
        b=PreciseTime(self.server_sent_time.seconds - self.server_recv_time.seconds,
                        self.server_sent_time.fraction - self.server_recv_time.fraction)

        return (a.seconds - b.seconds) + (b.fraction - a.fraction)/(2**32)