import socket
from unittest.mock import patch, MagicMock
import pytest

from server.app.models.CustomError import DNSError
from server.app.utils.domain_name_to_ip import domain_name_to_ip_default, domain_name_to_ip_close_to_client, \
    edns_response_to_ips, perform_edns_query, domain_name_to_ip_list
import dns.rdatatype


@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_close_to_client")
@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_default")
def test_domain_name_to_ip_list_normal(mock_dn_default, mock_dn_close):
    mock_dn_default.return_value = ["11.22.34.45", "13.22.34.46", "14.22.34.47"]
    mock_dn_close.return_value = ["71.22.34.45", "73.22.34.46", "74.22.34.47"]
    # test client ip none
    result = domain_name_to_ip_list("nl.pool.ntp.org", None, 4)
    assert set(result) == {"11.22.34.45", "13.22.34.46", "14.22.34.47"}
    mock_dn_default.assert_called_once()
    mock_dn_close.assert_not_called()

    mock_dn_default.reset_mock()
    mock_dn_close.reset_mock()
    result = domain_name_to_ip_list("nl.pool.ntp.org", "83.25.24.10", 4)
    assert set(result) == {"71.22.34.45", "73.22.34.46", "74.22.34.47"}
    mock_dn_default.assert_not_called()
    mock_dn_close.assert_called_once()


@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_close_to_client")
@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_default")
def test_domain_name_to_ip_list_normal_ipv6(mock_dn_default, mock_dn_close):
    mock_dn_default.return_value = ["2b06:93c0::25", "2c06:93c0::24", "2d06:93c0::24"]
    mock_dn_close.return_value = ["5b06:93c0::20", "8b06:93c0::20", "9b06:93c0::20"]
    # test client ip none
    result = domain_name_to_ip_list("nl.pool.ntp.org", None, 6)
    assert set(result) == {"2b06:93c0::25", "2c06:93c0::24", "2d06:93c0::24"}
    mock_dn_default.assert_called_once()
    mock_dn_close.assert_not_called()

    mock_dn_default.reset_mock()
    mock_dn_close.reset_mock()
    result = domain_name_to_ip_list("nl.pool.ntp.org", "1a06:13c0::24", 6)
    assert set(result) == {"5b06:93c0::20", "8b06:93c0::20", "9b06:93c0::20"}
    mock_dn_default.assert_not_called()
    mock_dn_close.assert_called_once()


@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_close_to_client")
@patch("server.app.utils.domain_name_to_ip.domain_name_to_ip_default")
def test_domain_name_to_ip_list_empty(mock_dn_default, mock_dn_close):
    mock_dn_default.return_value = []
    mock_dn_close.return_value = None
    #[]
    with pytest.raises(Exception):
        domain_name_to_ip_list("nl.pool.ntp.org", None, 4)
    mock_dn_default.assert_called_once()
    mock_dn_close.assert_not_called()

    #None
    mock_dn_default.reset_mock()
    mock_dn_close.reset_mock()
    with pytest.raises(DNSError):
        domain_name_to_ip_list("nl.pool.ntp.org", "74.22.34.47", 4)

    mock_dn_default.reset_mock()
    mock_dn_close.reset_mock()
    with pytest.raises(DNSError):
        domain_name_to_ip_list("nl.pool.ntp.org", "74.22.34.47", 6)
    mock_dn_default.assert_not_called()
    mock_dn_close.assert_called_once()


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
    result = domain_name_to_ip_close_to_client(domain_name="intp.org....", client_ip="83.25.24.10", wanted_ip_type=4)
    assert result is None

    # invalid IP address
    with pytest.raises(Exception):
        domain_name_to_ip_close_to_client("time.google.com", "not an IP", 4)


