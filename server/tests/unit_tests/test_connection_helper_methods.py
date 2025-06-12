from ipaddress import ip_address

import pytest
from unittest.mock import MagicMock

from server.app.models.CustomError import InvalidMeasurementDataError
from server.app.db.db_interaction import row_to_dict, rows_to_dicts, dict_to_measurement, rows_to_measurements
from server.app.models.Measurement import Measurement
from server.app.models.Time import Time
from server.app.dtos.NtpMeasurement import NtpMeasurement


@pytest.fixture
def fake_measurement():
    m = MagicMock(spec=Measurement)
    m.id = 1
    m.vantage_point_ip = "1.2.3.4"
    m.ntp_server_ip = ip_address("5.6.7.8")
    m.ntp_server_name = "ntp.example.com"
    m.ntp_version = 4
    m.ntp_server_ref_parent = "9.9.9.9"
    m.ref_name = "ref"
    m.time_offset = 1.23
    m.rtt = 0.45
    m.stratum = 2
    m.precision = -20
    m.reachability = ""
    m.root_delay = 12
    m.root_delay_prec = 5
    m.ntp_last_sync_time = 1650000000
    m.ntp_last_sync_time_prec = 1
    return m


@pytest.fixture
def fake_time():
    t = MagicMock(spec=Time)
    t.client_sent = 1650000001
    t.client_sent_prec = 0
    t.server_recv = 1650000002
    t.server_recv_prec = 0
    t.server_sent = 1650000003
    t.server_sent_prec = 0
    t.client_recv = 1650000004
    t.client_recv_prec = 0
    return t


def test_row_to_dict(fake_measurement, fake_time):
    result = row_to_dict(fake_measurement, fake_time)

    assert result["vantage_point_ip"] == "1.2.3.4"
    assert result["ntp_server_ip"] == ip_address("5.6.7.8")
    assert result["offset"] == 1.23
    assert result["client_sent"] == 1650000001
    assert result["client_recv_prec"] == 0


def test_rows_to_dicts(fake_measurement, fake_time):
    fake_row = MagicMock()
    fake_row.Measurement = fake_measurement
    fake_row.Time = fake_time
    rows = [fake_row, fake_row]

    result = rows_to_dicts(rows)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["ntp_server_name"] == "ntp.example.com"
    assert result[1]["ntp_server_ip"] == ip_address("5.6.7.8")


def test_dict_to_measurement(fake_measurement, fake_time):
    entry = row_to_dict(fake_measurement, fake_time)
    ntp_measurement = dict_to_measurement(entry)

    assert isinstance(ntp_measurement, NtpMeasurement)
    assert ntp_measurement.vantage_point_ip == ip_address("1.2.3.4")
    assert ntp_measurement.main_details.offset == 1.23
    assert ntp_measurement.server_info.ntp_server_name == "ntp.example.com"
    assert ntp_measurement.timestamps.client_sent_time.seconds == 1650000001
    assert ntp_measurement.timestamps.client_sent_time.fraction == 0


def test_dict_to_measurement_missing_keys():
    incomplete_entry = {
        "vantage_point_ip": ip_address("1.2.3.4")
    }
    with pytest.raises(InvalidMeasurementDataError) as exc_info:
        dict_to_measurement(incomplete_entry)
    assert "Missing required keys" in str(exc_info.value)


def test_dict_to_measurement_malformed_values():
    malformed_entry = {
        'vantage_point_ip': "1.2.3.4",
        'ntp_server_ip': "5.6.7.8",
        'ntp_server_name': "ntp.example.com",
        'ntp_version': 4,
        'ntp_server_ref_parent_ip': "9.9.9.9",
        'ref_name': "ref",
        'offset': "should_be_float",  # wrong type
        'RTT': 0.1,
        'stratum': 2,
        'precision': -20,
        'reachability': 255,
        'root_delay': 0,
        'root_delay_prec': 0,
        'poll': 6,
        'root_dispersion': 0,
        'root_dispersion_prec': 0,
        'ntp_last_sync_time': 1000,
        'ntp_last_sync_time_prec': 0,
        'client_sent': 1650000001,
        'client_sent_prec': 0,
        'server_recv': 1650000002,
        'server_recv_prec': 0,
        'server_sent': 1650000003,
        'server_sent_prec': 0,
        'client_recv': 1650000004,
        'client_recv_prec': 0,
    }

    with pytest.raises(InvalidMeasurementDataError) as exc_info:
        dict_to_measurement(malformed_entry)
    assert "Failed to build NtpMeasurement" in str(exc_info.value)


def test_rows_to_measurements(fake_measurement, fake_time):
    fake_row = MagicMock()
    fake_row.Measurement = fake_measurement
    fake_row.Time = fake_time
    rows = [fake_row, fake_row]

    result = rows_to_measurements(rows)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], NtpMeasurement)
    assert isinstance(result[1], NtpMeasurement)
    assert result[0].main_details.rtt == 0.45
    assert result[1].server_info.ntp_server_name == "ntp.example.com"
