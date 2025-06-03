import os
import yaml
from dotenv import load_dotenv


def load_config(path="../../server_config.yaml"):
    """
    It loads the config from a YAML file.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    with open(path, "r") as f:
        return yaml.safe_load(f)

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
    print(get_edns_default_servers())
    get_ripe_timeout_per_probe()
    get_ripe_number_of_probes_per_measurement()
    get_ripe_probes_wanted_percentages()

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
    return ntp["version"]

def get_timeout_measurement_s() -> int:
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
    if not isinstance(ntp["timeout_measurement_s"], int):
        raise ValueError("ntp 'timeout_measurement_s' must be an 'int'")
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
    return ntp["number_of_measurements_for_calculating_jitter"]

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
    return edns["default_order_of_edns_servers"]

def get_ripe_timeout_per_probe() -> int:
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
    if not isinstance(ripe_atlas["timeout_per_probe_ms"], float | int):
        raise ValueError("ripe_atlas 'timeout_per_probe_ms' must be a 'float or an int' (in ms)")
    return ripe_atlas["timeout_per_probe_ms"]

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
    return ripe_atlas["number_of_probes_per_measurement"]

def get_ripe_probes_wanted_percentages() -> int:
    """
    This method returns an array representing how many probes of each type (ASN, prefix, country, area, random) we want to use.
    The default distribution that we found excellent is [0.33, 0.30, 0.27, 0.10, 0.0] which means:
    33% probes on the same ASN, 30% probes with the same prefix, 27% probes with the same country, 10% probes with the same area and
    0% random probes.

    Raises:
        ValueError: If this variable has not been correctly set.
    """
    if "ripe_atlas" not in config:
        raise ValueError("ripe_atlas section is missing")
    ripe_atlas = config["ripe_atlas"]
    if "probes_wanted_percentages" not in ripe_atlas:
        raise ValueError("ripe_atlas 'probes_wanted_percentages' is missing")
    if not isinstance(ripe_atlas["probes_wanted_percentages"], list):
        raise ValueError("ripe_atlas 'probes_wanted_percentages' must be a 'list'")
    if len(ripe_atlas["probes_wanted_percentages"]) != 5:
        raise ValueError("ripe_atlas 'probes_wanted_percentages' must contain exactly 5 elements")
    return ripe_atlas["probes_wanted_percentages"]


verify_if_config_is_set()