@patch("server.app.utils.domain_name_to_ip.dns.edns.ECSOption")
@patch("server.app.utils.domain_name_to_ip.edns_response_to_ips")
@patch("server.app.utils.domain_name_to_ip.perform_edns_query")
@patch("server.app.utils.domain_name_to_ip.get_mask_ipv6")
@patch("server.app.utils.domain_name_to_ip.get_mask_ipv4")
def test_domain_name_to_ip_close_to_client_first_resolver(mock_mask4, mock_mask6,
                                            mock_perform_edns_query, mock_edns_response_to_ips,
                                            mock_edns_option):
    mock_mask4.return_value = 24
    mock_mask6.return_value = 56
    mock_perform_edns_query.return_value = MagicMock()
    mock_edns_response_to_ips.return_value = ["1.2.5.78", "2.3.4.5"]
    mock_edns_option.return_value = MagicMock()
    # ipv4 wants ipv4
    result = domain_name_to_ip_close_to_client("nl.pool.ntp.org", "10.11.12.13", 4, ["8.8.8.8", "1.1.1.1"])
    assert set(result) == {"1.2.5.78", "2.3.4.5"}
    mock_perform_edns_query.assert_called_once()
    mock_edns_response_to_ips.assert_called_once()
    mock_edns_option.assert_called_once_with(address="10.11.12.13", srclen=24, scopelen=0)
    # ipv6 wants ipv6
    mock_perform_edns_query.reset_mock()
    mock_edns_response_to_ips.reset_mock()
    mock_edns_option.reset_mock()
    mock_edns_response_to_ips.return_value = ["2a06:93c0::2f", "2b06:93c0::2f"]
    result = domain_name_to_ip_close_to_client("nl.pool.ntp.org", "2a06:93c0::21", 6, ["8.8.8.8", "1.1.1.1"])
    assert set(result) == {"2a06:93c0::2f", "2b06:93c0::2f"}
    mock_perform_edns_query.assert_called_once()
    mock_edns_response_to_ips.assert_called_once()
    mock_edns_option.assert_called_once_with(address="2a06:93c0::21", srclen=56, scopelen=0)


@patch("server.app.utils.domain_name_to_ip.dns.edns.ECSOption")
@patch("server.app.utils.domain_name_to_ip.edns_response_to_ips")
@patch("server.app.utils.domain_name_to_ip.perform_edns_query")
@patch("server.app.utils.domain_name_to_ip.get_mask_ipv6")
@patch("server.app.utils.domain_name_to_ip.get_mask_ipv4")
def test_domain_name_to_ip_close_to_client_ipv4_wants_ipv6_and_reverse(mock_mask4, mock_mask6,
                                            mock_perform_edns_query, mock_edns_response_to_ips,
                                            mock_edns_option):
    mock_mask4.return_value = 24
    mock_mask6.return_value = 56
    mock_perform_edns_query.return_value = MagicMock()
    mock_edns_response_to_ips.return_value = ["1.2.5.78", "2.3.4.5"]
    mock_edns_option.return_value = MagicMock()
    # ipv6 wants ipv4
    result = domain_name_to_ip_close_to_client("nl.pool.ntp.org", "2a06:93c0::24", 4, ["8.8.8.8", "1.1.1.1"])
    assert set(result) == {"1.2.5.78", "2.3.4.5"}
    mock_perform_edns_query.assert_called_once()
    mock_edns_response_to_ips.assert_called_once()
    mock_edns_option.assert_called_once_with(address="2a06:93c0::24", srclen=56, scopelen=0)
    # ipv6 wants ipv6
    mock_perform_edns_query.reset_mock()
    mock_edns_response_to_ips.reset_mock()
    mock_edns_option.reset_mock()
    mock_edns_response_to_ips.return_value = ["2a06:93c0::2f", "2b06:93c0::2f"]
    result = domain_name_to_ip_close_to_client("nl.pool.ntp.org", "2.3.4.5", 4, ["8.8.8.8", "1.1.1.1"])
    assert set(result) == {"2a06:93c0::2f", "2b06:93c0::2f"}
    mock_perform_edns_query.assert_called_once()
    mock_edns_response_to_ips.assert_called_once()
    mock_edns_option.assert_called_once_with(address="2.3.4.5", srclen=24, scopelen=0)


@patch("server.app.utils.domain_name_to_ip.dns.edns.ECSOption")
@patch("server.app.utils.domain_name_to_ip.edns_response_to_ips")
@patch("server.app.utils.domain_name_to_ip.perform_edns_query")
@patch("server.app.utils.domain_name_to_ip.get_mask_ipv6")
@patch("server.app.utils.domain_name_to_ip.get_mask_ipv4")
def test_domain_name_to_ip_close_to_client_none_exception(mock_mask4, mock_mask6,
                                            mock_perform_edns_query, mock_edns_response_to_ips,
                                            mock_edns_option):
    mock_mask4.return_value = 24
    mock_mask6.return_value = 56
    mock_perform_edns_query.side_effect  = [None, MagicMock()]
    mock_edns_response_to_ips.return_value = ["1.2.5.78", "2.3.4.5"]
    mock_edns_option.return_value = MagicMock()
    # ipv4 with perform_edns_query returning None the first time and a list of IPs second time
    result = domain_name_to_ip_close_to_client("nl.pool.ntp.org", "10.11.12.13", 4, ["8.8.8.8", "1.1.1.1"])
    assert set(result) == {"1.2.5.78", "2.3.4.5"}
    assert mock_perform_edns_query.call_count == 2
    assert mock_edns_option.call_count == 1
    assert mock_edns_response_to_ips.call_count == 1
    #ipv6 -> try to throw an exception
    mock_perform_edns_query.reset_mock()
    mock_edns_response_to_ips.reset_mock()
    mock_edns_option.reset_mock()
    mock_perform_edns_query.side_effect = Exception("exception")
    mock_edns_response_to_ips.return_value = ["1.2.5.78", "2.3.4.5"]
    mock_edns_option.return_value = MagicMock()

    result = domain_name_to_ip_close_to_client("nl.pool.ntp.org", "2a06:93c0::2f", 6,["8.8.8.8", "1.1.1.1"])
    assert result is None
    assert mock_perform_edns_query.call_count == 1
    assert mock_edns_option.call_count == 1
    assert mock_edns_response_to_ips.call_count == 0

