from dataclasses import dataclass

@dataclass
class PreciseTime:
    """
    Represents a single NTP timestamp.

    Fields:
        seconds (int): The integer part of the timestamp (the first 32 bits).
        fraction (int): The fractional part of the timestamp (the last 32 bits).
    """
    seconds:int
    fraction:int

    def calculate_float_time(self)->float:
        #seconds+fraction/2^32
        return self.seconds+self.fraction/2**32