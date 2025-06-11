from ipaddress import IPv4Address

import pytest

from server.app.utils.perform_measurements import *
from unittest.mock import patch, MagicMock
from server.app.utils.calculations import ntp_precise_time_to_human_date
from server.app.dtos.PreciseTime import PreciseTime


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


def test_ntp_precise_time_to_human_date():
    t = PreciseTime(None, 12345)
    assert ntp_precise_time_to_human_date(t) == ""
    t2 = PreciseTime(3955513183, 623996928)
    assert ntp_precise_time_to_human_date(t2) == "2025-05-06 09:39:43.145286 UTC"


@patch("server.app.utils.domain_name_to_ip.socket.getaddrinfo")
@patch("server.app.utils.perform_measurements.ntplib.NTPClient.request")
def test_perform_ntp_measurement_domain_name(mock_request, mock_getaddrinfo):
    # Mock socket.getaddrinfo
    mock_getaddrinfo.return_value = [(None, None, None, None, ("123.45.67.89", 0))]

    # Create a fake ntplib response
    mock_response = MagicMock()
    mock_response.ref_id = 1590075150

    mock_response.ref_timestamp = 3948758383.2
    mock_response.orig_timestamp = 3948758384.0
    mock_response.recv_timestamp = 3948758385.0
    mock_response.tx_timestamp = 3948758386.0
    mock_response.dest_timestamp = 3948758389.2

    mock_response.offset = 0.001
    mock_response.delay = 0.002
    mock_response.stratum = 2
    mock_response.precision = -20

    mock_response.root_delay = 0.025
    mock_response.leap = 0
    mock_request.return_value = mock_response

    result_tuples = perform_ntp_measurement_domain_name_list("mock.ntp.server", None)

    assert result_tuples is not None
    assert isinstance(result_tuples, list)
    assert len(result_tuples) == 1
    result = result_tuples[0]

    assert result.server_info.ntp_version == 4
    assert result.server_info.ntp_server_ip == IPv4Address("123.45.67.89")
    assert result.server_info.ntp_server_name == "mock.ntp.server"
    assert result.server_info.ntp_server_ref_parent_ip == IPv4Address("94.198.159.14")
    assert result.server_info.ref_name is None

    assert result.timestamps.client_sent_time == PreciseTime(seconds=3948758389, fraction=858992640)
    assert result.timestamps.server_recv_time == PreciseTime(seconds=3948758384, fraction=0)
    assert result.timestamps.server_sent_time == PreciseTime(seconds=3948758385, fraction=0)
    assert result.timestamps.client_recv_time == PreciseTime(seconds=3948758386, fraction=0)

    assert result.main_details.offset == 0.001
    assert result.main_details.rtt == 0.002
    assert result.main_details.stratum == 2
    assert result.main_details.precision == -20
    assert result.main_details.reachability == ""

    assert result.extra_details.root_delay == PreciseTime(seconds=0, fraction=107374182)
    assert result.extra_details.ntp_last_sync_time == PreciseTime(seconds=3948758383, fraction=858992640)
    assert result.extra_details.leap == 0


