from typing import Optional
import requests



def get_probes(ip_asn: Optional[str], ip_country: Optional[str]) -> list[dict]:
    """
    This function handles all cases regarding what probes we should send.

    Args:
        ip_asn (int): The ASN of the IP.
        ip_country (str): The country of the IP.

    Returns:
        list[dict]: The list of probes that we will use for the measurement.
    """

    # ideas:
    # sort by
    # ASN -> the same network from the provider
    # prefixes -> the same family and the IPs that are
    probes = [
        {
            "type": "asn",
            "value": ip_asn,
            "requested": 1
        },
        {
            "type": "prefix",
            "value": "83.0.0.0/8",
            "requested": 1,
            "requested_by": 1
        },
        {
            "type": "country",
            "value": ip_country,
            "requested": 1,
            "requested_by": 2
        }
    ]
    return probes