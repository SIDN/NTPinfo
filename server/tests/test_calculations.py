from ipaddress import IPv4Address
from unittest.mock import patch, MagicMock

from server.app.dtos.PreciseTime import PreciseTime
from server.app.dtos.NtpTimestamps import NtpTimestamps
from server.app.dtos.NtpMeasurement import NtpMeasurement
from server.app.services.NtpCalculator import NtpCalculator
from server.app.utils.calculations import calculate_jitter_from_measurements
from sqlalchemy.orm import Session


def make_mock_measurement(seconds_offset: int) -> NtpMeasurement:
    fake_measurement = MagicMock(spec=NtpMeasurement)

    timestamps = NtpTimestamps(
        PreciseTime(0, 0),
        PreciseTime(seconds_offset // 4, 0),
        PreciseTime(seconds_offset // 2, 0),
        PreciseTime(seconds_offset, 0)
    )
    fake_server_info = MagicMock()
    fake_server_info.ntp_server_ip = IPv4Address("1.2.3.4")
    fake_server_info.ntp_version = 4
    fake_measurement.timestamps = timestamps
    fake_measurement.server_info = fake_server_info

    return fake_measurement


@patch("server.app.utils.calculations.get_measurements_for_jitter_ip")
def test_calculate_jitter_from_measurements(mock_get_measurements):
    fake_initial_measurement = make_mock_measurement(1)
    fake_session = MagicMock(spec=Session)
    other_measurements = [
        make_mock_measurement(5),
        make_mock_measurement(3),
        make_mock_measurement(4),
        make_mock_measurement(6)
    ]

    mock_get_measurements.return_value = other_measurements

    times = 4
    res, no_measurement = calculate_jitter_from_measurements(fake_session, fake_initial_measurement, times)

    offsets = [NtpCalculator.calculate_offset(fake_initial_measurement.timestamps)] + [
        NtpCalculator.calculate_offset(m.timestamps) for m in other_measurements]

    expected = NtpCalculator.calculate_jitter(offsets)

    assert res == expected
    assert no_measurement == 5


@patch("server.app.utils.calculations.get_measurements_for_jitter_ip")
def test_calculate_jitter_with_no_history(mock_get_measurements):
    fake_initial_measurement = make_mock_measurement(2)
    fake_session = MagicMock(spec=Session)

    mock_get_measurements.return_value = []

    res, no_measurement = calculate_jitter_from_measurements(fake_session, fake_initial_measurement)

    assert res == 0.0  # or whatever default you expect
    assert no_measurement == 1


@patch("server.app.utils.calculations.get_measurements_for_jitter_ip")
def test_calculate_jitter_with_some_none(mock_get_measurements):
    fake_initial_measurement = make_mock_measurement(1)
    fake_session = MagicMock(spec=Session)

    other_measurements = [
        make_mock_measurement(3),
        None,
        make_mock_measurement(5),
        None,
    ]
    mock_get_measurements.return_value = other_measurements

    res, no_measurement = calculate_jitter_from_measurements(fake_session, fake_initial_measurement)

    valid_offsets = [
        NtpCalculator.calculate_offset(fake_initial_measurement.timestamps),
        NtpCalculator.calculate_offset(other_measurements[0].timestamps),
        NtpCalculator.calculate_offset(other_measurements[2].timestamps),
    ]
    expected = NtpCalculator.calculate_jitter(valid_offsets)

    assert res == expected
    assert no_measurement == 3


@patch("server.app.utils.calculations.get_measurements_for_jitter_ip")
def test_calculate_jitter_with_identical_offsets(mock_get_measurements):
    fake_initial_measurement = make_mock_measurement(4)
    fake_session = MagicMock(spec=Session)

    identical_measurements = [make_mock_measurement(4) for _ in range(5)]
    mock_get_measurements.return_value = identical_measurements

    res, no_measurement = calculate_jitter_from_measurements(fake_session, fake_initial_measurement)

    assert res == 0.0
    assert no_measurement == 6
