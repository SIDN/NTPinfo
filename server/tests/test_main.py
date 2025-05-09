import pytest
from unittest.mock import patch, MagicMock
from server.app.models import NtpMeasurement
from server.app.main import measure


@patch("server.app.main.insert_measurement")
@patch("server.app.main.perform_ntp_measurement_domain_name")
@patch("server.app.main.perform_ntp_measurement_ip")
def test_measure_with_ip(mock_measure_ip, mock_measure_domain, mock_insert):
    fake_measurement = MagicMock(spec=NtpMeasurement)
    mock_measure_ip.return_value = fake_measurement

    result = measure("192.168.1.1")

    assert result is fake_measurement
    mock_measure_ip.assert_called_once_with("192.168.1.1")
    mock_insert.assert_called_once_with(fake_measurement, mock_insert.call_args[0][1])  # pool
    mock_measure_domain.assert_not_called()


@patch("server.app.main.insert_measurement")
@patch("server.app.main.perform_ntp_measurement_domain_name")
@patch("server.app.main.perform_ntp_measurement_ip")
def test_measure_with_domain(mock_measure_ip, mock_measure_domain, mock_insert):
    fake_measurement = MagicMock(spec=NtpMeasurement)
    mock_measure_domain.return_value = fake_measurement
    mock_measure_ip.return_value = None

    result = measure("pool.ntp.org")

    assert result is fake_measurement
    mock_measure_domain.assert_called_once_with("pool.ntp.org")
    mock_insert.assert_called_once_with(fake_measurement, mock_insert.call_args[0][1])  # pool
    mock_measure_ip.assert_not_called()


@patch("server.app.main.insert_measurement")
@patch("server.app.main.perform_ntp_measurement_domain_name")
@patch("server.app.main.perform_ntp_measurement_ip")
def test_measure_with_invalid_ip(mock_measure_ip, mock_measure_domain, mock_insert):
    fake_measurement = MagicMock(spec=NtpMeasurement)
    mock_measure_ip.return_value = None
    mock_measure_domain.return_value = fake_measurement

    result = measure("not.an.ip")

    assert result is fake_measurement
    mock_measure_ip.assert_not_called()
    mock_measure_domain.assert_called_once_with("not.an.ip")
    mock_insert.assert_called_once_with(fake_measurement, mock_insert.call_args[0][1])


@patch("server.app.main.insert_measurement")
@patch("server.app.main.perform_ntp_measurement_domain_name")
@patch("server.app.main.perform_ntp_measurement_ip")
def test_measure_with_unresolvable_input(mock_measure_ip, mock_measure_domain, mock_insert):
    mock_measure_ip.return_value = None
    mock_measure_domain.return_value = None

    result = measure("not.an.ip")

    assert result is None
    mock_measure_ip.assert_not_called()
    mock_measure_domain.assert_called_once_with("not.an.ip")
    mock_insert.assert_not_called()


@patch("server.app.main.insert_measurement")
@patch("server.app.main.perform_ntp_measurement_domain_name")
@patch("server.app.main.perform_ntp_measurement_ip")
def test_measure_with_exception(mock_measure_ip, mock_measure_domain, mock_insert):
    mock_measure_ip.return_value = None
    mock_measure_domain.side_effect = Exception("DNS failure")

    result = measure("invalid.server")

    assert result is None
    mock_measure_ip.assert_not_called()
    mock_measure_domain.assert_called_once_with("invalid.server")
    mock_insert.assert_not_called()
