from pydantic import BaseModel, Field, model_validator
from typing import Optional


class MeasurementRequest(BaseModel):
    """
    Data model for an NTP measurement request.

    Attributes:
        server (str): The IP address or domain name of the NTP server to be measured.
    """
    server: str
