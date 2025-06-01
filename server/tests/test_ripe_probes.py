import math
import pytest
from server.app.utils.ripe_probes import get_random_probes, get_area_probes, get_asn_probes, get_prefix_probes, \
    get_country_probes, get_best_probe_types, get_probes, get_available_probes_asn, get_available_probes_prefix, \
    get_available_probes_country, take_from_available_probes
from unittest.mock import patch, MagicMock


@patch("server.app.utils.ripe_probes.get_best_probe_types")
@patch("server.app.utils.ripe_probes.get_ip_network_details")
@patch("server.app.utils.ripe_probes.get_prefix_from_ip")
def test_get_probes_all_good(mock_get_prefix_from_ip, mock_get_network_details, mock_get_best_probe_types):
    types: dict[str, int] = {
        "country": 1,
        "area": 10,
        "asn": 2,
        "prefix": 14,
        "random": 5
    }
    mock_get_prefix_from_ip.return_value = "80.211.224.0/20"
    mock_get_network_details.return_value = ("AS15169","IT","West")
    mock_get_best_probe_types.return_value = types

    probes_result = get_probes("80.211.238.247")

    answer= [{'requested': 1, 'type': 'country', 'value': 'IT'},
             {'requested': 10, 'type': 'area', 'value': 'West'},
             {'requested': 2, 'type': 'asn', 'value': 'AS15169'},
             {'requested': 14, 'type': 'prefix', 'value': '80.211.224.0/20'},
             {'requested': 5, 'type': 'area', 'value': 'WW'}
    ]
    assert probes_result == answer

@patch("server.app.utils.ripe_probes.get_best_probe_types")
@patch("server.app.utils.ripe_probes.get_ip_network_details")
@patch("server.app.utils.ripe_probes.get_prefix_from_ip")
def test_get_probes_some_none(mock_get_prefix_from_ip, mock_get_network_details, mock_get_best_probe_types):
    types: dict[str, int] = {
        "country": 1,
        "area": 0,
        "asn": 2,
        "prefix": 0,
        "random": 5
    }
    mock_get_prefix_from_ip.return_value=None
    mock_get_network_details.return_value = ("AS15169","IT",None)
    mock_get_best_probe_types.return_value = types

    probes_result= get_probes("80.211.238.247")#(ip_asn="AS15169", ip_prefix="None", ip_country="IT", ip_area="None")

    answer= [{'requested': 1, 'type': 'country', 'value': 'IT'},
             {'requested': 2, 'type': 'asn', 'value': 'AS15169'},
             {'requested': 5, 'type': 'area', 'value': 'WW'}
    ]
    assert probes_result == answer

@patch("server.app.utils.ripe_probes.get_best_probe_types")
@patch("server.app.utils.ripe_probes.get_ip_network_details")
@patch("server.app.utils.ripe_probes.get_prefix_probes")
def test_get_probes_unexpected(mock_get_prefix_from_ip, mock_get_network_details, mock_get_best_probe_types):
    types: dict[str, int] = {
        "country": 0,
        "area": 0,
        "asn": 2,
        "tiger": 10,
        "prefix": 0,
        "random": 1
    }
    mock_get_prefix_from_ip.return_value = None
    mock_get_network_details.return_value = ("AS15169", None, None)
    mock_get_best_probe_types.return_value = types

    probes_result = get_probes("80.211.238.247")

    answer= [{'requested': 2, 'type': 'asn', 'value': 'AS15169'},
             {'requested': 10, 'type': 'area', 'value': 'WW'},
             {'requested': 1, 'type': 'area', 'value': 'WW'} # it is fine to add it separately, as the request would be the same
    ]
    assert probes_result == answer

def test_get_best_probe_types_first_3_none():
    #all None
    result = get_best_probe_types(None,None,None,None,4,34)
    assert result["asn"] == 0
    assert result["prefix"] == 0
    assert result["country"] == 0
    assert result["area"] == 0
    assert result["random"] == 34

    #area is available
    result = get_best_probe_types(None,None,None,"West",4,34)
    assert result["asn"] == 0
    assert result["prefix"] == 0
    assert result["country"] == 0
    assert result["area"] == 34
    assert result["random"] == 0

    #negative nr of probes requested
    with pytest.raises(Exception):
        get_best_probe_types("AS15169", "80.211.224.0/20", "NL", "North-Central", 4, -5)
    with pytest.raises(Exception):
        get_best_probe_types("AS15169", "2a06:93c0::/29", "NL", "North-Central", 6, -1)