@patch("server.app.utils.domain_name_to_ip.dns.query.tcp")
@patch("server.app.utils.domain_name_to_ip.dns.query.udp")
def test_perform_edns_query_udp_succeeds(mock_udp, mock_tcp):
    # tcp response
    mock_response = MagicMock()
    ecs4 = dns.edns.ECSOption(address="1.2.3.4", srclen=24)
    ecs6 = dns.edns.ECSOption(address="2a06:93c0::2f", srclen=56)
    # udp succeeds, tcp not called
    mock_udp.return_value = mock_response

    result = perform_edns_query("pool.ntp.org", "8.8.8.8", ecs4, 4, 3)
    assert result is mock_response
    mock_udp.assert_called_once()
    mock_tcp.assert_not_called()

    # ip v6
    mock_response.reset_mock()
    mock_udp.reset_mock()
    mock_tcp.reset_mock()
    result = perform_edns_query("pool.ntp.org", "8.8.8.8", ecs6, 6, 3)
    assert result is mock_response
    mock_udp.assert_called_once()
    mock_tcp.assert_not_called()

@patch("server.app.utils.domain_name_to_ip.dns.query.tcp")
@patch("server.app.utils.domain_name_to_ip.dns.query.udp")
def test_perform_edns_query_udp_fails_tcp_saves(mock_udp, mock_tcp):
    # tcp response
    mock_response = MagicMock()
    ecs4 = dns.edns.ECSOption(address="1.2.3.4", srclen=24)
    ecs6 = dns.edns.ECSOption(address="2a06:93c0::2f", srclen=56)
    # udp fails, tcp succeeds
    mock_udp.side_effect = Exception("UDP failed")
    mock_tcp.return_value = mock_response

    result = perform_edns_query("pool.ntp.org", "8.8.8.8", ecs4, 4, 3)
    assert result is mock_response
    # how udp request was sent
    mock_udp.assert_called_once()
    query_sent = mock_udp.call_args[0][0]
    # get the ecs option from all the fields it has
    ecs_option = next((opt for opt in query_sent.options if isinstance(opt, dns.edns.ECSOption)), None)
    assert ecs_option is not None
    assert ecs_option.address == "1.2.3.4"
    assert ecs_option.srclen == 24
    # how tcp request was sent
    mock_tcp.assert_called_once()
    query_sent = mock_tcp.call_args[0][0]
    # get the ecs option from all the fields it has
    ecs_option = next((opt for opt in query_sent.options if isinstance(opt, dns.edns.ECSOption)), None)
    assert ecs_option is not None
    assert ecs_option.address == "1.2.3.4"
    assert ecs_option.srclen == 24
    assert any(q.rdtype == dns.rdatatype.A for q in query_sent.question)

    # ip v6
    mock_response.reset_mock()
    mock_udp.reset_mock()
    mock_tcp.reset_mock()
    result = perform_edns_query("pool.ntp.org", "8.8.8.8", ecs6, 6, 3)
    assert result is mock_response
    # how udp request was sent
    mock_udp.assert_called_once()
    query_sent = mock_udp.call_args[0][0]
    # get the ecs option from all the fields it has
    ecs_option = next((opt for opt in query_sent.options if isinstance(opt, dns.edns.ECSOption)), None)
    assert ecs_option is not None
    assert ecs_option.address == "2a06:93c0::2f"
    assert ecs_option.srclen == 56
    # how tcp request was sent
    mock_tcp.assert_called_once()
    query_sent = mock_tcp.call_args[0][0]
    # get the ecs option from all the fields it has
    ecs_option = next((opt for opt in query_sent.options if isinstance(opt, dns.edns.ECSOption)), None)
    assert ecs_option is not None
    assert ecs_option.address == "2a06:93c0::2f"
    assert ecs_option.srclen == 56
    assert any(q.rdtype == dns.rdatatype.AAAA for q in query_sent.question)

