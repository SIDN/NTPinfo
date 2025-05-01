from dataclasses import dataclass

@dataclass
class PreciseTime:
    seconds:int
    fraction:int

    def calculate_float_time(self)->float:
        #seconds+fraction/2^32
        return self.seconds+self.fraction/2**32