@patch("server.app.utils.perform_measurements.ntplib.NTPClient.request")
def test_perform_ntp_measurement_ip(mock_request):
    # Create a fake ntplib response
    mock_response = MagicMock()
    mock_response.ref_id = 1590075150

    mock_response.ref_timestamp = 3948758383.2
    mock_response.orig_timestamp = 3948758384.0
    mock_response.recv_timestamp = 3948758385.0
    mock_response.tx_timestamp = 3948758386.0
    mock_response.dest_timestamp = 3948758389.2

    mock_response.offset = 0.001
    mock_response.delay = 0.002
    mock_response.stratum = 2
    mock_response.precision = -20

    mock_response.root_delay = 0.025
    mock_response.leap = 0
    mock_request.return_value = mock_response

    result = perform_ntp_measurement_ip("123.45.67.89", 3)

    assert result is not None

    assert result.server_info.ntp_version == 3
    assert result.server_info.ntp_server_ip == IPv4Address("123.45.67.89")
    assert result.server_info.ntp_server_name is None
    assert result.server_info.ntp_server_ref_parent_ip == IPv4Address("94.198.159.14")
    assert result.server_info.ref_name is None

    assert result.timestamps.client_sent_time == PreciseTime(seconds=3948758389, fraction=858992640)
    assert result.timestamps.server_recv_time == PreciseTime(seconds=3948758384, fraction=0)
    assert result.timestamps.server_sent_time == PreciseTime(seconds=3948758385, fraction=0)
    assert result.timestamps.client_recv_time == PreciseTime(seconds=3948758386, fraction=0)

    assert result.main_details.offset == 0.001
    assert result.main_details.rtt == 0.002
    assert result.main_details.stratum == 2
    assert result.main_details.precision == -20
    assert result.main_details.reachability == ""

    assert result.extra_details.root_delay == PreciseTime(seconds=0, fraction=107374182)
    assert result.extra_details.ntp_last_sync_time == PreciseTime(seconds=3948758383, fraction=858992640)
    assert result.extra_details.leap == 0

    assert print_ntp_measurement(result) == True
    assert print_ntp_measurement(23) == False

@patch("server.app.utils.perform_measurements.get_server_ip")
def test_convert_ntp_response_to_measurement(mock_server_ip):
    mock_server_ip.return_value = IPv4Address("2.4.5.6")
    mock_response = MagicMock()
    mock_response.ref_id = 23467
    mock_response.stratum = 1
    mock_response.orig_timestamp = 3000.23
    mock_response.recv_timestamp = 3001.56
    mock_response.tx_timestamp = 3002.78
    mock_response.dest_timestamp = 3003.97
    mock_response.ref_timestamp = 2999.123
    mock_response.offset = 0.001
    mock_response.delay = 0.002
    mock_response.stratum = 2
    mock_response.precision = -20

    mock_response.root_delay = 0.025
    mock_response.leap = 0
    mock_response.poll = 0.02
    mock_response.root_dispersion = 4000

    result = convert_ntp_response_to_measurement(mock_response, "32.34.35.36", "ntp server", 4)

    assert result is not None

    assert result.server_info.ntp_version == 4
    assert result.server_info.ntp_server_ip == IPv4Address("32.34.35.36")
    assert result.server_info.ntp_server_name == "ntp server"
    assert result.server_info.ntp_server_ref_parent_ip == IPv4Address('0.0.91.171')
    assert result.server_info.ref_name is None

    assert result.timestamps.client_sent_time == PreciseTime(seconds=3000, fraction=987842478)
    assert result.timestamps.server_recv_time == PreciseTime(seconds=3001, fraction=2405181685)
    assert result.timestamps.server_sent_time == PreciseTime(seconds=3002, fraction=3350074490)
    assert result.timestamps.client_recv_time == PreciseTime(seconds=3003, fraction=4166118277)

    assert result.main_details.offset == 0.001
    assert result.main_details.rtt == 0.002
    assert result.main_details.stratum == 2
    assert result.main_details.precision == -20
    assert result.main_details.reachability == ""

    assert result.extra_details.root_delay == PreciseTime(seconds=0, fraction=107374182)
    assert result.extra_details.ntp_last_sync_time == PreciseTime(seconds=2999, fraction=528280977)
    assert result.extra_details.leap == 0
    assert result.extra_details.poll == 0.02
    assert result.extra_details.root_dispersion == PreciseTime(seconds=4000, fraction=0)

    assert result.vantage_point_ip == IPv4Address("2.4.5.6")

