from dataclasses import dataclass
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.dtos.ProbeData import ProbeData


@dataclass
class RipeMeasurement:
    """
    Represents the complete set of information retrieved from a RipeMeasurement.

    Fields:
        measurement_id (int): ID of the measurement from RIPE Atlas
        ntp_measurement (NtpMeasurement): The NTP measurement data
        probe_data (ProbeData): Data related to the probe
        time_to_result (int): The duration (seconds) it took to receive the result after the measurement was initiated
        ref_id (str): The reference ID of the server
    """
    measurement_id: int
    ntp_measurement: NtpMeasurement
    probe_data: ProbeData
    time_to_result: float
    ref_id: str
