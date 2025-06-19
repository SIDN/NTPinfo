import pytest
from fastapi.testclient import TestClient

from server.app.utils.validate import is_ip_address
from server.app.utils.domain_name_to_ip import domain_name_to_ip_close_to_client
from server.app.main import create_app


@pytest.fixture(scope="function")
def client():
    app = create_app(dev=False)
    app.state.limiter.reset()
    client = TestClient(app)
    yield client
    app.state.limiter.reset()

# test measurements from our server

def test_read_data_measurement_server_success(client):
    headers = {"X-Forwarded-For": "85.25.24.10"}
    response1 = client.post("/measurements/", json={"server": "time.apple.com", "ipv6_measurement": False},
                                headers=headers)
    response2 = client.post("/measurements/", json={"server": "time.apple.com", "ipv6_measurement": True},
                                headers=headers)
    # assert there was no problem from our back-end. We cannot directly check if it is 200 because
    # the NTP server could refuse to answer, or our server may not have both IPv4 or IPv6 addresses, or our
    # rate limiting should not block this test, as this IP was not used before.
    assert response1.status_code in {200, 400, 422}
    assert response2.status_code in {200, 400, 422}

def test_read_data_measurement_wrong_server(client):
    headers = {"X-Forwarded-For": "86.25.24.10"}

    response = client.post("/measurements/", json={"server": "random-server-name.orggg", "ipv6_measurement": False},
                                headers=headers)
    assert response.status_code == 422
    details = response.json()["detail"]
    assert (details == "Domain name is invalid or cannot be resolved." or "Our server cannot perform" in details)

    # want IPv6
    client.app.state.limiter.reset() # reset the rate limit
    response = client.post("/measurements/", json={"server": "random-server-name.orggg", "ipv6_measurement": True},
                           headers=headers)
    # depends on our server IP. It either fails because of this, or because the measurement failed
    # (because the domain name could not be resolved)
    assert response.status_code == 422
    details = response.json()["detail"]
    assert (details == "Domain name is invalid or cannot be resolved." or "Our server cannot perform" in details)

# test that querying the DNS works
def test_domain_name_to_dns(client):
    # we want ipv4
    result = domain_name_to_ip_close_to_client("time.google.com", "88.25.24.10", 4)
    assert result is not None
    # assert they are ipv4
    for ip in result:
        assert is_ip_address(ip) == "ipv4"

    # we want ipv6
    result = domain_name_to_ip_close_to_client("time.google.com", "88.25.24.10", 6)
    assert result is not None
    # assert they are ipv6
    for ip in result:
        assert is_ip_address(ip) == "ipv6"
