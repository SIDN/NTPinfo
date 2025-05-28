import os
from dotenv import load_dotenv


load_dotenv()


def get_ipinfo_lite_api_token() -> str:
    """
    This function returns the IPinfo Lite API token.
    """
    return os.getenv('IPINFO_LITE_API_TOKEN')

def get_ripe_account_email() -> str:
    """
    This function returns the RIPE Atlas account email. (one that has enough credits)
    """
    return os.getenv('ripe_account_email')

def get_ripe_api_token() -> str:
    """
    This function returns the RIPE Atlas API token.
    """
    return os.getenv('ripe_api_token')