def test_get_random_probes():
    answer = {
        "type": "area",
        "value": "WW",
        "requested": 7
    }
    assert get_random_probes(7) == answer

def test_get_area_probes():
    answer = {
        "type": "area",
        "value": "West",
        "requested": 7
    }
    assert get_area_probes("West",7) == answer
    answer = {
        "type": "area",
        "value": "North-East",
        "requested": 70
    }
    assert get_area_probes("North-East",70) == answer

def test_get_asn_probes():
    answer = {
        "type": "asn",
        "value": "AS15169",
        "requested": 7
    }
    assert get_asn_probes("AS15169",7) == answer
    answer = {
        "type": "asn",
        "value": "AS13335",
        "requested": 20
    }
    assert get_asn_probes("AS13335",20) == answer

def test_get_prefix_probes():
    answer = {
        "type": "prefix",
        "value": "162.159.200.0/24",
        "requested": 7
    }
    assert get_prefix_probes("162.159.200.0/24",7) == answer
    answer = {
        "type": "prefix",
        "value": "192.2.3.0/8",
        "requested": 20
    }
    assert get_prefix_probes("192.2.3.0/8",20) == answer

def test_get_country_probes():
    answer = {
        "type": "country",
        "value": "NL",
        "requested": 7
    }
    assert get_country_probes("NL",7) == answer
    answer = {
        "type": "country",
        "value": "RO",
        "requested": 20
    }
    assert get_country_probes("RO",20) == answer

@patch("server.app.utils.ripe_probes.ProbeRequest")
def test_get_available_probes_asn(mock_probe_request):
    mock = MagicMock()
    mock.total_count = 58
    mock_probe_request.return_value = mock

    # simulate the part with next()
    mock.__iter__.return_value = iter([None])

    #test ipv4
    result = get_available_probes_asn("AS12345","ipv4")
    assert result == 58
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["asn"] == 12345
    assert kwargs["tags"] == "system-ipv4-works"
    assert kwargs["status"] == 1

    #test ipv6
    mock_probe_request.reset_mock()
    result = get_available_probes_asn("AS67890","ipv6")
    assert result == 58
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["asn"] == 67890
    assert kwargs["tags"] == "system-ipv6-works"
    assert kwargs["status"] == 1

@patch("server.app.utils.ripe_probes.ProbeRequest")
def test_get_available_probes_asn_stop_iteration(mock_probe_request):
    mock = MagicMock()
    mock.total_count = 43
    mock_probe_request.return_value = mock

    # simulate the part with next() to throw an error
    mock.__next__.side_effect = StopIteration
    #test ipv4
    result = get_available_probes_asn("AS12347","ipv4")
    assert result == 0
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["asn"] == 12347
    assert kwargs["tags"] == "system-ipv4-works"
    assert kwargs["status"] == 1

    #test ipv6
    mock_probe_request.reset_mock()
    result = get_available_probes_asn("AS12340","ipv6")
    assert result == 0
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["asn"] == 12340
    assert kwargs["tags"] == "system-ipv6-works"
    assert kwargs["status"] == 1

@patch("server.app.utils.ripe_probes.ProbeRequest")
def test_get_available_probes_prefix(mock_probe_request):
    mock = MagicMock()
    mock.total_count = 50
    mock_probe_request.return_value = mock

    # simulate the part with next()
    mock.__iter__.return_value = iter([None])

    #test ipv4
    result = get_available_probes_prefix("80.211.224.0/20","ipv4")
    assert result == 50
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["prefix_v4"] == "80.211.224.0/20"
    assert kwargs["tags"] == "system-ipv4-works"
    assert kwargs["status"] == 1

    #test ipv6
    mock_probe_request.reset_mock()
    result = get_available_probes_prefix("2a06:93c0::/29","ipv6")
    assert result == 50
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["prefix_v6"] == "2a06:93c0::/29"
    assert kwargs["tags"] == "system-ipv6-works"
    assert kwargs["status"] == 1

