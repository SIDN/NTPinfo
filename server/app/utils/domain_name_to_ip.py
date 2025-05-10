import socket
import dns.message
import dns.query
import dns.edns
import dns.rdatatype

def domain_name_to_ip_default(domain_name: str) -> list[str]:
    """
    It uses the DNS of this server to obtain the ip addresses of the domain name.
    This method is useful if you want IPs close to this server, or you do not care about the location of the IPs.

    Args:
        domain_name(str): The domain name.:
    Returns:
        list(str): A list of IPs of the domain name.
    """
    try:
        #188.24.115.185
        #ip = socket.gethostbyname(domain_name)
        results = socket.getaddrinfo(domain_name, 123, proto=socket.IPPROTO_UDP)
        ips = sorted(set(item[4][0] for item in results))
        return ips
    except Exception as e:
        print("Error in domain name to ip default: ", e)
        return None


def domain_name_to_ip_close_to_client(domain_name: str, client_ip, mask=24,
                                      resolvers=('1.1.1.1', '8.8.8.8', '9.9.9.9')) -> list[str]:
    #create a EDNS client subnet, which will be used to tell a close DNS server to the cient
    ecs = dns.edns.ECSOption(address=client_ip, srclen=mask, scopelen=0)
    for r in resolvers:
        #prepare to ask the DNS
        query = dns.message.make_query(domain_name, dns.rdatatype.A)
        query.use_edns(edns=True, options=[ecs])
        try:
            response=dns.query.udp(query, r, timeout=2)
        except Exception:
            try:
                response=dns.query.tcp(query, r, timeout=4)
            except Exception:
                continue
print(domain_name_to_ip_default("pool.ntp.org"))