import os
from dotenv import load_dotenv


load_dotenv()


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