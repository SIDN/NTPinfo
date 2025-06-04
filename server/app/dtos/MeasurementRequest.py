from pydantic import BaseModel, Field, model_validator
from typing import Optional


class MeasurementRequest(BaseModel):
    """
    Data model for an NTP measurement request.

    Attributes:
        server (str): The IP address or domain name of the NTP server to be measured.
        random_probes (bool): Whether the user wants to have random probes around the world (default : selected around their location)
    """
    server: str
    random_probes: bool
