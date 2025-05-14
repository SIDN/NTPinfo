from pydantic import BaseModel


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
    measurements_no: int
