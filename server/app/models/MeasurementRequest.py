from pydantic import BaseModel, Field, model_validator
from typing import Optional

class MeasurementRequest(BaseModel):
    """
    Data model for an NTP measurement request.

    Attributes:
        server (str): The IP address or domain name of the NTP server to be measured.
        jitter_flag (bool): Whether the user wants to perform multiple measurements and get the jitter back.
        measurements_no (int): The number of measurements requested (should be at most 10).
    """
    server: str
    jitter_flag: bool
    measurements_no: Optional[int] = Field(default=None, le=10)

    @model_validator(mode="after")
    def check_measurements(self) -> 'MeasurementRequest':
        """
        Function that validates interaction between jitter_flag and measurements_no.
        If jitter_flag is set to True, measurements_no must be provided, otherwise it can be ignored.

        Returns:
            MeasurementRequest: The validated model instance.

        Raises:
            ValueError: If jitter_flag is True but measurements_no is not provided.
        """
        if self.jitter_flag:
            if self.measurements_no is None:
                raise ValueError("measurements_no is required when jitter_flag is True.")
        else:
            self.measurements_no = 0
        return self
