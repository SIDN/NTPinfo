import ipaddress

def is_ip_address(ip_str:str) -> str | None:
    try:
        ip = ipaddress.ip_address(ip_str)
        if isinstance(ip, ipaddress.IPv4Address):
            return "ipv4"
        else:
            if isinstance(ip, ipaddress.IPv6Address):
                return "ipv6"
        #this part is unreachable (Well, at least another ip version would be created
        #return None
    except ValueError:
        return None