@patch("server.app.utils.domain_name_to_ip.dns.query.tcp")
@patch("server.app.utils.domain_name_to_ip.dns.query.udp")
def test_perform_edns_query_udp_and_tcp_fail(mock_udp, mock_tcp):
    ecs4 = dns.edns.ECSOption(address="1.2.3.4", srclen=24)
    ecs6 = dns.edns.ECSOption(address="2a06:93c0::2f", srclen=56)
    #udp and tcp both fails
    mock_udp.side_effect = Exception("UDP failed")
    mock_tcp.side_effect = Exception("TCP failed")

    result = perform_edns_query("pool.ntp.org", "8.8.8.8", ecs4, 4, 3)
    assert result is None
    # how udp request was sent
    mock_udp.assert_called_once()
    query_sent = mock_udp.call_args[0][0]
    # get the ecs option from all the fields it has
    ecs_option = next((opt for opt in query_sent.options if isinstance(opt, dns.edns.ECSOption)), None)
    assert ecs_option is not None
    assert ecs_option.address == "1.2.3.4"
    assert ecs_option.srclen == 24
    # how tcp request was sent
    mock_tcp.assert_called_once()
    query_sent = mock_tcp.call_args[0][0]
    # get the ecs option from all the fields it has
    ecs_option = next((opt for opt in query_sent.options if isinstance(opt, dns.edns.ECSOption)), None)
    assert ecs_option is not None
    assert ecs_option.address == "1.2.3.4"
    assert ecs_option.srclen == 24
    assert any(q.rdtype == dns.rdatatype.A for q in query_sent.question)

    # ip v6
    mock_udp.reset_mock()
    mock_tcp.reset_mock()
    result = perform_edns_query("pool.ntp.org", "8.8.8.8", ecs6, 6, 3)
    assert result is None
    # how udp request was sent
    mock_udp.assert_called_once()
    query_sent = mock_udp.call_args[0][0]
    # get the ecs option from all the fields it has
    ecs_option = next((opt for opt in query_sent.options if isinstance(opt, dns.edns.ECSOption)), None)
    assert ecs_option is not None
    assert ecs_option.address == "2a06:93c0::2f"
    assert ecs_option.srclen == 56
    # how tcp request was sent
    mock_tcp.assert_called_once()
    query_sent = mock_tcp.call_args[0][0]
    # get the ecs option from all the fields it has
    ecs_option = next((opt for opt in query_sent.options if isinstance(opt, dns.edns.ECSOption)), None)
    assert ecs_option is not None
    assert ecs_option.address == "2a06:93c0::2f"
    assert ecs_option.srclen == 56
    assert any(q.rdtype == dns.rdatatype.AAAA for q in query_sent.question)


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
    aaaa_rrset.rdtype = dns.rdatatype.AAAA
    aaaa_rrset.items = [MagicMock(address="2a06:93c0::24"), MagicMock(address="2a36:93c0::24")]
    # response
    mock_response = MagicMock()
    mock_response.answer = [a_rrset, aaaa_rrset, a_rrset2]

    result = edns_response_to_ips(mock_response, client_ip="83.25.24.10", wanted_ip_type=4, resolvers=["8.8.8.8"])

    assert set(result) == {"123.43.12.9",
                      "124.11.13.19",
                      "11.43.12.9",
                      "2a06:93c0::24",
                      "2a36:93c0::24"}

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

    result = edns_response_to_ips(mock_response, client_ip="83.25.24.10", wanted_ip_type=4, resolvers=["8.8.8.8"])
    mock_domain_name.assert_called_with("redirected.example.com", "83.25.24.10", 4, ["8.8.8.8"], 1, 2)
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

    result = edns_response_to_ips(mock_response, client_ip="83.25.24.10", wanted_ip_type=4, resolvers=["8.8.8.8"])
    mock_domain_name.assert_called_with("redirected.example.com", "83.25.24.10", 4, ["8.8.8.8"], 1, 2)
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

    result = edns_response_to_ips(mock_response, client_ip="83.25.24.10", wanted_ip_type=4, resolvers=["8.8.8.8"], depth=2, max_depth=2)
    mock_domain_name.assert_not_called()
    assert set(result) == {"123.43.12.9", "124.11.13.19"}