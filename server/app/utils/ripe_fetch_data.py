import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_data_from_ripe_measurement(measurement_id: str) -> list[dict]:
    url = f"https://atlas.ripe.net/api/v2/measurements/{measurement_id}/results/"

    headers = {
        "Authorization": f"Key {os.getenv('RIPE_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
    return response.json()


def parse_data_from_ripe_measurement(data: list[dict]):
    for measurement in data:
        print(measurement['dst_name'])


parse_data_from_ripe_measurement(get_data_from_ripe_measurement("105960562"))
