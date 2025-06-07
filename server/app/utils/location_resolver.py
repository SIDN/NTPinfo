import geoip2.database
from geoip2.errors import AddressNotFoundError, GeoIP2Error

from server.app.utils.load_config_data import get_max_mind_path


def get_client_location(client_ip: str) -> tuple[float, float]:
    try:
        with geoip2.database.Reader(f'{get_max_mind_path()}') as reader:
            response = reader.city(client_ip)
            return response.location.latitude, response.location.longitude
    except (AddressNotFoundError, ValueError, GeoIP2Error, OSError) as e:
        print(e)
        return 25.0, -71.0
    except Exception as e:
        print(e)
        return 25.0, -71.0
