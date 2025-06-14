import socket
from typing import Optional
import dns.message
import dns.query
import dns.edns
import dns.rdatatype

from server.app.models.CustomError import DNSError
from server.app.utils.ip_utils import get_ip_family
from server.app.utils.load_config_data import get_edns_default_servers, get_mask_ipv6, get_mask_ipv4, get_edns_timeout_s
from server.app.utils.validate import is_valid_domain_name


def domain_name_to_ip_list(ntp_server_domain_name: str, client_ip: Optional[str], wanted_ip_type: int) -> list[str]:
    """
    This method handles the case when client IP is None and uses our server as the default IP.
    It will return the list of IP addresses that are close to the client.

    Args:
        ntp_server_domain_name (str): NTP server domain name.
        client_ip (Optional[str]): Client IP address.
        wanted_ip_type (int): The IP type of the resulting IPs that we want. (IPv4 or IPv6).

    Returns:
        list[str]: List of IP addresses that are close to the client or to the server if client IP is None

    Raises:
        DNSError: If the domain name is invalid, or it was impossible to find some IP addresses.
    """
    domain_ips: list[str] | None
    if client_ip is None:  # if we do not have the client_ip available, use this server as a "client ip"
        domain_ips = domain_name_to_ip_default(ntp_server_domain_name)
    else:
        domain_ips = domain_name_to_ip_close_to_client(ntp_server_domain_name, client_ip, wanted_ip_type)

    # if the domain name is invalid or []
    if domain_ips is None or len(domain_ips) == 0:
        raise DNSError(f"Could not find any IP address for {ntp_server_domain_name}.")
    return domain_ips

def domain_name_to_ip_default(domain_name: str) -> Optional[list[str]]:
    """
    It uses the DNS of this server to obtain the ip addresses of the domain name.
    This method is useful if you want IPs close to this server, or you do not care about the location of the IPs.

    Args:
        domain_name(str): The NTP server domain name.

    Returns:
        Optional[list[str]]: A list of IPs of the domain name or None if the domain name is not valid.
    """
    try:
        if not is_valid_domain_name(domain_name):
            return None
        results = socket.getaddrinfo(domain_name, 123, proto=socket.IPPROTO_UDP)
        ips = sorted(set(item[4][0] for item in results))
        return ips
    except Exception as e:
        print("Error in domain name to ip default: ", e)
        return None


def domain_name_to_ip_close_to_client(domain_name: str, client_ip: str, wanted_ip_type: int,
                                                    resolvers: list[str] = get_edns_default_servers(),
                                                    depth: int = 0, max_depth: int = 2) -> Optional[list[str]]:
    """
    This method tries to obtain the ip addresses of the domain name from some popular DNS servers (resolvers)
    that have (or may have) the ability to get an IP close to the client. It uses EDNS queries to get the IPs
    and in case the queries return a domain name, this method recursively tries to solve them. It uses "depth"
    and "max_depth" to prevent infinite loops in redirecting.

    It is important to note that multiple servers may share the same IP address. So, some countries may use the
    same IP for the same domain name. You can check this using https://www.whatsmydns.net/. This also provides
    insights in the cases where we receive CNAME responses.


    If the name is not a domain name, it will return an empty list.
    If the EDNS query does not return a CNAME, depth and max_depth would not be used.

    Args:
        domain_name(str): The domain name.
        client_ip(str): The client IP.
        wanted_ip_type(int): The IP type of the resulting IPs that we want.
        resolvers(list): A list of popular DNS resolvers that are ECS-capable.
        depth(int): The depth of the EDNS query if it returns a CNAME. (It is recommended to set this to 0.)
        max_depth(int): The maximum depth of the EDNS query. (It is recommended to set this to 2 or 3 to prevent long delay.)

    Returns:
        Optional[list[str]]: A list of IPs of the domain name or None if the domain name is not valid.

    Raises:
        Exception: If the client IP is invalid
    """
    if not is_valid_domain_name(domain_name):
        return None

    ip_family = get_ip_family(client_ip) # may throw an exception if the client IP is invalid
    mask: int # The DNS MASK for client IP. (how many bits of the ip)
    if ip_family == 6:
        mask = get_mask_ipv6()
    else:
        mask = get_mask_ipv4()

    ips: list[str] = []

    try:
        # create a EDNS client subnet, which will be used to tell a close DNS server to the client
        ecs = dns.edns.ECSOption(address=client_ip, srclen=mask, scopelen=0)
        # we try for all resolvers because some of them may not accept some domain names
        for r in resolvers:
            # stop if we already found some IP addresses. Remove this "if" if you want to get more IPs
            if len(ips) != 0:
                break
            response = perform_edns_query(domain_name, r, ecs, wanted_ip_type=wanted_ip_type)

            if response is None:
                continue
            # collect the IPs or search further if we found a CNAME
            ips = ips + edns_response_to_ips(response, client_ip, wanted_ip_type, resolvers, depth, max_depth)
    except Exception as e:
        print("Error in domain name to ip close to client: ", e)
        return None

    #remove duplicates
    ips = list(set(ips))
    return ips


