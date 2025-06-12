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

    def __post_init__(self) -> None:
        if not isinstance(self.measurement_id, int):
            raise TypeError(f"measurement_id must be int, got {type(self.measurement_id).__name__}")
        if not isinstance(self.ntp_measurement, NtpMeasurement):
            raise TypeError(f"ntp_measurement must be NtpMeasurement, got {type(self.ntp_measurement).__name__}")
        if not isinstance(self.probe_data, ProbeData):
            raise TypeError(f"probe_data must be ProbeData, got {type(self.probe_data).__name__}")
        if not isinstance(self.time_to_result, (float, int)):
            raise TypeError(f"time_to_result must be float or int, got {type(self.time_to_result).__name__}")
        if not isinstance(self.ref_id, str):
            raise TypeError(f"ref_id must be str, got {type(self.ref_id).__name__}")

