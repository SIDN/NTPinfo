from datetime import datetime, timezone, timedelta

from integration_tests.db_fixture import *

def test_perform_measurement(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}
    end = datetime.now(timezone.utc)

    resp_get_before = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_before.json()["measurements"]) == 0
    cnt = 0
    response = client.post("/measurements/", json={"server": "91.210.128.220"},
                                headers=headers)
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        assert "measurement" in response.json()
        cnt = 1
    assert len(response.json()) == 1

    end = datetime.now(timezone.utc)
    resp_get_after = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_after.json()["measurements"]) == cnt

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
    assert response.status_code == 200 or response.status_code == 404
    assert len(response.json()) == 1
    if response.status_code == 200:
        assert "measurement" in response.json()
        assert len(response.json()["measurement"]) >= 1

def test_perform_multiple_measurements(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}
    end = datetime.now(timezone.utc)

    resp_get_before = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_before.json()["measurements"]) == 0
    cnt = 0
    for _ in range(3):
        response = client.post("/measurements/", json={"server": "91.210.128.220"},
                                headers=headers)
        assert response.status_code == 200 or response.status_code == 404
        if response.status_code == 200:
            cnt += 1
            assert "measurement" in response.json()
        assert len(response.json()) == 1

    end = datetime.now(timezone.utc)
    resp_get_after = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert resp_get_after.status_code == 200

    assert len(resp_get_after.json()["measurements"]) == cnt

def test_perform_multiple_measurement_rate_limiting(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}
    end = datetime.now(timezone.utc)

    resp_get_before = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    cnt = 0
    assert len(resp_get_before.json()["measurements"]) == 0
    for _ in range(5):
        response = client.post("/measurements/", json={"server": "91.210.128.220"},
                                headers=headers)
        assert response.status_code == 200 or response.status_code == 404
        if response.status_code == 200:
            cnt += 1
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
    assert len(resp_get_after.json()["measurements"]) == cnt

def test_perform_measurement_empty_server(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}

    response = client.post("/measurements/", json={"server": ""},
                                headers=headers)
    assert response.status_code == 400
    assert response.json() == {'error': "Either 'ip' or 'dn' must be provided"}

    end = datetime.now(timezone.utc)
    resp_get_after = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_after.json()["measurements"]) == 0

def test_perform_measurement_wrong_server(client):
    headers = {"X-Forwarded-For": "83.25.24.10"}

    response = client.post("/measurements/", json={"server": "random-server"},
                                headers=headers)
    assert response.status_code == 404
    assert "measurement" not in response.json()

    end = datetime.now(timezone.utc)
    resp_get_after = client.get("/measurements/history/", params={
        "server": "random-server",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert len(resp_get_after.json()["measurements"]) == 0

def test_read_historic_data_empty(client):
    end = datetime.now(timezone.utc)
    response = client.get("/measurements/history/", params={
        "server": "",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert response.status_code == 400
    assert "measurement" not in response.json()
    assert response.json() == {'error': "Either 'ip' or 'domain name' must be provided"}

def test_read_historic_data_wrong_start(client):
    end = datetime.now(timezone.utc)
    response = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end + timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert response.status_code == 400
    assert "measurement" not in response.json()
    assert response.json() == {'error': "'start' must be earlier than 'end'"}

def test_read_historic_data_wrong_end(client):
    end = datetime.now(timezone.utc) + timedelta(minutes=10)
    response = client.get("/measurements/history/", params={
        "server": "91.210.128.220",
        "start": (end - timedelta(minutes=10)).isoformat(),
        "end": end.isoformat()
    })
    assert response.status_code == 400
    assert "measurement" not in response.json()
    assert response.json() == {'error': "'end' cannot be in the future"}



