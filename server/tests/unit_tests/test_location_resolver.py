from unittest.mock import patch, Mock

from server.app.utils.location_resolver import get_coordinates_for_ip
from geoip2.errors import AddressNotFoundError, GeoIP2Error


@patch("server.app.utils.location_resolver.geoip2.database.Reader")
def test_valid_ip_returns_coordinates(mock_reader):
    mock_response = Mock()
    mock_response.location.latitude = 1.23
    mock_response.location.longitude = -1.22
    mock_reader.return_value.__enter__.return_value.city.return_value = mock_response

    coords = get_coordinates_for_ip("0.0.0.0")
    assert coords == (1.23, -1.22)


@patch("server.app.utils.location_resolver.geoip2.database.Reader")
def test_ip_not_found_returns_fallback(mock_reader):
    mock_reader.return_value.__enter__.return_value.city.side_effect = AddressNotFoundError("Not found")

    coords = get_coordinates_for_ip("0.0.0.0")
    assert coords == (25.0, -71.0)


@patch("server.app.utils.location_resolver.geoip2.database.Reader")
def test_none_location_fields_return_fallback(mock_reader):
    mock_response = Mock()
    mock_response.location.latitude = None
    mock_response.location.longitude = -10.0
    mock_reader.return_value.__enter__.return_value.city.return_value = mock_response

    coords = get_coordinates_for_ip("0.0.0.0")
    assert coords == (25.0, -71.0)


@patch("server.app.utils.location_resolver.geoip2.database.Reader")
def test_geoip2_error_returns_fallback(mock_reader):
    mock_reader.side_effect = GeoIP2Error("Database corrupted")

    coords = get_coordinates_for_ip("0.0.0.0")
    assert coords == (25.0, -71.0)


@patch("server.app.utils.location_resolver.geoip2.database.Reader")
def test_file_not_found_returns_fallback(mock_reader):
    mock_reader.side_effect = OSError("File not found")

    coords = get_coordinates_for_ip("0.0.0.0")
    assert coords == (25.0, -71.0)


@patch("server.app.utils.location_resolver.geoip2.database.Reader")
def test_other_exception_returns_fallback(mock_reader):
    mock_reader.side_effect = Exception("Other exception")

    coords = get_coordinates_for_ip("0.0.0.0")
    assert coords == (25.0, -71.0)
