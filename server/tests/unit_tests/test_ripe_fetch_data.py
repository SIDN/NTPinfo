from ipaddress import ip_address

import pytest
from unittest.mock import Mock, patch

from server.app.dtos.PreciseTime import PreciseTime
from server.app.dtos.RipeMeasurement import RipeMeasurement
from server.app.dtos.ProbeData import ProbeData
from server.app.utils.ripe_fetch_data import get_data_from_ripe_measurement, get_probe_data_from_ripe_by_id, \
    parse_probe_data, is_failed_measurement, successful_measurement, parse_data_from_ripe_measurement, \
    check_all_measurements_scheduled, check_all_measurements_done

MOCK_MEASUREMENT_INFO = {
    "af": 4,
    "creation_time": 1748876705,
    "credits_per_result": 13,
    "description": "NTP measurement to 18.252.12.124",
    "estimated_results_per_day": 12,
    "group": "https://atlas.ripe.net/api/v2/measurements/groups/123456/",
    "group_id": 123456,
    "id": 123456,
    "in_wifi_group": False,
    "interval": None,
    "is_all_scheduled": True,
    "is_oneoff": True,
    "is_public": True,
    "packets": 2,
    "participant_count": 12,
    "probes_requested": 12,
    "probes_scheduled": 12,
    "resolve_on_probe": False,
    "resolved_ips": [
        "18.252.12.124"
    ],
    "result": "https://atlas.ripe.net/api/v2/measurements/123456/results/",
    "size": None,
    "spread": None,
    "start_time": 1748876705,
    "status": {
        "id": 4,
        "name": "Stopped",
        "when": 1748877060
    },
    "stop_time": 1748877060,
    "tags": [],
    "target": "18.252.12.124",
    "target_asn": None,
    "target_ip": "18.252.12.124",
    "target_prefix": None,
    "timeout": 4000,
    "type": "ntp"
}

MOCK_MEASUREMENT_INFO_NOT_SCHEDULED = {
    "af": 4,
    "creation_time": 1748876705,
    "credits_per_result": 13,
    "description": "NTP measurement to 18.252.12.124",
    "estimated_results_per_day": 12,
    "group": "https://atlas.ripe.net/api/v2/measurements/groups/123456/",
    "group_id": 123456,
    "id": 123456,
    "in_wifi_group": False,
    "interval": None,
    "is_all_scheduled": True,
    "is_oneoff": True,
    "is_public": True,
    "packets": 2,
    "participant_count": 12,
    "probes_requested": 12,
    "probes_scheduled": 5,
    "resolve_on_probe": False,
    "resolved_ips": [
        "18.252.12.124"
    ],
    "result": "https://atlas.ripe.net/api/v2/measurements/123456/results/",
    "size": None,
    "spread": None,
    "start_time": 1748876705,
    "status": {
        "id": 4,
        "name": "Stopped",
        "when": 1748877060
    },
    "stop_time": 1748877060,
    "tags": [],
    "target": "18.252.12.124",
    "target_asn": None,
    "target_ip": "18.252.12.124",
    "target_prefix": None,
    "timeout": 4000,
    "type": "ntp"
}

MOCK_MEASUREMENT_INFO_ONGOING = {
    "af": 4,
    "creation_time": 1748876705,
    "credits_per_result": 13,
    "description": "NTP measurement to 18.252.12.124",
    "estimated_results_per_day": 12,
    "group": "https://atlas.ripe.net/api/v2/measurements/groups/123456/",
    "group_id": 123456,
    "id": 123456,
    "in_wifi_group": False,
    "interval": None,
    "is_all_scheduled": True,
    "is_oneoff": True,
    "is_public": True,
    "packets": 2,
    "participant_count": 12,
    "probes_requested": 12,
    "probes_scheduled": 5,
    "resolve_on_probe": False,
    "resolved_ips": [
        "18.252.12.124"
    ],
    "result": "https://atlas.ripe.net/api/v2/measurements/123456/results/",
    "size": None,
    "spread": None,
    "start_time": 1748876705,
    "status": {
        "id": 4,
        "name": "Ongoing",
        "when": 1748877060
    },
    "stop_time": 1748877060,
    "tags": [],
    "target": "18.252.12.124",
    "target_asn": None,
    "target_ip": "18.252.12.124",
    "target_prefix": None,
    "timeout": 4000,
    "type": "ntp"
}

