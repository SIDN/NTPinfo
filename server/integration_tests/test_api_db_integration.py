from datetime import datetime, timezone, timedelta

from server.app.models.Measurement import Measurement
from server.integration_tests.db_fixture import *

def test_perform_measurement(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}
    end = datetime.now(timezone.utc)

    resp_get_before = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_before.json()["measurements"]) == 0

    response = client.post("/measurements/", json={"server": "91.210.128.220"},
                                headers=headers)
    assert response.status_code == 200
    assert "measurement" in response.json()
    assert len(response.json()) == 1

    end = datetime.now(timezone.utc)
    resp_get_after = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_after.json()["measurements"]) == 1

def test_perform_measurement_dn(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}
    end = datetime.now(timezone.utc)

    resp_get_before = client.get("/measurements/history/", params={
        "server": "time.apple.com",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_before.json()["measurements"]) == 0

    response = client.post("/measurements/", json={"server": "time.apple.com"},
                                headers=headers)
    assert response.status_code == 200
    assert "measurement" in response.json()
    assert len(response.json()) == 1

    end = datetime.now(timezone.utc)
    resp_get_after = client.get("/measurements/history/", params={
        "server": "time.apple.com",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    length = len(resp_get_after.json()["measurements"])
    assert 3 <= length <= 7


def test_perform_multiple_measurements(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}
    end = datetime.now(timezone.utc)

    resp_get_before = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_before.json()["measurements"]) == 0

    for _ in range(3):
        response = client.post("/measurements/", json={"server": "91.210.128.220"},
                                headers=headers)
        assert response.status_code == 200
        assert "measurement" in response.json()
        assert len(response.json()) == 1

    end = datetime.now(timezone.utc)
    resp_get_after = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert resp_get_after.status_code == 200

    assert len(resp_get_after.json()["measurements"]) == 3

def test_perform_multiple_measurement_rate_limiting(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}
    end = datetime.now(timezone.utc)

    resp_get_before = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_before.json()["measurements"]) == 0
    for _ in range(5):
        response = client.post("/measurements/", json={"server": "91.210.128.220"},
                                headers=headers)
        assert response.status_code == 200
        assert "measurement" in response.json()
        assert len(response.json()) == 1

    response = client.post("/measurements/", json={"server": "91.210.128.220"},
                           headers=headers)
    assert response.status_code == 429

    end = datetime.now(timezone.utc)
    resp_get_after = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert resp_get_after.status_code == 200
    assert len(resp_get_after.json()["measurements"]) == 5


