import pytest
from unittest.mock import patch, MagicMock

from server.app.utils.load_config_data import get_ipinfo_lite_api_token, get_ripe_account_email, get_ripe_api_token, \
    get_ntp_version, get_timeout_measurement_s, get_nr_of_measurements_for_jitter, get_mask_ipv4, get_mask_ipv6, \
    get_edns_default_servers, get_edns_timeout_s, get_ripe_timeout_per_probe_ms


@patch("server.app.utils.load_config_data.os.getenv")
def test_get_ipinfo_lite_api_token(mock):
    mock.return_value = "token"
    assert get_ipinfo_lite_api_token() == "token"
    mock.assert_called_with("IPINFO_LITE_API_TOKEN")

    # None -> Exception
    mock.return_value = None
    with pytest.raises(ValueError):
        get_ipinfo_lite_api_token()
    mock.assert_called_with("IPINFO_LITE_API_TOKEN")

@patch("server.app.utils.load_config_data.os.getenv")
def test_get_ripe_account_email(mock):
    mock.return_value = "email"
    assert get_ripe_account_email() == "email"
    mock.assert_called_with("ripe_account_email")

    # None -> Exception
    mock.return_value = None
    with pytest.raises(ValueError):
        get_ripe_account_email()
    mock.assert_called_with("ripe_account_email")

@patch("server.app.utils.load_config_data.os.getenv")
def test_get_ripe_api_token(mock):
    mock.return_value = "ripe token"
    assert get_ripe_api_token() == "ripe token"
    mock.assert_called_with("ripe_api_token")

    # None -> Exception
    mock.return_value = None
    with pytest.raises(ValueError):
        get_ripe_api_token()
    mock.assert_called_with("ripe_api_token")

# ntp version
@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ntp_version_ok(mock_config):
    mock_config["ntp"] = {"version": 5}
    assert get_ntp_version() == 5

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ntp_version_missing_section(mock_config):
    with pytest.raises(ValueError, match="ntp section is missing"):
        get_ntp_version()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ntp_version_missing_var(mock_config):
    mock_config["ntp"] = {"blabla": 5}
    with pytest.raises(ValueError, match="ntp 'version' is missing"):
        get_ntp_version()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ntp_version_different_type(mock_config):
    mock_config["ntp"] = {"version": "no"}
    with pytest.raises(ValueError, match="ntp 'version' must be an 'int'"):
        get_ntp_version()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ntp_version_boundaries(mock_config):
    mock_config["ntp"] = {"version": -1}
    with pytest.raises(ValueError, match="ntp 'version' must be > 0"):
        get_ntp_version()
    mock_config["ntp"] = {"version": 0}
    with pytest.raises(ValueError, match="ntp 'version' must be > 0"):
        get_ntp_version()
    mock_config["ntp"] = {"version": 1}
    assert get_ntp_version() == 1

# ntp timeout_measurement_s
@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_gget_timeout_measurement_s_ok(mock_config):
    mock_config["ntp"] = {"timeout_measurement_s": 5}
    assert get_timeout_measurement_s() == 5
    mock_config["ntp"] = {"timeout_measurement_s": 5.2}
    assert get_timeout_measurement_s() == 5.2

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_timeout_measurement_s_missing_section(mock_config):
    with pytest.raises(ValueError, match="ntp section is missing"):
        get_timeout_measurement_s()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_timeout_measurement_s_missing_var(mock_config):
    mock_config["ntp"] = {"blabla": 5.3}
    with pytest.raises(ValueError, match="ntp 'timeout_measurement_s' is missing"):
        get_timeout_measurement_s()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_timeout_measurement_s_different_type(mock_config):
    mock_config["ntp"] = {"timeout_measurement_s": "no"}
    with pytest.raises(ValueError, match="ntp 'timeout_measurement_s' must be a 'float' or an 'int'"):
        get_timeout_measurement_s()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_timeout_measurement_s_boundaries(mock_config):
    mock_config["ntp"] = {"timeout_measurement_s": -0.1}
    with pytest.raises(ValueError, match="ntp 'timeout_measurement_s' cannot be negative"):
        get_timeout_measurement_s()
    mock_config["ntp"] = {"timeout_measurement_s": 0}
    assert get_timeout_measurement_s() == 0