MOCK_MEASUREMENT_INFO_PROBES_ERROR = {

    "participant_count": 12,
    "probes_requested": -1,
    "probes_scheduled": 5,
}

MOCK_MEASUREMENT_INFO_NO_RESPONSE = {

    "participant_count": 12,
    "probes_requested": -1,
    "probes_scheduled": 5,
    "status": {
        "id": 2,
        "when": None
    }
}

MOCK_MEASUREMENT_ERROR = {
    "error": {
        "detail": "Method \"GET\" not allowed.",
        "status": 405,
        "title": "Method Not Allowed",
        "code": 104
    }
}

MOCK_MEASUREMENT_RESPONSE = [
    {
        "fw": 5090,
        "mver": "2.6.4",
        "lts": 8,
        "dst_name": "time.some_server.com",
        "ttr": 36.760828,
        "dst_addr": "18.252.12.124",
        "src_addr": "83.231.3.54",
        "proto": "UDP",
        "af": 4,
        "li": "no",
        "version": 4,
        "mode": "server",
        "stratum": 1,
        "poll": 64,
        "precision": 9.53674E-7,
        "root-delay": 0,
        "root-dispersion": 0.000198364,
        "ref-id": "GPSs",
        "ref-ts": 3957337537.1502366,
        "result": [
            {
                "x": "*"
            },
            {
                "origin-ts": 3957337543.171214,
                "receive-ts": 3957337543.1753526,
                "transmit-ts": 3957337543.1753654,
                "final-ts": 3957337543.180171,
                "rtt": 0.008944,
                "offset": 0.000334
            },
            {
                "origin-ts": 3957337543.180198,
                "receive-ts": 3957337543.1842,
                "transmit-ts": 3957337543.1842275,
                "final-ts": 3957337543.189035,
                "rtt": 0.008809,
                "offset": 0.000403
            }
        ],
        "msm_id": 123,
        "prb_id": 9999,
        "timestamp": 1748348739,
        "msm_name": "Ntp",
        "from": "83.231.3.54",
        "type": "ntp",
        "group_id": 123,
        "stored_timestamp": 134
    }
]

MOCK_MEASUREMENT_RESPONSE_FAILED = [
    {
        "fw": 4790,
        "lts": 73,
        "dst_name": "time.some_server.com",
        "dst_addr": "18.252.12.124",
        "src_addr": "83.231.3.54",
        "proto": "UDP",
        "af": 4,
        "result": [
            {
                "x": "*"
            },
            {
                "x": "*"
            },
            {
                "x": "*"
            }
        ],
        "msm_id": 123,
        "prb_id": 999,
        "timestamp": 1748348749,
        "msm_name": "Ntp",
        "from": "83.231.3.54",
        "type": "ntp",
        "group_id": 123,
        "stored_timestamp": 1748348764
    }
]

