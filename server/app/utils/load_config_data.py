import math
import os
from typing import Any, cast
import yaml
from dotenv import load_dotenv


def load_config() -> dict[str, Any]:
    """
    It loads the config from a YAML file.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "..", "server_config.yaml")
    config_path = os.path.abspath(config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as f:
        return cast(dict[str, Any], yaml.safe_load(f))

load_dotenv()
config = load_config()

def verify_if_config_is_set() -> bool:
    """
    This method ensures that the config file has all the required variables, and they are all correctly set. (the same data type)
    It will return true if everything is fine, else it will rise an exception,

    Raises:
        ValueError: If the config file does not have all the required variables or some of them are invalid.
    """
    # verify from .env (the secrets)
    get_ipinfo_lite_api_token()
    get_ripe_account_email()
    get_ripe_api_token()

    # from config
    get_ntp_version()
    get_timeout_measurement_s()
    get_nr_of_measurements_for_jitter()
    get_mask_ipv4()
    get_mask_ipv6()
    get_edns_default_servers()
    get_edns_timeout_s()
    get_ripe_timeout_per_probe_ms()
    get_ripe_packets_per_probe()
    get_ripe_number_of_probes_per_measurement()
    # everything is fine
    return True

def get_ipinfo_lite_api_token() -> str:
    """
    This function returns the IPinfo Lite API token.

    Raises:
        ValueError: If no IPinfo Lite API token is found.
    """
    ans =  os.getenv('IPINFO_LITE_API_TOKEN')
    if ans is not None:
        return ans
    raise ValueError('IPINFO_LITE_API_TOKEN environment variable not set')

def get_ripe_account_email() -> str:
    """
    This function returns the RIPE Atlas account email. (one that has enough credits)

    Raises:
        ValueError: If the RIPE Atlas account email is not set.
    """
    ans = os.getenv('ripe_account_email')
    if ans is not None:
        return ans
    raise ValueError('ripe_account_email environment variable is not set')

def get_ripe_api_token() -> str:
    """
    This function returns the RIPE Atlas API token.

    Raises:
        ValueError: If the RIPE Atlas API token is not set.
    """
    ans =  os.getenv('ripe_api_token')
    if ans is not None:
        return ans
    raise ValueError('ripe_api_token environment variable not set')

def get_ntp_version() -> int:
    """
    This method returns the ntp version that we use in measurements.

    Raises:
        ValueError: If the ntp version has not been correctly set.
    """
    if "ntp" not in config:
        raise ValueError("ntp section is missing")
    ntp = config["ntp"]
    if "version" not in ntp:
        raise ValueError("ntp 'version' is missing")
    if not isinstance(ntp["version"], int):
        raise ValueError("ntp 'version' must be an 'int'")
    if ntp["version"] <= 0:
        raise ValueError("ntp 'version' must be > 0")
    return ntp["version"]

def get_timeout_measurement_s() -> float | int:
    """
    This method returns the timeout for an NTP measurement.

    Raises:
        ValueError: If the ntp version has not been correctly set.
    """
    if "ntp" not in config:
        raise ValueError("ntp section is missing")
    ntp = config["ntp"]
    if "timeout_measurement_s" not in ntp:
        raise ValueError("ntp 'timeout_measurement_s' is missing")
    if not isinstance(ntp["timeout_measurement_s"], float | int):
        raise ValueError("ntp 'timeout_measurement_s' must be a 'float' or an 'int'")
    if ntp["timeout_measurement_s"] < 0:
        raise ValueError("ntp 'timeout_measurement_s' cannot be negative")
    return ntp["timeout_measurement_s"]

def get_nr_of_measurements_for_jitter() -> int:
    """
    This method returns the number of measurement requested for calculating the jitter.

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "ntp" not in config:
        raise ValueError("ntp section is missing")
    ntp = config["ntp"]
    if "number_of_measurements_for_calculating_jitter" not in ntp:
        raise ValueError("ntp 'number_of_measurements_for_calculating_jitter' is missing")
    if not isinstance(ntp["number_of_measurements_for_calculating_jitter"], int):
        raise ValueError("ntp 'number_of_measurements_for_calculating_jitter' must be an 'int'")
    if ntp["number_of_measurements_for_calculating_jitter"] <= 0:
        raise ValueError("ntp 'number_of_measurements_for_calculating_jitter' must be > 0")
    return ntp["number_of_measurements_for_calculating_jitter"]