# ntp number_of_measurements_for_calculating_jitter
@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_nr_of_measurements_for_jitter_ok(mock_config):
    mock_config["ntp"] = {"number_of_measurements_for_calculating_jitter": 6}
    assert get_nr_of_measurements_for_jitter() == 6

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_nr_of_measurements_for_jitter_missing_section(mock_config):
    with pytest.raises(ValueError, match="ntp section is missing"):
        get_nr_of_measurements_for_jitter()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_nr_of_measurements_for_jitter_missing_var(mock_config):
    mock_config["ntp"] = {"blabla": 5}
    with pytest.raises(ValueError, match="ntp 'number_of_measurements_for_calculating_jitter' is missing"):
        get_nr_of_measurements_for_jitter()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_nr_of_measurements_for_jitter_different_type(mock_config):
    mock_config["ntp"] = {"number_of_measurements_for_calculating_jitter": 9.8}
    with pytest.raises(ValueError, match="ntp 'number_of_measurements_for_calculating_jitter' must be an 'int'"):
        get_nr_of_measurements_for_jitter()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_nr_of_measurements_for_jitter_boundaries(mock_config):
    mock_config["ntp"] = {"number_of_measurements_for_calculating_jitter": -1}
    with pytest.raises(ValueError, match="ntp 'number_of_measurements_for_calculating_jitter' must be > 0"):
        get_nr_of_measurements_for_jitter()
    mock_config["ntp"] = {"number_of_measurements_for_calculating_jitter": 0}
    with pytest.raises(ValueError, match="ntp 'number_of_measurements_for_calculating_jitter' must be > 0"):
        get_nr_of_measurements_for_jitter()
    mock_config["ntp"] = {"number_of_measurements_for_calculating_jitter": 1}
    assert get_nr_of_measurements_for_jitter() == 1


# edns mask_ipv4
@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv4_ok(mock_config):
    mock_config["edns"] = {"mask_ipv4": 6}
    assert get_mask_ipv4() == 6

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv4_missing_section(mock_config):
    with pytest.raises(ValueError, match="edns section is missing"):
        get_mask_ipv4()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv4_missing_var(mock_config):
    mock_config["edns"] = {"blabla": 5}
    with pytest.raises(ValueError, match="edns 'mask_ipv4' is missing"):
        get_mask_ipv4()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv4_different_type(mock_config):
    mock_config["edns"] = {"mask_ipv4": "no"}
    with pytest.raises(ValueError, match="edns 'mask_ipv4' must be an 'int'"):
        get_mask_ipv4()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv4_boundaries(mock_config):
    mock_config["edns"] = {"mask_ipv4": -1}
    with pytest.raises(ValueError, match="edns 'mask_ipv4' must be between 0 and 32 inclusive"):
        get_mask_ipv4()
    mock_config["edns"] = {"mask_ipv4": 33}
    with pytest.raises(ValueError, match="edns 'mask_ipv4' must be between 0 and 32 inclusive"):
        get_mask_ipv4()
    mock_config["edns"] = {"mask_ipv4": 0}
    assert get_mask_ipv4() == 0
    mock_config["edns"] = {"mask_ipv4": 32}
    assert get_mask_ipv4() == 32

# edns mask_ipv6
@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv6_ok(mock_config):
    mock_config["edns"] = {"mask_ipv6": 40}
    assert get_mask_ipv6() == 40

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv6_missing_section(mock_config):
    with pytest.raises(ValueError, match="edns section is missing"):
        get_mask_ipv6()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv6_missing_var(mock_config):
    mock_config["edns"] = {"blabla": 5}
    with pytest.raises(ValueError, match="edns 'mask_ipv6' is missing"):
        get_mask_ipv6()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv6_different_type(mock_config):
    mock_config["edns"] = {"mask_ipv6": "no"}
    with pytest.raises(ValueError, match="edns 'mask_ipv6' must be an 'int'"):
        get_mask_ipv6()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_mask_ipv6_boundaries(mock_config):
    mock_config["edns"] = {"mask_ipv6": -1}
    with pytest.raises(ValueError, match="edns 'mask_ipv6' must be between 0 and 64 inclusive"):
        get_mask_ipv6()
    mock_config["edns"] = {"mask_ipv6": 65}
    with pytest.raises(ValueError, match="edns 'mask_ipv6' must be between 0 and 64 inclusive"):
        get_mask_ipv6()
    mock_config["edns"] = {"mask_ipv6": 0}
    assert get_mask_ipv6() == 0
    mock_config["edns"] = {"mask_ipv6": 64}
    assert get_mask_ipv6() == 64

