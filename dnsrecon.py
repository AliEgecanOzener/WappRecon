import whois
import dns.resolver, dns.query, dns.message, dns.rdatatype, dns.reversename, dns.resolver
from utils import Utils
from colorama import init
from termcolor import colored

init()

class DNSRecon:
    def __init__(self, url, cookie, proxy, basic_auth_creds):
        self.url = url
        self.utils = Utils(self.url)
        self.cookie = self.utils.convert_string_to_dict(cookie)
        self.proxy = proxy
        self.basic_auth_creds = basic_auth_creds

        self.user_agent = self.utils.get_random_user_agent()

        if self.basic_auth_creds:
            self.headers = {"User-Agent": self.user_agent}

        else:
            self.headers = {"User-Agent": self.user_agent}

        self.records = {
            "A": [],
            "AAAA": [],
            "NS": [],
            "MX": [],
            "TXT": [],
            "CNAME": [],
            "SOA": [],
            "PTR": []
        }

        self.zone = []
        self.whois = None

    def is_valid_target(self):
        if self.utils.is_valid_url(self.url):
            domain = self.utils.get_base_domain(self.url)
            return self.utils.is_valid_domain(domain)
        elif self.utils.is_valid_domain(self.url):
            return True
        return False

    def append_list(self, list_obj, data):
        for d in data:
            text = d.to_text().strip()
            if text not in list_obj:
                list_obj.append(text)


    def check_record(self, record_type):
        if not self.is_valid_target():
            print(colored("[WARNING] Invalid target. Quitting...", "light_red"))
            return None

        try:
            if record_type == "PTR":
                if not self.records["A"]:
                    self.check_record("A")
                if not self.records["A"]:
                    print(colored("[INFO] No A record found. Cannot do PTR lookup.", "yellow"))
                    return None
                ip = self.records["A"][0]
                rev_name = dns.reversename.from_address(ip)
                result = dns.resolver.resolve(rev_name, "PTR")
            else:
                domain = self.utils.get_base_domain(self.url)
                result = dns.resolver.resolve(domain, record_type)

            self.append_list(self.records[record_type], result)
            return self.records[record_type]

        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            print(colored(f"[ERROR] Domain {self.utils.get_base_domain(self.url)} does not exist", "red"))
        except dns.resolver.LifetimeTimeout:
            print(
                colored(f"[ERROR] Timeout while querying {record_type} records for {self.utils.get_base_domain(self.url)}", "red"))
        except Exception as e:
            print(colored(f"[ERROR] {record_type} lookup failed: {e}", "red"))

        return None

    def axfr(self):
        print(colored("************************************************************************************************","yellow", attrs=['bold']))
        print(colored("AXFR Check", "yellow", attrs=['bold']))
        print(colored("************************************************************************************************","yellow", attrs=['bold']))
        if not self.is_valid_target():
            print("[INFO] Given target is invalid. Quitting...")
            return None

        domain = self.utils.get_base_domain(self.url)

        if not self.records['NS']:
            nameservers = self.check_record("NS")
            if not nameservers:
                print(f"[INFO] No NS record found for {self.url}. Quitting...")
                return None

        for server in self.records['NS']:

            try:
                server_domain = server.strip(".")
                server_ip = self.utils.get_ip_info(server_domain)
                print(f"[INFO] Trying AXFR from {server_domain} ({server_ip}) for {domain}")

                zone = dns.zone.from_xfr(dns.query.xfr(server_ip, domain))
                print(colored(f"[SUCCESS] Zone transfer successful from {server_domain}", "yellow"))
                self.zone.append((server_domain, zone))

            except Exception as e:
                print(f"[ERROR] Zone transfer failed for {server}: {e}")
                continue
    def return_axfr_subdomains(self):
        subdomains = set()
        if not self.zone:
            self.zone = self.axfr()

        if not self.zone:
           return

        domain = self.utils.get_base_domain(self.url)
        for name, node in self.zone.items():
            fqdn = f"{name}.{domain}" if str(name) != "@" else domain
            subdomains.add(fqdn)
        return subdomains

    def whois_lookup(self):
        if not self.is_valid_target():
            print(colored("[WARNING] Invalid target. Quitting...", "light_red"))
            return None
        domain = self.utils.get_base_domain(self.url)

        try:
            whois_info = whois.whois(domain)
            self.whois = whois_info
            return self.whois

        except Exception as e:
            print(f"[ERROR] {e}")


    def print_axfr(self):

        if not self.zone:
            print("[INFO] No zone transfer data available.")
            return

        for server_domain, zone in self.zone:
            print(colored(f"[INFO] Zone transfer records from {server_domain}...", "yellow", attrs=['bold']))
            print(colored("---------------------------------------------------------------------------------------------------", "yellow", attrs=['bold']))
            print(colored("---------------------------------------------------------------------------------------------------","yellow", attrs=['bold']))
            print(colored("---------------------------------------------------------------------------------------------------","yellow", attrs=['bold']))

            for name, node in zone.nodes.items():
                print(zone[name].to_text(name))



    def print_whois(self):
        print(colored("************************************************************************************************","yellow", attrs=['bold']))
        print(colored("[INFO] Whois records...", "yellow", attrs=['bold']))
        print(colored("************************************************************************************************","yellow", attrs=['bold']))

        print(self.whois)

    def print_dns_records(self, record_type):

        records = self.records.get(record_type, [])
        if not records:
            print(colored(f"[INFO] No {record_type} records found for {self.utils.get_base_domain(self.url)}", "yellow"))
            return
        print(colored(f"[INFO] {record_type} records:", "yellow"))
        for data in records:
            print(data)

"""
url = "microsoft.com"
hit_dns = DNSRecon(url, "", "", "")

hit_dns.whois_lookup()
hit_dns.print_whois()

hit_dns.axfr()
hit_dns.print_axfr()

print(colored("************************************************************************************************",
              "yellow", attrs=['bold']))
print(colored("[INFO] DNS records...", "yellow", attrs=['bold']))
print(colored("************************************************************************************************",
              "yellow", attrs=['bold']))

for rtype in ["A", "AAAA", "NS", "MX", "TXT", "CNAME", "SOA", "PTR"]:
    hit_dns.check_record(rtype)
    hit_dns.print_dns_records(rtype)
"""



