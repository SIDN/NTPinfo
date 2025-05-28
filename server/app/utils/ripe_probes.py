import requests



def get_probes(ip_asn,ip_country):
    probes = [
        {
            "type": "asn",
            "value": ip_asn,
            "requested": "50"
        },
        {
            "type": "prefix",
            "value": "83.0.0.0/8",
            "requested": 10,
            "requested_by": 1
        },
        {
            "type": "country",
            "value": ip_country,
            "requested": 10,
            "requested_by": 2
        }
    ]
    return probes