# edns edns_default_servers
@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_default_servers_ok(mock_config):
    mock_config["edns"] = {"default_order_of_edns_servers": ["2.2.2.2", "8.3.5.3"]}
    assert get_edns_default_servers() == ["2.2.2.2","8.3.5.3"]

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_default_servers_missing_section(mock_config):
    with pytest.raises(ValueError, match="edns section is missing"):
        get_edns_default_servers()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_default_servers_missing_var(mock_config):
    mock_config["edns"] = {"blabla": 5}
    with pytest.raises(ValueError, match="edns 'default_order_of_edns_servers' is missing"):
        get_edns_default_servers()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_default_servers_different_type(mock_config):
    mock_config["edns"] = {"default_order_of_edns_servers": "3.2.4.5"}
    with pytest.raises(ValueError, match="edns 'default_order_of_edns_servers' must be a 'list'"):
        get_edns_default_servers()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_default_servers_empty(mock_config):
    mock_config["edns"] = {"default_order_of_edns_servers": []}
    with pytest.raises(ValueError, match="edns 'default_order_of_edns_servers' cannot be empty"):
        get_edns_default_servers()

# edns edns_timeout_s
@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_timeout_s_ok(mock_config):
    mock_config["edns"] = {"edns_timeout_s": 3}
    assert get_edns_timeout_s() == 3
    mock_config["edns"] = {"edns_timeout_s": 3.09}
    assert get_edns_timeout_s() == 3.09

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_timeout_s_missing_section(mock_config):
    with pytest.raises(ValueError, match="edns section is missing"):
        get_edns_timeout_s()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_timeout_s_missing_var(mock_config):
    mock_config["edns"] = {"blabla": 5}
    with pytest.raises(ValueError, match="edns 'edns_timeout_s' is missing"):
        get_edns_timeout_s()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_timeout_s_different_type(mock_config):
    mock_config["edns"] = {"edns_timeout_s": "yes"}
    with pytest.raises(ValueError, match="edns 'edns_timeout_s' must be a 'float' or an 'int' in s"):
        get_edns_timeout_s()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_edns_timeout_s_boundaries(mock_config):
    mock_config["edns"] = {"edns_timeout_s": -2}
    with pytest.raises(ValueError, match="edns 'edns_timeout_s' cannot be negative"):
        get_edns_timeout_s()
    mock_config["edns"] = {"edns_timeout_s": 0}
    assert get_edns_timeout_s() == 0

# ripe_atlas timeout_per_probe_ms
@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ripe_timeout_per_probe_ms_ok(mock_config):
    mock_config["ripe_atlas"] = {"timeout_per_probe_ms": 300}
    assert get_ripe_timeout_per_probe_ms() == 300
    mock_config["ripe_atlas"] = {"timeout_per_probe_ms": 30.09}
    assert get_ripe_timeout_per_probe_ms() == 30.09

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ripe_timeout_per_probe_ms_missing_section(mock_config):
    with pytest.raises(ValueError, match="ripe_atlas section is missing"):
        get_ripe_timeout_per_probe_ms()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ripe_timeout_per_probe_ms_missing_var(mock_config):
    mock_config["ripe_atlas"] = {"blabla": 5}
    with pytest.raises(ValueError, match="ripe_atlas 'timeout_per_probe_ms' is missing"):
        get_ripe_timeout_per_probe_ms()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ripe_timeout_per_probe_ms_different_type(mock_config):
    mock_config["ripe_atlas"] = {"timeout_per_probe_ms": "yes"}
    with pytest.raises(ValueError, match="ripe_atlas 'timeout_per_probe_ms' must be a 'float' or an 'int' in ms"):
        get_ripe_timeout_per_probe_ms()

@patch("server.app.utils.load_config_data.config", new_callable=dict)
def test_get_ripe_timeout_per_probe_ms_boundaries(mock_config):
    mock_config["ripe_atlas"] = {"timeout_per_probe_ms": -0.1}
    with pytest.raises(ValueError, match="ripe_atlas 'timeout_per_probe_ms' must be > 0"):
        get_ripe_timeout_per_probe_ms()
    mock_config["ripe_atlas"] = {"timeout_per_probe_ms": 0}
    with pytest.raises(ValueError, match="ripe_atlas 'timeout_per_probe_ms' must be > 0"):
        get_ripe_timeout_per_probe_ms()
    mock_config["ripe_atlas"] = {"timeout_per_probe_ms": 0.2}
    assert get_ripe_timeout_per_probe_ms() == 0.2