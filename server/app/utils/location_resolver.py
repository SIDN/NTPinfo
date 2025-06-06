import geoip2.database
from geoip2.errors import AddressNotFoundError, GeoIP2Error


def get_client_location(client_ip: str) -> tuple[float, float]:
    try:
        with geoip2.database.Reader('../../GeoLite2-City.mmdb') as reader:
            response = reader.city(client_ip)
            return response.location.latitude, response.location.longitude
    except (AddressNotFoundError, ValueError, GeoIP2Error, OSError) as e:
        print(e)
        return 25.0, -71.0
    except Exception as e:
        print(e)
        return 25.0, -71.0
