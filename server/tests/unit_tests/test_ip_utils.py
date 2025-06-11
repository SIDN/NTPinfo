from ipaddress import IPv4Address, IPv6Address
from unittest.mock import patch, MagicMock
import pytest

from server.app.utils.ip_utils import ref_id_to_ip_or_name, get_ip_family, get_area_of_ip, get_ip_network_details, \
    ip_to_str


def test_ip_to_str():
    assert ip_to_str(IPv4Address("123.45.67.89")) == "123.45.67.89"
    assert ip_to_str(IPv6Address("2001:db8:3333:4444:5555:6666:7777:8888")) == "2001:db8:3333:4444:5555:6666:7777:8888"
    assert ip_to_str(None) is None


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
    assert get_area_of_ip("NL", None) == "WW"
    assert get_area_of_ip("NL", "EU") == "North-Central"
    assert get_area_of_ip("US", "NA") == "West"
    assert get_area_of_ip("BR", "SA") == "West"
    assert get_area_of_ip("ZA", "AF") == "South-Central"
    # North-East
    assert get_area_of_ip("RU", "AS") == "North-East"
    assert get_area_of_ip("KZ", "AS") == "North-East"
    assert get_area_of_ip("MN", "AS") == "North-East"
    # South-East
    assert get_area_of_ip("CN", "AS") == "South-East"


@patch("server.app.utils.ip_utils.get_continent_for_ip")
@patch("server.app.utils.ip_utils.get_country_for_ip")
@patch("server.app.utils.ip_utils.get_asn_for_ip")
def test_get_ip_network_details_success(mock_get_asn, mock_get_country, mock_get_continent):
    mock_get_asn.return_value = "12345"
    mock_get_country.return_value = "NL"
    mock_get_continent.return_value = "EU"

    asn, country, area = get_ip_network_details("1.1.1.1")

    assert asn == "12345"
    assert country == "NL"
    assert area == "North-Central"


@patch("server.app.utils.ip_utils.get_continent_for_ip")
@patch("server.app.utils.ip_utils.get_country_for_ip")
@patch("server.app.utils.ip_utils.get_asn_for_ip")
def test_get_ip_network_details_exception(mock_get_asn, mock_get_country, mock_get_continent):
    mock_get_asn.side_effect = Exception("fail")
    mock_get_country.side_effect = Exception("fail")
    mock_get_continent.side_effect = Exception("fail")

    asn, country, area = get_ip_network_details("1.1.1.1")

    assert asn is None
    assert country is None
    assert area is None
