from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime
class NtpCalculator:

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def calculate_offset(timestamps: NtpTimestamps) -> float:
        """
        Calculates the clock offset between client and server using NTP timestamps.
        Uses the formula  ((t2 - t1) + (t3 - t4)) / 2
        
        args:
        timestamps (NtpTimestamps): A single NTP timestamps object, containing data about the 4 key timestamps
 
        returns:
            float: Clock offset in seconds
        """
        # a = t2 - t1
        a = PreciseTime(
            timestamps.server_recv_time.seconds - timestamps.client_sent_time.seconds,
            timestamps.server_recv_time.fraction - timestamps.client_sent_time.fraction
        )
        #b = t3 - t4
        b = PreciseTime(
            timestamps.server_sent_time.seconds - timestamps.client_recv_time.seconds,
            timestamps.server_sent_time.fraction - timestamps.client_recv_time.fraction
        )
        
        offset_seconds: float = (a.seconds + b.seconds) / 2.0
        offset_fraction: float = (a.fraction + b.fraction) / 2.0
        return offset_seconds + offset_fraction / (2 ** 32)
    
    @staticmethod
    def calculate_delay(timestamps: NtpTimestamps) -> float:
        """
         Calculates round-trip delay between client and server using NTP timestamps.

        Args:
            timestamps (NtpTimestamps): A single NTP timestamps object, containing data about the 4 key timestamps

        Returns:
            float: Delay in seconds
        """
        a = PreciseTime(
            timestamps.client_recv_time.seconds - timestamps.client_sent_time.seconds,
            timestamps.client_recv_time.fraction - timestamps.client_sent_time.fraction
        )
        b = PreciseTime(
            timestamps.server_sent_time.seconds - timestamps.server_recv_time.seconds,
            timestamps.server_sent_time.fraction - timestamps.server_recv_time.fraction
        )
        ans: float = (a.seconds - b.seconds) + (b.fraction - a.fraction) / (2 ** 32)
        return ans
    
    @staticmethod
    def calculate_float_time(time: PreciseTime) -> float:
        """
        Converts a PreciseTime object to a float in seconds.

        Args:
            time (PreciseTime): A single PreciseTime object, representing a single timestamp

        Returns:
            float: Time in seconds
        """
        ans: float = time.seconds + time.fraction / (2 ** 32)
        return ans