@patch("server.app.utils.ripe_probes.ProbeRequest")
def test_get_available_probes_prefix_stop_iteration(mock_probe_request):
    mock = MagicMock()
    mock.total_count = 43
    mock_probe_request.return_value = mock

    # simulate the part with next() to throw an error
    mock.__next__.side_effect = StopIteration

    #test ipv4
    result = get_available_probes_prefix("80.211.224.0/20","ipv4")
    assert result == 0
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["prefix_v4"] == "80.211.224.0/20"
    assert kwargs["tags"] == "system-ipv4-works"
    assert kwargs["status"] == 1

    #test ipv6
    mock_probe_request.reset_mock()
    result = get_available_probes_prefix("2a06:93c0::/29","ipv6")
    assert result == 0
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["prefix_v6"] == "2a06:93c0::/29"
    assert kwargs["tags"] == "system-ipv6-works"
    assert kwargs["status"] == 1

@patch("server.app.utils.ripe_probes.ProbeRequest")
def test_get_available_probes_country(mock_probe_request):
    mock = MagicMock()
    mock.total_count = 65
    mock_probe_request.return_value = mock

    # simulate the part with next()
    mock.__iter__.return_value = iter([None])

    #test ipv4
    result = get_available_probes_country("NL","ipv4")
    assert result == 65
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["country_code"] == "NL"
    assert kwargs["tags"] == "system-ipv4-works"
    assert kwargs["status"] == 1

    #test ipv6
    mock_probe_request.reset_mock()
    result = get_available_probes_country("RO","ipv6")
    assert result == 65
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["country_code"] == "RO"
    assert kwargs["tags"] == "system-ipv6-works"
    assert kwargs["status"] == 1

@patch("server.app.utils.ripe_probes.ProbeRequest")
def test_get_available_probes_country_stop_iteration(mock_probe_request):
    mock = MagicMock()
    mock.total_count = 43
    mock_probe_request.return_value = mock

    # simulate the part with next() to throw an error
    mock.__next__.side_effect = StopIteration

    #test ipv4
    result = get_available_probes_country("NL","ipv4")
    assert result == 0
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["country_code"] =="NL"
    assert kwargs["tags"] == "system-ipv4-works"
    assert kwargs["status"] == 1

    #test ipv6
    mock_probe_request.reset_mock()
    result = get_available_probes_country("NL","ipv6")
    assert result == 0
    assert mock_probe_request.call_count==1
    args, kwargs = mock_probe_request.call_args
    assert kwargs["country_code"] == "NL"
    assert kwargs["tags"] == "system-ipv6-works"
    assert kwargs["status"] == 1

def test_take_from_available_probes():

    assert ([1,2,3,4,5],[1,2,3,4,6]) == take_from_available_probes(0,[1,2,3,4,5],[1,2,3,4,6])
    assert ([1.0,2.4,3.3,4.0,5.0],[1.1,2.2,3.3,4.4,5.5]) == take_from_available_probes(-1.0,[1.0,2.4,3.3,4.0,5.0],[1.1,2.2,3.3,4.4,5.5])
    # needed=3 -> take 2 from "prefix" type and 1 from "area"
    pb_available = [0,2,0,3,10]
    ans = [1,0,0,0,0]
    assert ([0,0,0,2,10],[1,2,0,1,0]) == take_from_available_probes(3,pb_available,ans)

    # needed=5 -> take 5 from "asn" type
    pb_available = [7, 2, 0, 3, 10]
    ans = [1, 0, 0, 0, 6]
    assert ([2, 2, 0, 3, 10], [6, 0, 0, 0, 6]) == take_from_available_probes(5, pb_available, ans)

    # needed=9 -> take 9 from "prefix", "country" and "area"
    pb_available = [0, 3.2, 4.01, 5, 10]
    ans = [1.1, 0, 0, 1, 6]
    expected_pb_available, expected_ans = ([0, 0, 0, 3.21, 10], [1.1, 3.2, 4.01, 2.79, 6])
    result_pb_available, result_ans = take_from_available_probes(9, pb_available, ans)
    for x, y in zip(expected_pb_available, result_pb_available):
        assert math.isclose(x, y, abs_tol=1e-6)
    for x, y in zip(expected_ans, ans):
        assert math.isclose(x, y, abs_tol=1e-6)


    # needed=900 -> take from everything, but it will throw an exception as we do not have a solution
    pb_available = [0, 3.3, 4.4, 5, 10]
    ans = [1.1, 0, 0, 1, 6]
    with pytest.raises(Exception):
        take_from_available_probes(900, pb_available, ans)