@patch("server.app.utils.perform_measurements.get_server_ip")
def test_convert_ntp_response_to_measurement_exception(mock_server_ip):
    mock_server_ip.return_value = None
    mock_response = MagicMock()
    mock_response.ref_id = 23467
    mock_response.stratum = 1
    mock_response.orig_timestamp = 3000.23
    mock_response.recv_timestamp = 3001.56
    mock_response.tx_timestamp = 3002.78
    mock_response.dest_timestamp = 3003.97
    mock_response.ref_timestamp = 2999.123
    mock_response.offset = 0.001
    mock_response.delay = 0.002
    mock_response.stratum = 2
    mock_response.precision = -20

    mock_response.root_delay = 0.025
    mock_response.leap = 0
    mock_response.poll = 0.02
    mock_response.root_dispersion = 4000

    result = convert_ntp_response_to_measurement(mock_response, "32.34.35.36", "ntp server", 4)

    assert result is not None
    assert result.server_info.ntp_version == 4
    assert result.vantage_point_ip is None

    assert convert_ntp_response_to_measurement(mock_response, "something else", "ntp server", 4) is None


@patch("server.app.utils.perform_measurements.requests.post")
@patch("server.app.utils.perform_measurements.get_request_settings")
def test_perform_ripe_measurement_domain_name_normal(mock_settings, mock_post):
    mock_settings.return_value = ({"Authorization": "Key"}, {"some": 36, "other": "other"})
    mock_response = MagicMock()
    mock_response.json.return_value = {"measurements": [85439]}
    mock_post.return_value = mock_response

    result = perform_ripe_measurement_domain_name("time.apple.com", "2.3.4.5", 10)

    assert result == 85439

@patch("server.app.utils.perform_measurements.requests.post")
@patch("server.app.utils.perform_measurements.get_request_settings")
def test_perform_ripe_measurement_domain_name_try_catch(mock_settings, mock_post):
    mock_settings.return_value = ({"Authorization": "Key"}, {"somefield": 3, "other": "no"})
    mock_response = MagicMock()
    mock_response.json.return_value = {"error": "not found"}
    mock_post.return_value = mock_response

    with pytest.raises(RipeMeasurementError, match="not found"):
        perform_ripe_measurement_domain_name("time.apple.com", "2.3.4.5", 10)

    mock_response2 = MagicMock()
    mock_response2.json.return_value = {"something": "error, not found"}
    mock_post.return_value = mock_response2
    with pytest.raises(RipeMeasurementError, match=r"Ripe measurement failed:.*"):
        perform_ripe_measurement_domain_name("time.apple.com", "2.3.4.5", 10)

@patch("server.app.utils.perform_measurements.requests.post")
@patch("server.app.utils.perform_measurements.get_request_settings")
def test_perform_ripe_measurement_domain_name_exceptions(mock_settings, mock_post):
    # invalid "probes requested"
    with pytest.raises(InputError):
        perform_ripe_measurement_domain_name("ntp.pool.org", "2.3.4.5", -1)
    with pytest.raises(InputError):
        perform_ripe_measurement_domain_name("ntp.pool.org", "2.3.4.5", 0)
    # invalid client ip
    with pytest.raises(InputError):
        perform_ripe_measurement_domain_name("ntp.pool.org", "blabla", 3)


@patch("server.app.utils.perform_measurements.requests.post")
@patch("server.app.utils.perform_measurements.get_request_settings")
def test_perform_ripe_measurement_ip_normal(mock_settings, mock_post):
    mock_settings.return_value = ({"Authorization": "Key"}, {"somefield": 3, "other": "no"})
    mock_response = MagicMock()
    mock_response.json.return_value = {"measurements": [12412]}
    mock_post.return_value = mock_response

    result = perform_ripe_measurement_ip("123.45.67.89", "2.3.4.5", 10)

    assert result == 12412

