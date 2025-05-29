from ipaddress import ip_address

import pytest
from unittest.mock import Mock, patch

from server.app.models.RipeMeasurement import RipeMeasurement
from server.app.models.ProbeData import ProbeData
from server.app.utils.ripe_fetch_data import get_data_from_ripe_measurement, get_probe_data_from_ripe_by_id, \
    parse_probe_data, is_failed_measurement, successful_measurement, parse_data_from_ripe_measurement

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


@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_get_data_from_ripe_measurement(mock_get):
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


@patch("server.app.utils.ripe_fetch_data.requests.get")
def test_get_probe_data_from_ripe_by_id(mock_get):
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


@patch("server.app.utils.ripe_fetch_data.get_probe_data_from_ripe_by_id")
def test_parse_data_from_ripe_measurement(mock_get_probe):
    mock_get_probe.return_value = MOCK_PROBE_RESPONSE
    results = parse_data_from_ripe_measurement(MOCK_MEASUREMENT_RESPONSE)
    assert isinstance(results, list)
    assert isinstance(results[0], RipeMeasurement)
    assert results[0].ntp_measurement.vantage_point_ip == ip_address("83.231.3.54")
    assert results[0].time_to_result == 36.760828
    assert results[0].measurement_id == 123
    assert results[0].root_dispersion == 0.000198364
    assert results[0].ref_id == "GPSs"
    assert results[0].poll == 64
    assert results[0].probe_data.probe_id == 9999

    assert results[0].ntp_measurement.timestamps.client_sent_time.seconds != 0
    assert results[0].ntp_measurement.timestamps.client_sent_time.fraction != 0

    assert results[0].ntp_measurement.timestamps.server_recv_time.seconds != 0
    assert results[0].ntp_measurement.timestamps.server_recv_time.fraction != 0

    assert results[0].ntp_measurement.timestamps.server_sent_time.seconds != 0
    assert results[0].ntp_measurement.timestamps.server_sent_time.fraction != 0

    assert results[0].ntp_measurement.timestamps.client_recv_time.seconds != 0
    assert results[0].ntp_measurement.timestamps.client_recv_time.fraction != 0


@patch("server.app.utils.ripe_fetch_data.get_probe_data_from_ripe_by_id")
def test_parse_data_from_ripe_measurement_with_no_response(mock_get_probe):
    mock_get_probe.return_value = MOCK_PROBE_RESPONSE
    results = parse_data_from_ripe_measurement(MOCK_MEASUREMENT_RESPONSE_FAILED)
    assert isinstance(results, list)
    assert isinstance(results[0], RipeMeasurement)
    assert results[0].ntp_measurement.vantage_point_ip == ip_address("83.231.3.54")
    assert results[0].time_to_result == 0
    assert results[0].measurement_id == 123
    assert results[0].root_dispersion == 0
    assert results[0].ref_id == "NO REFERENCE"
    assert results[0].poll == 0
    assert results[0].probe_data.probe_id == 9999

    assert results[0].ntp_measurement.timestamps.client_sent_time.seconds == 0
    assert results[0].ntp_measurement.timestamps.client_sent_time.fraction == 0

    assert results[0].ntp_measurement.timestamps.server_recv_time.seconds == 0
    assert results[0].ntp_measurement.timestamps.server_recv_time.fraction == 0

    assert results[0].ntp_measurement.timestamps.server_sent_time.seconds == 0
    assert results[0].ntp_measurement.timestamps.server_sent_time.fraction == 0

    assert results[0].ntp_measurement.timestamps.client_recv_time.seconds == 0
    assert results[0].ntp_measurement.timestamps.client_recv_time.fraction == 0
