from server.app.utils.load_config_data import get_nr_of_measurements_for_jitter
from server.app.db.db_interaction import get_measurements_for_jitter_ip
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.services.NtpCalculator import NtpCalculator
from sqlalchemy.orm import Session
import ntplib
from datetime import datetime, timezone
from server.app.dtos.PreciseTime import PreciseTime
from math import radians, cos, sin, sqrt, atan2


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


def convert_float_to_precise_time(value: float) -> PreciseTime:
    """
    Converts a float value to a PreciseTime object.

    Args:
        value (float): the float value to convert

    Returns:
        a PreciseTime object
    """
    seconds = int(value)
    fraction = ntplib._to_frac(value)  # by default, a second is split into 2^32 parts
    return PreciseTime(seconds, fraction)


def human_date_to_ntp_precise_time(dt: datetime) -> PreciseTime:
    """
    Converts a UTC datetime object to a PreciseTime object in NTP time.

    Args:
        dt (datetime): A timezone-aware datetime object in UTC.

    Returns:
        PreciseTime: The corresponding NTP time.
    """
    if dt.tzinfo is None:
        raise ValueError("Input datetime must be timezone-aware (UTC)")

    unix_timestamp = dt.timestamp()
    ntp_timestamp = unix_timestamp + ntplib.NTP.NTP_DELTA

    ntp_seconds = int(ntp_timestamp)
    ntp_fraction = int((ntp_timestamp - ntp_seconds) * (2 ** 32))

    return PreciseTime(ntp_seconds, ntp_fraction)

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    It calculates the haversine distance between two points using this formula:
    d = 2 * R * asin(sqrt(a)) where R is Earth's radius in kilometers
    and 'a' is a value calculated using the latitude and longitude difference of the two points.

    Args:
        lat1 (float): The latitude of the first point.
        lon1 (float): The longitude of the first point.
        lat2 (float): The latitude of the second point.
        lon2 (float): The longitude of the second point.

    Returns:
        float: The haversine distance between the two points. (in kilometers)
    """
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    d = 2.0 * r * atan2(sqrt(a), sqrt(1 - a))
    return d