MOCK_PROBE_RESPONSE = {
    "address_v4": "83.231.3.54",
    "address_v6": "2a04:4c39:1:ca::a",
    "asn_v4": 1233,
    "asn_v6": 1233,
    "country_code": "RO",
    "description": "some",
    "firmware_version": 5090,
    "first_connected": 1704795929,
    "geometry": {
        "type": "Point",
        "coordinates": [
            12.12,
            14.14
        ]
    },
    "id": 9999,
    "is_anchor": "true",
    "is_public": "true",
    "last_connected": 1748537238,
    "prefix_v4": "83.231.0.0/19",
    "prefix_v6": "2a04:4c39::/29",
    "status": {
        "id": 1,
        "name": "Connected",
        "since": "2025-04-28T08:59:39Z"
    },
    "status_since": 1745830779,
    "tags": [
        {
            "name": "system: Anchor",
            "slug": "system-anchor"
        },
        {
            "name": "system: Resolves A Correctly",
            "slug": "system-resolves-a-correctly"
        },
        {
            "name": "system: Resolves AAAA Correctly",
            "slug": "system-resolves-aaaa-correctly"
        },
        {
            "name": "system: IPv4 Works",
            "slug": "system-ipv4-works"
        },
        {
            "name": "system: IPv6 Works",
            "slug": "system-ipv6-works"
        },
        {
            "name": "system: IPv4 Capable",
            "slug": "system-ipv4-capable"
        },
        {
            "name": "system: IPv6 Capable",
            "slug": "system-ipv6-capable"
        },
        {
            "name": "system: IPv6 Stable 30d",
            "slug": "system-ipv6-stable-30d"
        },
        {
            "name": "system: IPv6 Stable 1d",
            "slug": "system-ipv6-stable-1d"
        },
        {
            "name": "system: IPv4 Stable 30d",
            "slug": "system-ipv4-stable-30d"
        },
        {
            "name": "system: IPv4 Stable 90d",
            "slug": "system-ipv4-stable-90d"
        },
        {
            "name": "system: IPv6 Stable 90d",
            "slug": "system-ipv6-stable-90d"
        },
        {
            "name": "system: IPv4 Stable 1d",
            "slug": "system-ipv4-stable-1d"
        },
        {
            "name": "system: Virtual",
            "slug": "system-virtual"
        }
    ],
    "total_uptime": 43514758,
    "type": "Probe"
}

MOCK_PROBE_RESPONSE_ERROR = {
    "error": {
        "detail": "Not found.",
        "status": 404,
        "title": "Not Found",
        "code": 104
    }
}

