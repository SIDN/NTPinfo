from dataclasses import dataclass

@dataclass
class PreciseTime:
    """
    Represents a single NTP timestamp.

    Fields:
        seconds (int): The integer part of the timestamp (the first 32 bits).
        fraction (int): The fractional part of the timestamp (the last 32 bits).
    """
    seconds: int
    fraction: int

    def __post_init__(self) -> None:
        if int(self.seconds) != self.seconds or int(self.fraction) != self.fraction:
            raise ValueError("Invalid seconds and fraction values")
        if not isinstance(self.seconds, int | float):
            raise TypeError(f"seconds must be an integer, got {type(self.seconds).__name__}")
        if not isinstance(self.fraction, int | float):
            raise TypeError(f"fraction must be an integer, got {type(self.fraction).__name__}")
