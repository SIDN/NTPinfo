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
        if self.seconds < 0 or self.fraction < 0:
            raise ValueError("seconds and fraction must be positive")
        if not isinstance(self.seconds, int):
            raise TypeError(f"seconds must be an integer, got {type(self.seconds).__name__}")
        if not isinstance(self.fraction, int):
            raise TypeError(f"fraction must be an integer, got {type(self.fraction).__name__}")