MOCK_PROBE_RESPONSE_NO_ADDR = {
    "asn_v4": 1233,
    "asn_v6": 1233,
    "country_code": "RO",
    "description": "some",
    "firmware_version": 5090,
    "first_connected": 1704795929,
    "geometry": {
        "type": "Point",
        "coordinates": [
            12.12,
            14.14
        ]
    },
    "id": 9999,
}


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_get_data_from_ripe_measurement(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_RESPONSE

    data = get_data_from_ripe_measurement("123")
    assert isinstance(data, list)
    assert len(data) == 1
    assert "result" in data[0]
    assert data[0]["msm_id"] == 123
    assert data[0]["dst_name"] == "time.some_server.com"
    assert data[0]["dst_addr"] == "18.252.12.124"
    assert data[0]["from"] == "83.231.3.54"
    assert data[0]["prb_id"] == 9999


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_get_data_from_ripe_measurement_raises_on_error_response(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=400)
    mock_get.return_value.json.return_value = {
        "error": {
            "title": "Bad Request",
            "detail": "Invalid measurement ID."
        }
    }

    with pytest.raises(ValueError) as exc_info:
        get_data_from_ripe_measurement("invalid_id")

    assert "RIPE API error: Bad Request - Invalid measurement ID." in str(exc_info.value)


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_get_probe_data_from_ripe_by_id(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_PROBE_RESPONSE

    data = get_probe_data_from_ripe_by_id("9999")
    assert isinstance(data, dict)
    assert data["id"] == 9999
    assert data["address_v4"] == "83.231.3.54"
    assert data["country_code"] == "RO"
    assert data["geometry"]["coordinates"] == [12.12, 14.14]


def test_parse_probe_data():
    parsed = parse_probe_data(MOCK_PROBE_RESPONSE)
    assert isinstance(parsed, ProbeData)
    assert parsed.probe_id == 9999
    assert parsed.probe_addr[0] == ip_address("83.231.3.54")
    assert parsed.probe_addr[1] == ip_address("2a04:4c39:1:ca::a")
    assert parsed.probe_location.country_code == "RO"
    assert parsed.probe_location.coordinates == [12.12, 14.14]


def test_parse_probe_data_with_error():
    parsed = parse_probe_data(MOCK_PROBE_RESPONSE_ERROR)
    assert isinstance(parsed, ProbeData)
    assert parsed.probe_id == '-1'
    assert parsed.probe_addr == (None, None)
    assert parsed.probe_location is None


def test_parse_probe_data_with_no_probe_addr():
    parsed = parse_probe_data(MOCK_PROBE_RESPONSE_NO_ADDR)
    assert isinstance(parsed, ProbeData)
    assert parsed.probe_id == 9999
    assert parsed.probe_addr == (None, None)
    assert parsed.probe_location.country_code == "RO"
    assert parsed.probe_location.coordinates == [12.12, 14.14]


def test_is_failed_measurement_true():
    result = {"result": [{"x": "*"}, {"x": "*"}]}
    assert is_failed_measurement(result) is True


def test_is_failed_measurement_false():
    result = {"result": [{"x": "*"}, {"origin-ts": 3957337543.171214,
                                      "receive-ts": 3957337543.1753526,
                                      "transmit-ts": 3957337543.1753654,
                                      "final-ts": 3957337543.180171,
                                      "rtt": 0.008944,
                                      "offset": 0.000334}]}
    assert is_failed_measurement(result) is False


def test_successful_measurement_index():
    result = {"result": [{"x": "*"},
                         {"origin-ts": 3957337543.171214,
                          "receive-ts": 3957337543.1753526,
                          "transmit-ts": 3957337543.1753654,
                          "final-ts": 3957337543.180171,
                          "rtt": 0.008944,
                          "offset": 0.000334
                          },
                         {
                             "origin-ts": 3957337543.180198,
                             "receive-ts": 3957337543.1842,
                             "transmit-ts": 3957337543.1842275,
                             "final-ts": 3957337543.189035,
                             "rtt": 0.008809,
                             "offset": 0.000403
                         }]}
    assert successful_measurement(result) == 1


def test_successful_measurement_none():
    result = {"result": [{"x": "*"}]}
    assert successful_measurement(result) is None


@patch("server.app.utils.ripe_fetch_data.check_all_measurements_done")
@patch("server.app.utils.ripe_fetch_data.get_probe_data_from_ripe_by_id")
def test_parse_data_from_ripe_measurement(mock_get_probe, mock_check_done):
    mock_get_probe.return_value = MOCK_PROBE_RESPONSE
    mock_check_done.return_value = "Complete"
    results, status = parse_data_from_ripe_measurement(MOCK_MEASUREMENT_RESPONSE)
    assert status == "Complete"
    assert isinstance(results, list)
    assert isinstance(results[0], RipeMeasurement)
    assert results[0].ntp_measurement.vantage_point_ip == ip_address("83.231.3.54")
    assert results[0].time_to_result == 36.760828
    assert results[0].measurement_id == 123
    assert results[0].ntp_measurement.extra_details.root_dispersion == PreciseTime(seconds=0, fraction=851966)
    assert results[0].ref_id == "GPSs"
    assert results[0].ntp_measurement.extra_details.poll == 64
    assert results[0].probe_data.probe_id == 9999

    assert results[0].ntp_measurement.timestamps.client_sent_time.seconds != 0
    assert results[0].ntp_measurement.timestamps.client_sent_time.fraction != 0

    assert results[0].ntp_measurement.timestamps.server_recv_time.seconds != 0
    assert results[0].ntp_measurement.timestamps.server_recv_time.fraction != 0

    assert results[0].ntp_measurement.timestamps.server_sent_time.seconds != 0
    assert results[0].ntp_measurement.timestamps.server_sent_time.fraction != 0

    assert results[0].ntp_measurement.timestamps.client_recv_time.seconds != 0
    assert results[0].ntp_measurement.timestamps.client_recv_time.fraction != 0


@patch("server.app.utils.ripe_fetch_data.check_all_measurements_done")
@patch("server.app.utils.ripe_fetch_data.get_probe_data_from_ripe_by_id")
def test_parse_data_from_ripe_measurement_with_no_response(mock_get_probe, mock_check_done):
    mock_get_probe.return_value = MOCK_PROBE_RESPONSE
    mock_check_done.return_value = "Timeout"
    results, status = parse_data_from_ripe_measurement(MOCK_MEASUREMENT_RESPONSE_FAILED)
    assert status == "Timeout"
    assert isinstance(results, list)
    assert isinstance(results[0], RipeMeasurement)
    assert results[0].ntp_measurement.vantage_point_ip == ip_address("83.231.3.54")
    assert results[0].time_to_result == -1
    assert results[0].measurement_id == 123
    assert results[0].ntp_measurement.extra_details.root_dispersion == PreciseTime(seconds=-1, fraction=0)
    assert results[0].ref_id == "NO REFERENCE"
    assert results[0].ntp_measurement.extra_details.poll == -1
    assert results[0].probe_data.probe_id == 9999

    assert results[0].ntp_measurement.timestamps.client_sent_time.seconds == -1
    assert results[0].ntp_measurement.timestamps.client_sent_time.fraction == 0

    assert results[0].ntp_measurement.timestamps.server_recv_time.seconds == -1
    assert results[0].ntp_measurement.timestamps.server_recv_time.fraction == 0

    assert results[0].ntp_measurement.timestamps.server_sent_time.seconds == -1
    assert results[0].ntp_measurement.timestamps.server_sent_time.fraction == 0

    assert results[0].ntp_measurement.timestamps.client_recv_time.seconds == -1
    assert results[0].ntp_measurement.timestamps.client_recv_time.fraction == 0


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_scheduled(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_INFO

    data = check_all_measurements_scheduled("123456")
    assert data is True


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_not_scheduled(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_INFO_NOT_SCHEDULED

    data = check_all_measurements_scheduled("123456")
    assert data is False


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_probes_error(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_INFO_PROBES_ERROR

    with pytest.raises(ValueError, match="RIPE API error: The number of scheduled probes is negative"):
        check_all_measurements_scheduled("123456")


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_scheduled_error_get(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_ERROR

    with pytest.raises(ValueError,
                       match=r'RIPE API error: Method Not Allowed - Method "GET" not allowed\.'):
        check_all_measurements_scheduled("123456")


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_done(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_INFO

    response = check_all_measurements_done("123456", 12)
    assert response == "Complete"


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_done_stopped(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_INFO

    # status is 'Stopped'
    response = check_all_measurements_done("123456", 10)
    assert response == "Complete"


@patch("server.app.utils.ripe_fetch_data.time.time")
@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_done_ongoing(mock_get, mock_get_token, mock_time):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_time.return_value = 1748876764
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_INFO_ONGOING

    response = check_all_measurements_done("123456", 10)
    assert response == "Ongoing"


@patch("server.app.utils.ripe_fetch_data.time.time")
@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_done_timeout(mock_get, mock_get_token, mock_time):
    mock_get_token.return_value = "token"
    mock_time.return_value = 1748876770
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_INFO_ONGOING

    response = check_all_measurements_done("123456", 10)
    assert response == "Timeout"


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_done_no_status_name_from_ripe(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_INFO_NO_RESPONSE

    response = check_all_measurements_done("123456", 10)
    assert response == "Timeout"


@patch("server.app.utils.ripe_fetch_data.get_ripe_api_token")
@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_check_all_measurement_done_error_get(mock_get, mock_get_token):
    mock_get_token.return_value = "token"
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = MOCK_MEASUREMENT_ERROR

    with pytest.raises(ValueError,
                       match=r'RIPE API error: Method Not Allowed - Method "GET" not allowed\.'):
        check_all_measurements_done("123456", 1)
