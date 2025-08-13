import json
from colorama import init
from termcolor import colored
from dnsrecon import DNSRecon
from utils import Utils
import requests

init()

class SubdomainRecon:
    def __init__(self, url, cookie="", proxy="", basic_auth_creds=""):
        self.url = url
        self.utils = Utils(self.url)
        self.cookie = self.utils.convert_string_to_dict(cookie)
        self.proxy = proxy
        self.basic_auth_creds = basic_auth_creds

        self.subdomains = set()
        self.available_subdomains = set()
        self.unavailable_subdomains = set()

        self.user_agent = self.utils.get_random_user_agent()
        self.headers = {"User-Agent": self.user_agent}
        self.dnsrecon = DNSRecon(self.url, self.cookie, self.proxy, self.basic_auth_creds)

    def subdomain_recon(self):
        print(colored("*" * 50, "yellow", attrs=['bold']))
        print(colored("SUBDOMAIN RECONNAISSANCE", "yellow", attrs=['bold']))
        print(colored("[INFO] Subdomain recon is starting...", "yellow"))

        print(colored("[INFO] Scanning with crt.sh...", "yellow"))
        crtsh_domains = self.crt_sh()
        if crtsh_domains:
            self.subdomains.update(crtsh_domains)

        print(colored("\n[INFO] Scanning with AXFR...", "yellow"))
        axfr_domains = self.dnsrecon.axfr()
        if axfr_domains:
            self.subdomains.update(axfr_domains)

        self.print_subdomains()
        return self.subdomains

    def crt_sh(self):
        if not self.utils.is_valid_url(self.url):
            print(colored("[ERROR] Given URL is invalid. Quitting...", "light_red"))
            return set()

        domain = self.utils.get_domain_name(self.url)
        if not self.utils.is_valid_domain(domain):
            print(colored(f"[ERROR] Domain {domain} is invalid. Quitting...", "light_red"))
            return set()

        try:
            url = f"https://crt.sh/?q={domain}&output=json"
            resp = requests.get(url=url, timeout=120, headers=self.headers)
            if 200 <= resp.status_code < 300:
                return self.crtsh_json(resp.text)
            else:
                print(colored(f"[ERROR] Domain {domain} is not found on crt.sh. Quitting", "light_red"))
                return set()
        except requests.RequestException as e:
            print(colored(f"[ERROR] Failed to fetch subdomains: {e}", "light_red"))
            return set()

    def crtsh_json(self, resp_text):
        try:
            data = json.loads(resp_text)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse hatası: {e}")
            return

        name_value = {entry["name_value"] for entry in data if "name_value" in entry}
        domain = self.utils.get_domain_name(self.url)
        filtered = set()
        for name in name_value:
            n = name.split('\n')
            for a in n:
                if domain in a:
                    if a not in filtered:
                        if "*" not in a:
                            filtered.add(a.strip())
        return filtered

    def print_subdomains(self):
        print("\n" + colored("[INFO] Found Subdomains:", "light_green"))
        for sub in sorted(self.subdomains):
            print(sub)

    def print_subdomain_info(self, untested):
        print("\n" + colored("[INFO] Subdomain Status", "light_green"))
        print(colored("[INFO] Available Subdomains", "light_green"))
        for s in sorted(self.available_subdomains):
            print(s)

        print("\n" + colored("*" * 50, "yellow"))
        print(colored("[INFO] Unavailable Subdomains", "light_green"))
        for s in sorted(self.unavailable_subdomains):
            print(s)

        print("\n" + colored("*" * 50, "yellow"))
        print(colored("[INFO] Untested Subdomains", "light_green"))
        for s in sorted(untested):
            print(s)

    def check_url(self, url):
        try:
            r = requests.get(url, timeout=5, cookies=self.cookie, headers=self.headers)
            if 200 <= r.status_code < 300:
                return True
            return False
        except requests.RequestException:
            return None

    def check_available_subdomains(self, max_retries=3):
        untested_subdomains = list(self.subdomains)
        retries = 0

        while untested_subdomains and retries < max_retries:
            print(colored(f"[INFO] Checking subdomains... Attempt {retries + 1} of {max_retries}", "yellow"))
            next_round = []

            for subdomain in untested_subdomains:
                print("\n" + colored(f"[INFO] Checking subdomain: {subdomain}", "yellow"))

                https_result = self.check_url(f"https://{subdomain}")
                http_result = self.check_url(f"http://{subdomain}") if https_result is not True else True

                if https_result or http_result:
                    print(colored(f"[FOUND] {subdomain} is available.", "light_green"))
                    self.available_subdomains.add(subdomain)
                elif https_result is None or http_result is None:
                    print(colored(f"[INFO] {subdomain} could not be tested.", "yellow"))
                    next_round.append(subdomain)
                else:
                    print(colored(f"[INFO] {subdomain} is unavailable.", "yellow"))
                    self.unavailable_subdomains.add(subdomain)

            untested_subdomains = next_round
            retries += 1

        self.print_subdomain_info(untested_subdomains)


if __name__ == "__main__":
    target = "https://zonetransfer.me/"
    subdomain_hunter = SubdomainRecon(target)
    subdomain_hunter.subdomain_recon()