@patch("server.app.utils.perform_measurements.requests.post")
@patch("server.app.utils.perform_measurements.get_request_settings")
def test_perform_ripe_measurement_ip_try_catch(mock_settings, mock_post):
    mock_settings.return_value = ({"Authorization": "Key"}, {"somefield": 3, "other": "no"})
    mock_response = MagicMock()
    mock_response.json.return_value = {"error": "not found"}
    mock_post.return_value = mock_response

    with pytest.raises(RipeMeasurementError, match="not found"):
        perform_ripe_measurement_ip("123.45.67.89", "2.3.4.5", 10)

    mock_response2 = MagicMock()
    mock_response2.json.return_value = {"something": "error, not found"}
    mock_post.return_value = mock_response2
    with pytest.raises(RipeMeasurementError, match=r"Ripe measurement failed:.*"):
        perform_ripe_measurement_ip("123.45.67.89", "2.3.4.5", 10)


@patch("server.app.utils.perform_measurements.requests.post")
@patch("server.app.utils.perform_measurements.get_request_settings")
def test_perform_ripe_measurement_ip_exceptions(mock_settings, mock_post):
    # invalid "probes requested"
    with pytest.raises(InputError):
        perform_ripe_measurement_ip("123.45.67.89", "2.3.4.5", -1)
    with pytest.raises(InputError):
        perform_ripe_measurement_ip("123.45.67.89", "2.3.4.5", 0)
    # invalid client ip
    with pytest.raises(InputError):
        perform_ripe_measurement_ip("123.45.67.89", "blabla", 3)
    # invalid ntp server IP
    with pytest.raises(InputError):
        perform_ripe_measurement_ip("123.45aso.67.89", "2.3.4.5", 0)


@patch("server.app.utils.perform_measurements.get_probes")
@patch("server.app.utils.perform_measurements.get_ripe_account_email")
@patch("server.app.utils.perform_measurements.get_ripe_timeout_per_probe_ms")
@patch("server.app.utils.perform_measurements.get_ripe_packets_per_probe")
@patch("server.app.utils.perform_measurements.get_ripe_api_token")
def test_get_request_settings_ok(mock_ripe_api_token, mock_packets, mock_timeout, mock_email, mock_probes):
    mock_ripe_api_token.return_value = "token"
    mock_packets.return_value = 4
    mock_timeout.return_value = 3400
    mock_email.return_value = "email@email.com"
    mock_probes.return_value = [{
        "type": "probes",
        "value": "234,12,865",
        "requested": 3
    },
    {
        "type": "asn",
        "value": "9009",
        "requested": 4
    }]

    (h, c) = get_request_settings(4, "ntp.server.com", "74.22.34.47",28)
    assert h == {
        "Authorization": "Key token",
        "Content-Type": "application/json"
    }
    assert c == {"definitions": [
        {
            "type": "ntp",
            "af": 4,
            "resolve_on_probe": True,
            "description": "NTP measurement to ntp.server.com",
            "packets": 4,
            "timeout": 3400,
            "skip_dns_check": False,
            "target": "ntp.server.com"
        }
    ],
        "is_oneoff": True,
        "bill_to": "email@email.com",
        "probes": [{
            "type": "probes",
            "value": "234,12,865",
            "requested": 3
        },
            {
                "type": "asn",
                "value": "9009",
                "requested": 4
            }]
    }
@patch("server.app.utils.perform_measurements.get_probes")
@patch("server.app.utils.perform_measurements.get_ripe_account_email")
@patch("server.app.utils.perform_measurements.get_ripe_timeout_per_probe_ms")
@patch("server.app.utils.perform_measurements.get_ripe_packets_per_probe")
@patch("server.app.utils.perform_measurements.get_ripe_api_token")
def test_get_request_settings_exception(mock_ripe_api_token, mock_packets, mock_timeout, mock_email, mock_probes):
    mock_ripe_api_token.return_value = "token"
    mock_packets.return_value = 4
    mock_timeout.return_value = 3400
    mock_email.return_value = "email@email.com"
    mock_probes.side_effect = InputError("exc")
    with pytest.raises(Exception):
        get_request_settings(4, "ntp.server.com", "74.22.34.47", 28)

    mock_timeout.reset_mock()
    mock_timeout.side_effect = ValueError("env problem")
    with pytest.raises(ValueError):
        get_request_settings(4, "ntp.server.com", "74.22.34.47", 28)
