import socket
from unittest.mock import patch, MagicMock
import pytest
from server.app.utils.domain_name_to_ip import domain_name_to_ip_default, domain_name_to_ip_close_to_client, \
    edns_response_to_ips
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


def test_domain_name_to_ip_close_to_client_invalid_input():
    # invalid domain name
    result = domain_name_to_ip_close_to_client(domain_name="intp.org....", client_ip="83.25.24.10")
    assert result is None

    # invalid IP address
    with pytest.raises(Exception):
        domain_name_to_ip_close_to_client("time.google.com", "not an IP")


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



@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_close_to_client")
def test_edns_response_to_ips_only_ips(mock_domain_name):
    # answers with IPv4 (A)
    a_rrset = MagicMock()
    a_rrset.rdtype = dns.rdatatype.A
    a_rrset.items = [MagicMock(address="123.43.12.9"), MagicMock(address="124.11.13.19")]
    # answers with IPv4 (A)
    a_rrset2 = MagicMock()
    a_rrset2.rdtype = dns.rdatatype.A
    a_rrset2.items = [MagicMock(address="11.43.12.9")]

    # answers with IPv6 (AAAA)
    aaaa_rrset = MagicMock()
    aaaa_rrset.rdtype = dns.rdatatype.A
    aaaa_rrset.items = [MagicMock(address="123.143.10.9"), MagicMock(address="124.111.10.19")]
    # response
    mock_response = MagicMock()
    mock_response.answer = [a_rrset, aaaa_rrset, a_rrset2]

    result = edns_response_to_ips(mock_response, client_ip="83.25.24.10", resolvers=["8.8.8.8"])

    assert set(result) == {"123.43.12.9",
                      "124.11.13.19",
                      "123.143.10.9",
                      "124.111.10.19",
                      "11.43.12.9"}

@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_close_to_client")
def test_edns_response_to_ips_cname(mock_domain_name):
    mock_domain_name.return_value = ["33.44.56.78", "44.44.55.75", "2.2.2.2"]
    # answers with IPv4 (A)
    a_rrset = MagicMock()
    a_rrset.rdtype = dns.rdatatype.A
    a_rrset.items = [MagicMock(address="123.43.12.9"), MagicMock(address="124.11.13.19")]
    # answers with CNAME
    cname_rrset = MagicMock()
    cname_rrset.rdtype = dns.rdatatype.CNAME
    cname_item = MagicMock()
    cname_item.__str__.return_value = "redirected.example.com."
    cname_rrset.items = [cname_item]

    # response
    mock_response = MagicMock()
    mock_response.answer = [a_rrset, cname_rrset]

    result = edns_response_to_ips(mock_response, client_ip="83.25.24.10", resolvers=["8.8.8.8"])
    mock_domain_name.assert_called_with("redirected.example.com", "83.25.24.10",
                                        ["8.8.8.8"], 1, 2)
    assert set(result) == {"123.43.12.9",
                      "124.11.13.19",
                      "33.44.56.78",
                      "44.44.55.75",
                      "2.2.2.2"}

@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_close_to_client")
def test_edns_response_to_ips_cname_none(mock_domain_name):
    mock_domain_name.return_value = None
    # answers with IPv4 (A)
    a_rrset = MagicMock()
    a_rrset.rdtype = dns.rdatatype.A
    a_rrset.items = [MagicMock(address="123.43.12.9"), MagicMock(address="124.11.13.19")]
    # answers with CNAME
    cname_rrset = MagicMock()
    cname_rrset.rdtype = dns.rdatatype.CNAME
    cname_item = MagicMock()
    cname_item.__str__.return_value = "redirected.example.com."
    cname_rrset.items = [cname_item]

    # response
    mock_response = MagicMock()
    mock_response.answer = [a_rrset, cname_rrset]

    result = edns_response_to_ips(mock_response, client_ip="83.25.24.10", resolvers=["8.8.8.8"])
    mock_domain_name.assert_called_with("redirected.example.com", "83.25.24.10",
                                        ["8.8.8.8"], 1, 2)
    assert set(result) == {"123.43.12.9",
                      "124.11.13.19"}

@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_close_to_client")
def test_edns_response_to_ips_cname_too_large_depth(mock_domain_name):
    mock_domain_name.return_value = ["33.44.56.78", "44.44.55.75", "2.2.2.2"] # it should not arrive there because depth is max_depth
    # answers with IPv4 (A)
    a_rrset = MagicMock()
    a_rrset.rdtype = dns.rdatatype.A
    a_rrset.items = [MagicMock(address="123.43.12.9"), MagicMock(address="124.11.13.19")]
    # answers with CNAME
    cname_rrset = MagicMock()
    cname_rrset.rdtype = dns.rdatatype.CNAME
    cname_item = MagicMock()
    cname_item.__str__.return_value = "redirected.example.com."
    cname_rrset.items = [cname_item]

    # response
    mock_response = MagicMock()
    mock_response.answer = [a_rrset, cname_rrset]

    result = edns_response_to_ips(mock_response, client_ip="83.25.24.10", resolvers=["8.8.8.8"], depth=2, max_depth=2)
    mock_domain_name.assert_not_called()
    assert set(result) == {"123.43.12.9", "124.11.13.19"}