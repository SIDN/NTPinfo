from app.utils.load_config_data import get_nr_of_measurements_for_jitter
from server.app.db.connection import get_measurements_for_jitter_ip
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.services.NtpCalculator import NtpCalculator
from sqlalchemy.orm import Session
import ntplib
from datetime import datetime, timezone
from server.app.dtos.PreciseTime import PreciseTime


def calculate_jitter_from_measurements(session: Session, initial_measurement: NtpMeasurement,
                                       no_measurements: int = get_nr_of_measurements_for_jitter()) -> tuple[float, int]:
    """
    Calculates the NTP jitter based on a set of previous measurements and one initial reference measurement.

    This function computes the jitter by calculating the standard deviation of the offsets
    from a given initial measurement and a number of most recent measurements from the same NTP server

    Args:
        session (Session): The active SQLAlchemy database session
        initial_measurement (NtpMeasurement): The reference measurement not already stored in the database,
                                              used as the baseline for offset comparison
        no_measurements (int): The number of recent historical measurements to fetch from the database
                                         for jitter calculation

    Returns:
        tuple[float, int]:
            - float: The calculated jitter in seconds
            - int: The actual number of historical measurements used for the calculation
    """
    offsets = [NtpCalculator.calculate_offset(initial_measurement.timestamps)]
    last_measurements = get_measurements_for_jitter_ip(session=session,
                                                       ip=initial_measurement.server_info.ntp_server_ip,
                                                       number=(no_measurements - 1))
    nr_m = 0
    for m in last_measurements:
        if m is not None:
            offsets.append(NtpCalculator.calculate_offset(m.timestamps))
            nr_m = nr_m + 1

    return float(NtpCalculator.calculate_jitter(offsets)), nr_m

def ntp_precise_time_to_human_date(t: PreciseTime) -> str:
    """
    Converts a PreciseTime object to a human-readable time string in UTC. (ex:'2025-05-05 14:30:15.123456 UTC')
    We need to shift from ntp time to unix time so we need to subtract all the seconds from 1900 to 1970

    Args:
        t (PreciseTime): The PreciseTime object.

    Returns:
        str: the date in UTC format or empty, depending on whether the PreciseTime object could be converted to UTC.
    """
    try:
        timestamp = ntplib._to_time(t.seconds - ntplib.NTP.NTP_DELTA, t.fraction)
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f UTC")
    except Exception as e:
        print(e)
        return ""