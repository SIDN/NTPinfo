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


import requests
def get_country_from_ip(ip):
    #return ""
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    data = response.json()
    return data.get("country", "Unknown")

def domain_name_to_ip_close_to_client(domain_name: str, client_ip: str, mask: int=24,
                                      resolvers: list[str]=['8.8.8.8', '1.1.1.1']) -> list[str] | None:
    """
    This method tries to obtain the ip addresses of the domain name from some popular DNS servers (resolvers)
    that have (or may have) the ability to get an IP close to the client.
    If the name is not a domain name, it will return an empty list.

    Args:
        domain_name(str): The domain name.
        client_ip(str): The client IP.
        mask(int): The DNS MASK. (how many bits of the ip)
        resolvers(list): A list of popular DNS resolvers that are ECS-capable.

    Returns:
        list(str) | None: A list of IPs of the domain name or None if the domain name is not valid.
    """
    if not is_valid_domain_name(domain_name):
        return None
    ips = []
    #create a EDNS client subnet, which will be used to tell a close DNS server to the client
    try:
        ecs = dns.edns.ECSOption(address=client_ip, srclen=mask, scopelen=0)
        #we try for all resolvers because some of them may not accept some domain name
        for r in resolvers:
            #stop if we already found some IP address
            if len(ips)!=0:
                break
            #prepare to ask the DNS
            query = dns.message.make_query(domain_name, dns.rdatatype.A)
            query.use_edns(edns=True, options=[ecs])
            #try with udp and if it fails try with tcp
            try:
                response = dns.query.udp(query, r, timeout=2)
            except Exception:
                try:
                    response = dns.query.tcp(query, r, timeout=2)
                except Exception:
                    continue

            # print(response)
            #ncollect the IPs or search further if we found a CNAME
            for ans in response.answer:
                #nwe take into consideration IPv4,IPv6 and CNAME (which redirects to another domain name
                if ans.rdtype in (dns.rdatatype.A,dns.rdatatype.AAAA):#, dns.rdatatype.AAAA):
                    for i in ans.items:
                        ips.append(i.address)
                else:
                    if ans.rdtype == dns.rdatatype.CNAME:
                        #there is at most 1 CNAME
                        next_domain_name = str(list(ans.items)[0]).rstrip('.')
                        ips+=domain_name_to_ip_close_to_client(next_domain_name,client_ip,mask,resolvers)
            #print(ips)
            #print([get_country_from_ip(x) for x in ips])
    except Exception as e:
        print("Error in domain name to ip close to client: ", e)
        return None

    #remove duplicates
    ips = list(set(ips))
    return ips
#example of usage:
dn="pool.ntp.org"
client_ip="85.161.47.136"
ans=domain_name_to_ip_close_to_client(dn, client_ip,16)
print(ans)
print([get_country_from_ip(x) for x in ans])
#print([get_country_from_ip(x) for x in domain_name_to_ip_close_to_client(dn, client_ip,16)])
#print(domain_name_to_ip_close_to_client(dn, client_ip,24))
#dig +short +subnet=83.25.24.10/24 pool.ntp.org @50.116.32.247
print("By default: ")
print(domain_name_to_ip_default(dn))
#Cehia: 85.161.47.136
#Poland: 83.25.24.10
#Spain: 88.31.57.92
#US: 8.31.57.92
#time.google.com, time.windows.com, time.aws.com, time.cloudflare.com, and pool.ntp.org.