def get_mask_ipv4() -> int:
    """
    This method returns the mask we use for ipv4 IPs.

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "edns" not in config:
        raise ValueError("edns section is missing")
    edns = config["edns"]
    if "mask_ipv4" not in edns:
        raise ValueError("edns 'mask_ipv4' is missing")
    if not isinstance(edns["mask_ipv4"], int):
        raise ValueError("edns 'mask_ipv4' must be an 'int'")
    if edns["mask_ipv4"] < 0 or edns["mask_ipv4"] > 32:
        raise ValueError("edns 'mask_ipv4' must be between 0 and 32 inclusive")
    return edns["mask_ipv4"]


def get_mask_ipv6() -> int:
    """
    This method returns the mask we use for ipv6 IPs.

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "edns" not in config:
        raise ValueError("edns section is missing")
    edns = config["edns"]
    if "mask_ipv6" not in edns:
        raise ValueError("edns 'mask_ipv6' is missing")
    if not isinstance(edns["mask_ipv6"], int):
        raise ValueError("edns 'mask_ipv6' must be an 'int'")
    if edns["mask_ipv6"] < 0 or edns["mask_ipv6"] > 64:
        raise ValueError("edns 'mask_ipv6' must be between 0 and 64 inclusive")
    return edns["mask_ipv6"]

def get_edns_default_servers() -> list[str]:
    """
    This method returns the default list of EDNS servers. (in the order of their priorities)

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "edns" not in config:
        raise ValueError("edns section is missing")
    edns = config["edns"]
    if "default_order_of_edns_servers" not in edns:
        raise ValueError("edns 'default_order_of_edns_servers' is missing")
    if not isinstance(edns["default_order_of_edns_servers"], list):
        raise ValueError("edns 'default_order_of_edns_servers' must be a 'list'")
    if len(edns["default_order_of_edns_servers"]) == 0:
        raise ValueError("edns 'default_order_of_edns_servers' cannot be empty")
    return edns["default_order_of_edns_servers"]

def get_edns_timeout_s() -> float|int:
    """
    This method returns the timeout for the EDNS query request.

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "edns" not in config:
        raise ValueError("edns section is missing")
    edns = config["edns"]
    if "edns_timeout_s" not in edns:
        raise ValueError("edns 'edns_timeout_s' is missing")
    if not isinstance(edns["edns_timeout_s"], float | int):
        raise ValueError("edns 'edns_timeout_s' must be a 'float' or an 'int' in s")
    if edns["edns_timeout_s"] < 0:
        raise ValueError("edns 'edns_timeout_s' cannot be negative")
    return edns["edns_timeout_s"]

def get_ripe_timeout_per_probe_ms() -> float|int:
    """
    This method returns the timeout that a probe has to receive an answer from a measurement.

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "ripe_atlas" not in config:
        raise ValueError("ripe_atlas section is missing")
    ripe_atlas = config["ripe_atlas"]
    if "timeout_per_probe_ms" not in ripe_atlas:
        raise ValueError("ripe_atlas 'timeout_per_probe_ms' is missing")
    if not isinstance(ripe_atlas["timeout_per_probe_ms"], float|int):
        raise ValueError("ripe_atlas 'timeout_per_probe_ms' must be a 'float' or an 'int' in ms")
    if ripe_atlas["timeout_per_probe_ms"] <= 0:
        raise ValueError("ripe_atlas 'timeout_per_probe_ms' must be > 0")
    return ripe_atlas["timeout_per_probe_ms"]

def get_ripe_packets_per_probe() -> int:
    """
    This method returns the number of tries that a probe will do for a measurement.
    It will send "packets_per_probe" queries for that NTP server. (see RIPE Atlas documentation for more information)

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "ripe_atlas" not in config:
        raise ValueError("ripe_atlas section is missing")
    ripe_atlas = config["ripe_atlas"]
    if "packets_per_probe" not in ripe_atlas:
        raise ValueError("ripe_atlas 'packets_per_probe' is missing")
    if not isinstance(ripe_atlas["packets_per_probe"], int):
        raise ValueError("ripe_atlas 'packets_per_probe' must be an 'int'")
    if ripe_atlas["packets_per_probe"] <= 0:
        raise ValueError("ripe_atlas 'packets_per_probe' must be > 0")
    return ripe_atlas["packets_per_probe"]

def get_ripe_number_of_probes_per_measurement() -> int:
    """
    This method returns the number of probes requested and desired for a measurement.

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "ripe_atlas" not in config:
        raise ValueError("ripe_atlas section is missing")
    ripe_atlas = config["ripe_atlas"]
    if "number_of_probes_per_measurement" not in ripe_atlas:
        raise ValueError("ripe_atlas 'number_of_probes_per_measurement' is missing")
    if not isinstance(ripe_atlas["number_of_probes_per_measurement"], int):
        raise ValueError("ripe_atlas 'number_of_probes_per_measurement' must be an 'int'")
    if ripe_atlas["number_of_probes_per_measurement"] <= 0:
        raise ValueError("ripe_atlas 'number_of_probes_per_measurement' must be > 0")
    return ripe_atlas["number_of_probes_per_measurement"]

# verify_if_config_is_set()