from server.app.db.connection import get_measurements_for_jitter_ip
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.services.NtpCalculator import NtpCalculator
from sqlalchemy.orm import Session


def calculate_jitter_from_measurements(session: Session, initial_measurement: NtpMeasurement,
                                       no_measurements: int = 7) -> (float, int):
    """
    Calculates the NTP jitter based on a set of previous measurements and one initial reference measurement.

    This function computes the jitter by calculating the standard deviation of the offsets
    from a given initial measurement and a number of most recent measurements from the same NTP server

    Args:
        session (Session): The active SQLAlchemy database session
        initial_measurement (NtpMeasurement): The reference measurement not already stored in the database,
                                              used as the baseline for offset comparison
        no_measurements (int, optional): The number of recent historical measurements to fetch from the database
                                         for jitter calculation (default: 7)

    Returns:
        tuple[float, int]:
            - float: The calculated jitter in seconds
            - int: The actual number of historical measurements used for the calculation
    """
    offsets = [NtpCalculator.calculate_offset(initial_measurement.timestamps)]
    last_measurements = get_measurements_for_jitter_ip(session=session,
                                                       ip=initial_measurement.server_info.ntp_server_ip,
                                                       number=no_measurements)
    for m in last_measurements:
        offsets.append(NtpCalculator.calculate_offset(m.timestamps))
    return float(NtpCalculator.calculate_jitter(offsets)), len(last_measurements) + 1