def perform_edns_query(domain_name: str, resolver_name: str, ecs: dns.edns.ECSOption,
                       wanted_ip_type: int, timeout: float|int = get_edns_timeout_s()) -> Optional[dns.message.Message]:
    """
    This method performs a EDNS query against the domain name using the resolver as
    the DNS IP and returns the response.

    Args:
         domain_name(str): The domain name.
         resolver_name(str): The resolver name.
         ecs(dns.edns.ECSOption): The EDNS query option. It contains information about the client IP.
         wanted_ip_type(int): The IP type of the EDNS query. (4 or 6)
         timeout(float|int): The timeout for the EDNS query.

    Returns:
        Optional[dns.message.Message]: The response from the EDNS query.
    """
    # prepare to ask the DNS
    if wanted_ip_type == 4:
        query = dns.message.make_query(domain_name, dns.rdatatype.A)
    else:
        query = dns.message.make_query(domain_name, dns.rdatatype.AAAA)
    query.use_edns(edns=True, options=[ecs])
    # try with udp and if it fails try with tcp
    try:
        response = dns.query.udp(query, resolver_name, timeout=timeout)
    except Exception:
        try:
            response = dns.query.tcp(query, resolver_name, timeout=timeout)
        except Exception:
            return None
    return response


def edns_response_to_ips(response: dns.message.Message, client_ip: str, wanted_ip_type: int,
                         resolvers: list[str], depth: int=0, max_depth: int=2) -> list[str]:
    """
    This method takes the IPs from the response. In case the response has a CNAME, it will
    recursively try to get an IP from that CNAME. In the worst case, it will be redirected "max_depth" times.
    This parameter is useful for preventing an infinite loop in redirecting.

    Args:
        response(dns.message.Message): The response from the EDNS query.
        client_ip(str): The client IP.
        wanted_ip_type(int): The IP type of the resulting IPs that we want.
        resolvers(list): A list of popular DNS resolvers that are ECS-capable. They are used in the CNAME case.
        depth(int): The depth of the EDNS query.
        max_depth(int): The maximum depth of the EDNS query.

    Returns:
        list(str): A list of IPs taken from the response.
    """
    ips: list[str] = []
    for ans in response.answer:
        # take into consideration IPv4,IPv6 and CNAME (which redirects to another domain name)
        if ans.rdtype in (dns.rdatatype.A, dns.rdatatype.AAAA):
            for i in ans.items:
                ips.append(i.address)
        else:
            if ans.rdtype == dns.rdatatype.CNAME:
                # there is at most 1 CNAME
                next_domain_name = str(list(ans.items)[0]).rstrip('.')
                print("redirecting to ", next_domain_name)
                if depth < max_depth:
                    a = domain_name_to_ip_close_to_client(next_domain_name, client_ip, wanted_ip_type, resolvers,
                                                          depth + 1, max_depth)
                    if a is not None:
                        ips += a
    return ips
#example of usage:
# dn = "time.apple.com"
# client = "88.31.57.92"
# ans = domain_name_to_ip_close_to_client(dn, client )
# print(ans)
# print([get_country_from_ip(x) for x in ans])
#print([get_country_from_ip(x) for x in domain_name_to_ip_close_to_client(dn, client_ip,16)])
#print(domain_name_to_ip_close_to_client(dn, client_ip,24))
#dig +short +subnet=83.25.24.10/24 pool.ntp.org @50.116.32.247
# print("By default: ")
# print(domain_name_to_ip_default(dn))
#Cehia: 85.161.47.136
#Poland: 83.25.24.10
#Spain: 88.31.57.92
#US: 8.31.57.92
#time.google.com, time.windows.com, time.aws.com, time.cloudflare.com, and pool.ntp.org.
# print(domain_name_to_ip_list("time.apple.com", "83.25.24.10", 6))#2a01:b740:a20:3000::1f2"))
# print(domain_name_to_ip_list("time.apple.com", "2a01:b740:a20:3000::1f2", 4))
# print(domain_name_to_ip_list("time.apple.com", "83.25.24.10", 4))