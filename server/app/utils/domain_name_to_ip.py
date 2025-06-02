import socket
import dns.message
import dns.query
import dns.edns
import dns.rdatatype
from server.app.utils.validate import is_valid_domain_name


def domain_name_to_ip_default(domain_name: str) -> list[str] | None:
    """
    It uses the DNS of this server to obtain the ip addresses of the domain name.
    This method is useful if you want IPs close to this server, or you do not care about the location of the IPs.

    Args:
        domain_name(str): The domain name.:

    Returns:
        list(str) | None: A list of IPs of the domain name or None if the domain name is not valid.
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


def domain_name_to_ip_close_to_client(domain_name: str, client_ip: str, mask: int = 24,
                                                    resolvers: list[str] = ['8.8.8.8', '1.1.1.1'],
                                                    depth: int = 0, max_depth: int = 2) -> list[str] | None:
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
        mask(int): The DNS MASK. (how many bits of the ip)
        resolvers(list): A list of popular DNS resolvers that are ECS-capable.
        depth(int): The depth of the EDNS query if it returns a CNAME. (It is recommended to set this to 0.)
        max_depth(int): The maximum depth of the EDNS query. (It is recommended to set this to 2 or 3 to prevent long delay.)

    Returns:
        list(str) | None: A list of IPs of the domain name or None if the domain name is not valid.
    """
    if not is_valid_domain_name(domain_name):
        return None
    ips: list[str] = []

    try:
        # create a EDNS client subnet, which will be used to tell a close DNS server to the client
        ecs = dns.edns.ECSOption(address=client_ip, srclen=mask, scopelen=0)
        # we try for all resolvers because some of them may not accept some domain names
        for r in resolvers:
            # stop if we already found some IP addresses. Remove this "if" if you want to get more IPs
            if len(ips) != 0:
                break

            response = perform_edns_query(domain_name, r, ecs)

            if response is None:
                continue
            # collect the IPs or search further if we found a CNAME
            ips = ips + edns_response_to_ips(response, client_ip, mask, resolvers, depth, max_depth)
    except Exception as e:
        print("Error in domain name to ip close to client: ", e)
        return None

    #remove duplicates
    ips = list(set(ips))
    return ips


def perform_edns_query(domain_name: str, resolver_name: str, ecs: dns.edns.ECSOption,
                       timeout: int = 2) -> dns.message.Message | None:
    """
    This method performs a EDNS query against the domain name using the resolver as
    the DNS IP and returns the response.

    Args:
         domain_name(str): The domain name.
         resolver_name(str): The resolver name.
         ecs(dns.edns.ECSOption): The EDNS query option. It contains information about the client IP.
         timeout(int): The timeout for the EDNS query.

    Returns:
        dns.message.Message | None: The response from the EDNS query.
    """
    # prepare to ask the DNS
    query = dns.message.make_query(domain_name, dns.rdatatype.A)
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


def edns_response_to_ips(response: dns.message.Message, client_ip: str, mask: int,
                        resolvers: list[str], depth: int=0, max_depth: int=2) -> list[str]:
    """
    This method takes the IPs from the response. In case the response has a CNAME, it will
    recursively try to get an IP from that CNAME. In the worst case, it will be redirected "max_depth" times.
    This parameter is useful for preventing an infinite loop in redirecting.

    Args:
        response(dns.message.Message): The response from the EDNS query.
        client_ip(str): The client IP.
        mask(int): The DNS MASK. (how many bits of the ip)
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
                    a = domain_name_to_ip_close_to_client(next_domain_name, client_ip, mask, resolvers, depth + 1, max_depth)
                    if a is not None:
                        ips += a
    return ips
#example of usage:
# dn = "time.apple.com"
# client = "88.31.57.92"
# ans = domain_name_to_ip_close_to_client(dn, client, 24)
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