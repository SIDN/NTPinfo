
import socket
from unittest.mock import patch, MagicMock

from app.utils.domain_name_to_ip import domain_name_to_ip_default

@patch("server.app.utils.perform_measurements.socket.getaddrinfo")
def test_domain_name_to_ip_default_error(mock_getaddrinfo):
    # Mock socket.getaddrinfo
    mock_getaddrinfo.side_effect = socket.gaierror("Mocked error")
    # prepare the mock
    mock_ans = None
    result = domain_name_to_ip_default(domain_name="nl.pool.ntp.org")

    assert result == mock_ans

    result = domain_name_to_ip_default(domain_name=".pooegrhtrjr6jrjrj6jl.ntp.org")
    assert result is None


@patch("server.app.utils.perform_measurements.socket.getaddrinfo")
def test_domain_name_to_ip_default_empty(mock_getaddrinfo):
    # Mock socket.getaddrinfo
    mock_getaddrinfo.return_value = []
    # prepare the mock
    mock_ans = []
    result = domain_name_to_ip_default(domain_name="nl.pool.ntp.org")

    assert result == mock_ans

@patch("server.app.utils.perform_measurements.socket.getaddrinfo")
def test_domain_name_to_ip_default_one_ip(mock_getaddrinfo):
    # Mock socket.getaddrinfo
    mock_getaddrinfo.return_value = [(None, None, None, None, ("83.25.24.10", 0))]

    # prepare the mock
    mock_ans = ["83.25.24.10"]
    result = domain_name_to_ip_default(domain_name="it.pool.ntp.org")

    assert result == mock_ans

@patch("server.app.utils.perform_measurements.socket.getaddrinfo")
def test_domain_name_to_ip_default_more_ips(mock_getaddrinfo):
    # Mock socket.getaddrinfo
    mock_getaddrinfo.return_value = [
        (None, None, None, None, ("83.25.24.10", 0)),
        (None, None, None, None, ("83.25.24.13", 0)),
        (None, None, None, None, ("83.25.25.10", 0)),
        (None, None, None, None, ("86.25.24.10", 0))
    ]
    # prepare the mock
    mock_ans = sorted({"83.25.24.10", "83.25.24.13", "83.25.25.10", "86.25.24.10"})
    result = domain_name_to_ip_default(domain_name="ro.pool.ntp.org")

    assert result == mock_ans