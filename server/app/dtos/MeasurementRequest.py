from pydantic import BaseModel, Field, model_validator
from typing import Self


class MeasurementRequest(BaseModel):
    """
    Data model for an NTP measurement request.

    Attributes:
        server (str): The IP address or domain name of the NTP server to be measured.
    """
    server: str

    @model_validator(mode='after')
    def validate_after(self) -> Self:
        """
        Checks that the server is a string.
        Args:
            self (Self): Instance of the class.
        Returns:
            Self: the MeasurementRequest instance.

        Raises:
            TypeError: if the server is not a string.

        """
        if not isinstance(self.server, str):
            raise TypeError(f"server must be str, got {type(self.server).__name__}")
        return self
