from server.app.utils.ripe_probes import get_random_probes, get_area_probes, get_asn_probes, get_prefix_probes, \
    get_country_probes, get_best_probe_types, get_probes
from unittest.mock import patch, MagicMock


@patch("server.app.utils.ripe_probes.get_best_probe_types")
def test_get_probes_all_good(mock_get_best_probe_types):
    types: dict[str, int] = {
        "country": 1,
        "area": 10,
        "asn": 2,
        "prefix": 14,
        "random": 5
    }
    mock_get_best_probe_types.return_value = types

    probes_result= get_probes(ip_asn="AS15169", ip_prefix="162.159.200.0/24", ip_country="IT", ip_area="West")

    answer= [{'requested': 1, 'type': 'country', 'value': 'IT'},
             {'requested': 10, 'type': 'area', 'value': 'West'},
             {'requested': 2, 'type': 'asn', 'value': 'AS15169'},
             {'requested': 14, 'type': 'prefix', 'value': '162.159.200.0/24'},
             {'requested': 5, 'type': 'area', 'value': 'WW'}
    ]
    assert probes_result == answer
@patch("server.app.utils.ripe_probes.get_best_probe_types")
def test_get_probes_some_none(mock_get_best_probe_types):
    types: dict[str, int] = {
        "country": 1,
        "area": 0,
        "asn": 2,
        "prefix": 0,
        "random": 5
    }
    mock_get_best_probe_types.return_value = types

    probes_result= get_probes(ip_asn="AS15169", ip_prefix="None", ip_country="IT", ip_area="None")

    answer= [{'requested': 1, 'type': 'country', 'value': 'IT'},
             {'requested': 2, 'type': 'asn', 'value': 'AS15169'},
             {'requested': 5, 'type': 'area', 'value': 'WW'}
    ]
    assert probes_result == answer


def test_get_best_probe_types_all_none():
    result= get_best_probe_types(None,None,None,None,34)

    assert result["random"]==2
    assert "asn" not in result
    assert "prefix" not in result
    assert "country" not in result
    assert "area" not in result
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