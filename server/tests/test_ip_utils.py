from ipaddress import IPv4Address
from unittest.mock import patch, MagicMock
import pytest

from server.app.utils.ip_utils import ref_id_to_ip_or_name, get_ip_family, get_area_of_ip


def test_ref_id_to_ip_or_name():
    ip, name = ref_id_to_ip_or_name(1590075150, 2)
    assert ip == IPv4Address('94.198.159.14')
    assert name is None

    ip, name = ref_id_to_ip_or_name(1590075150, 2000)
    assert ip is None
    assert name is None

def test_get_ip_family():
    assert get_ip_family("189.24.80.23") == 4
    assert get_ip_family("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == 6
    with pytest.raises(Exception):
        get_ip_family("1sfefef23")



def test_get_area_of_ip():
    assert get_area_of_ip("NL",None) =="WW"
    assert get_area_of_ip("NL","EU") =="North-Central"
    assert get_area_of_ip("US","NA") =="West"
    assert get_area_of_ip("BR","SA") =="West"
    assert get_area_of_ip("ZA","AF") =="South-Central"
    # North-East
    assert get_area_of_ip("RU","AS") =="North-East"
    assert get_area_of_ip("KZ","AS") =="North-East"
    assert get_area_of_ip("MN","AS") =="North-East"
    # South-East
    assert get_area_of_ip("CN","AS") =="South-East"