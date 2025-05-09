import pytest
from unittest.mock import patch, MagicMock
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.main import measure, fetch_historic_data_with_timestamps
from datetime import datetime


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


@patch("server.app.main.get_measurements_timestamps_ip")
@patch("server.app.main.parse_ip")
def test_fetch_historic_data_empty_result(mock_parse_ip, mock_get_ip):
    mock_parse_ip.return_value = "10.0.0.5"
    mock_get_ip.return_value = []

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)

    results = fetch_historic_data_with_timestamps("10.0.0.5", start, end)
    assert results == []


@patch("server.app.main.get_measurements_timestamps_ip")
@patch("server.app.main.get_measurements_timestamps_dn")
@patch("server.app.main.parse_ip")
def test_fetch_historic_data_ip(mock_parse_ip, mock_get_dn, mock_get_ip):
    mock_parse_ip.return_value = "192.168.1.1"
    mock_get_ip.return_value = [
        {
            "id": 1,
            "ntp_server_ip": "192.168.1.1",
            "ntp_server_name": "test",
            "ntp_version": 3,
            "ntp_server_ref_parent_ip": "10.0.0.1",
            "ref_name": "parent.ref",

            "offset": 0.1,
            "delay": 0.2,
            "stratum": 2,
            "precision": -20,
            "reachability": 255,

            "root_delay": 10,
            "root_delay_prec": 100,
            "ntp_last_sync_time": 20,
            "ntp_last_sync_time_prec": 200,

            "client_sent": 1, "client_sent_prec": 10,
            "server_recv": 2, "server_recv_prec": 20,
            "server_sent": 3, "server_sent_prec": 30,
            "client_recv": 4, "client_recv_prec": 40,

        }
    ]
    mock_get_dn.return_value = []

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)

    results = fetch_historic_data_with_timestamps("192.168.1.1", start, end)

    assert isinstance(results, list)
    assert len(results) == 1
    print(results[0])
    assert isinstance(results[0], NtpMeasurement)
    mock_parse_ip.assert_called_once()
    mock_get_ip.assert_called_once()
    mock_get_dn.assert_not_called()


@patch("server.app.main.get_measurements_timestamps_ip")
@patch("server.app.main.get_measurements_timestamps_dn")
def test_fetch_historic_data_domain_name(mock_get_dn, mock_get_ip):
    mock_get_ip.return_value = []
    mock_get_dn.return_value = [
        {
            "id": 1,
            "ntp_server_ip": "192.168.1.1",
            "ntp_server_name": "time.google.com",
            "ntp_version": 3,
            "ntp_server_ref_parent_ip": "10.0.0.1",
            "ref_name": "parent.ref",

            "offset": 0.1,
            "delay": 0.2,
            "stratum": 2,
            "precision": -20,
            "reachability": 255,

            "root_delay": 10,
            "root_delay_prec": 100,
            "ntp_last_sync_time": 20,
            "ntp_last_sync_time_prec": 200,

            "client_sent": 1, "client_sent_prec": 10,
            "server_recv": 2, "server_recv_prec": 20,
            "server_sent": 3, "server_sent_prec": 30,
            "client_recv": 4, "client_recv_prec": 40,

        }
    ]

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)

    results = fetch_historic_data_with_timestamps("time.google.com", start, end)

    assert isinstance(results, list)
    assert len(results) == 1
    print(results[0])
    assert isinstance(results[0], NtpMeasurement)
    mock_get_ip.assert_not_called()
    mock_get_dn.assert_called_once()
