import socket
from unittest.mock import patch, MagicMock
from server.app.utils.domain_name_to_ip import domain_name_to_ip_default, domain_name_to_ip_close_to_client
import dns.rdatatype


@patch("server.app.utils.domain_name_to_ip.socket.getaddrinfo")
def test_domain_name_to_ip_default_error(mock_getaddrinfo):
    # Mock socket.getaddrinfo
    mock_getaddrinfo.side_effect = socket.gaierror("Mocked error")
    # prepare the mock
    mock_ans = None
    result = domain_name_to_ip_default(domain_name="nl.pool.ntp.org")

    assert result == mock_ans

    result = domain_name_to_ip_default(domain_name=".pooegrhtrjr6jrjrj6jl.ntp.org")
    assert result is None


@patch("server.app.utils.domain_name_to_ip.socket.getaddrinfo")
def test_domain_name_to_ip_default_empty(mock_getaddrinfo):
    # Mock socket.getaddrinfo
    mock_getaddrinfo.return_value = []
    # prepare the mock
    mock_ans = []
    result = domain_name_to_ip_default(domain_name="nl.pool.ntp.org")

    assert result == mock_ans

@patch("server.app.utils.domain_name_to_ip.socket.getaddrinfo")
def test_domain_name_to_ip_default_one_ip(mock_getaddrinfo):
    # Mock socket.getaddrinfo
    mock_getaddrinfo.return_value = [(None, None, None, None, ("83.25.24.10", 0))]

    # prepare the mock
    mock_ans = ["83.25.24.10"]
    result = domain_name_to_ip_default(domain_name="it.pool.ntp.org")

    assert result == mock_ans

@patch("server.app.utils.domain_name_to_ip.socket.getaddrinfo")
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


def test_domain_name_to_ip_close_to_client_invalid_domain_name():
    result = domain_name_to_ip_close_to_client(domain_name="intp.org....",client_ip="83.25.24.10")

    assert result is None


@patch('dns.query.udp')
def test_domain_name_to_ip_close_to_client_normal_case(mock_udp):
    udp_mock_response_1 = MagicMock()
    udp_mock_response_1.answer = [
        MagicMock(items=[MagicMock(address='51.68.141.5'),
                         MagicMock(address='178.215.228.24'),
                         MagicMock(address='89.161.47.132'),
                         MagicMock(address='193.59.134.156')
                         ],rdtype=dns.rdatatype.A)
    ]
    udp_mock_response_2 = MagicMock()
    udp_mock_response_2.answer = [
        MagicMock(items=[MagicMock(address='164.92.156.55'),
                         MagicMock(address='87.251.32.230'),
                         MagicMock(address='149.143.87.82'),
                         MagicMock(address='178.239.19.62')
                         ],rdtype=dns.rdatatype.A)
    ]
    mock_udp.side_effect = [udp_mock_response_1, udp_mock_response_2]

    mock_ans=['51.68.141.5', '178.215.228.24', '89.161.47.132', '193.59.134.156']#, '164.92.156.55', '87.251.32.230', '149.143.87.82', '178.239.19.62']

    result = domain_name_to_ip_close_to_client(domain_name="pool.ntp.org",client_ip="83.25.24.10")
    assert set(result) == set(mock_ans)


@patch('dns.query.udp')
@patch('dns.query.tcp')
def test_domain_name_to_ip_close_to_client_udp_fails_tcp_saves(mock_udp,mock_tcp):
    udp_mock_response_2 = MagicMock()
    udp_mock_response_2.answer = [
        MagicMock(items=[MagicMock(address='51.68.141.5'),
                         MagicMock(address='178.215.228.24'),
                         MagicMock(address='89.161.47.132'),
                         MagicMock(address='193.59.134.156')
                         ],rdtype=dns.rdatatype.A)
    ]
    tcp_mock_response_1 = MagicMock()
    tcp_mock_response_1.answer = [
        MagicMock(items=[MagicMock(address='164.92.156.55'),
                         MagicMock(address='87.251.32.230'),
                         MagicMock(address='149.143.87.82'),
                         MagicMock(address='178.239.19.62')
                         ],rdtype=dns.rdatatype.A)
    ]
    mock_udp.side_effect = [Exception("UDP failed"), udp_mock_response_2]
    mock_tcp.side_effect = [tcp_mock_response_1]

    mock_ans=['164.92.156.55', '87.251.32.230', '149.143.87.82', '178.239.19.62']

    result = domain_name_to_ip_close_to_client(domain_name="pool.ntp.org",client_ip="83.25.24.10")
    assert set(result) == set(mock_ans)


@patch('dns.query.udp')
@patch('dns.query.tcp')
def test_domain_name_to_ip_close_to_client_udp_and_tcp_fail(mock_udp,mock_tcp):
    udp_mock_response_1 = MagicMock()
    udp_mock_response_1.answer = [
        MagicMock(items=[MagicMock(address='51.68.141.5'),
                         MagicMock(address='178.215.228.24'),
                         MagicMock(address='89.161.47.132'),
                         MagicMock(address='193.59.134.156')
                         ],rdtype=dns.rdatatype.A)
    ]
    mock_udp.side_effect = [udp_mock_response_1, Exception("UDP failed")]
    mock_tcp.side_effect = Exception("TCP failed")

    mock_ans=['51.68.141.5', '178.215.228.24', '89.161.47.132', '193.59.134.156']

    result = domain_name_to_ip_close_to_client(domain_name="pool.ntp.org",client_ip="83.25.24.10")
    assert set(result) == set(mock_ans)