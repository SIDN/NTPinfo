from dataclasses import dataclass
from server.app.models.PreciseTime import PreciseTime

@dataclass
class NtpTimestamp:
    client_sent_time: PreciseTime #t1
    server_recv_time: PreciseTime #t2
    server_sent_time: PreciseTime #t3
    client_recv_time: PreciseTime #t4

    def calculate_offset(self)->float:
        # ((t2-t1)+(t3-t4))/2=(a+b)/2
        a=PreciseTime(self.server_recv_time.seconds-self.client_sent_time.seconds,
                      self.server_recv_time.fraction-self.client_sent_time.fraction)
        b=PreciseTime(self.server_sent_time.seconds-self.client_recv_time.seconds,
                      self.server_sent_time.fraction-self.client_recv_time.fraction)

        offset_seconds=(a.seconds+b.seconds)/2.0
        offset_fraction=(a.fraction+b.fraction)/2.0
        
        offset:float=offset_seconds+offset_fraction/(2**32)
        return offset