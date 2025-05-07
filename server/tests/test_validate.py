from server.app.utils.validate import is_ip_address


def test_validate():
    assert is_ip_address("1.2.3") is None
    assert is_ip_address("adfsdgh") is None
    assert is_ip_address("0.0.0.0.0.0") is None
    assert is_ip_address("123.45.67.89") == "ipv4"
    assert is_ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == "ipv6"
    assert is_ip_address("2001:db8:85a3::8a2e:370:7334") == "ipv6"
