class InputError(Exception):
    """
    Exception raised when an input error occurs. For example when the input parameters of a method are invalid.
    """

    def __init__(self, message: str = "Invalid input provided") -> None:
        """
        Initialize the exception object.
        """
        self.message = message
        super().__init__(self.message)


class RipeMeasurementError(Exception):
    """
    Exception raised when a ripe measurement failed. For example when our server sends a bad request to RIPE Atlas.
    """

    def __init__(self, message: str = "Ripe measurement failed") -> None:
        """
        Initialize the exception object.
        """
        self.message = message
        super().__init__(self.message)


class DNSError(Exception):
    """
    Exception raised when a DNS error occurs. For example when converting a domain name to IP addresses fails.
    """

    def __init__(self, message: str = "DNS error (domain name invalid)") -> None:
        """
        Initialize the exception object.
        """
        self.message = message
        super().__init__(self.message)


class InvalidMeasurementDataError(Exception):
    """
    Raised when input data is invalid or incomplete for NtpMeasurement.
    """

    def __init__(self, message: str = "Invalid measurement data provided") -> None:
        self.message = message
        super().__init__(self.message)


class DatabaseInsertError(Exception):
    """
    Raised when a measurement fails to insert into the database.
    """

    def __init__(self, message: str = "Failed to insert measurement into database") -> None:
        self.message = message
        super().__init__(self.message)


class MeasurementQueryError(Exception):
    """
    Raised when querying the database for measurements fails.
    """

    def __init__(self, message: str = "Failed to query measurement data") -> None:
        self.message = message
        super().__init__(self.message)
