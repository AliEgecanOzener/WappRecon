import json
from colorama import init
from termcolor import colored
from dnsrecon import DNSRecon
from utils import Utils
import requests
from bs4 import BeautifulSoup

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
        self.untested_subdomains = set()

        self.user_agent = self.utils.get_random_user_agent()
        self.headers = {"User-Agent": self.user_agent}
        self.dnsrecon = DNSRecon(self.url, self.cookie, self.proxy, self.basic_auth_creds)


    def subdomain_recon(self):
        print(colored("*" * 50, "yellow", attrs=['bold']))
        print(colored("SUBDOMAIN RECONNAISSANCE", "yellow", attrs=['bold']))
        print(colored("Subdomain recon is starting...", "yellow"))

        print("Checking crt.sh...")
        self.crt_sh()

        print("Checking zone transfer...")
        self.dnsrecon.return_axfr_subdomains()

        print("Checking hackertarget.com...")
        self.get_subdomains_hackertarget()

        print("Checking WayBack Archive...")
        self.get_subdomains_wayback()

        self.print_subdomains()
        print("\nSubdomain recon finished.")
        return self.subdomains

    def crt_sh(self):
        if not self.utils.is_valid_target():
            print(colored("[WARNING] Invalid target. Quitting...", "light_red"))
            return

        domain = self.utils.get_base_domain(self.url)
        try:
            url = f"https://crt.sh/?q={domain}&output=json"
            resp = requests.get(url=url, timeout=120, headers=self.headers)
            if 200 <= resp.status_code < 300:
                self.crtsh_json(resp.text)
        except requests.RequestException:
            return

    def crtsh_json(self, resp_text):
        try:
            data = json.loads(resp_text)
        except json.JSONDecodeError:
            return

        domain = self.utils.get_domain_name(self.url)
        for entry in data:
            name_value = entry.get("name_value", "")
            for sub in name_value.split('\n'):
                sub = sub.strip()
                if domain in sub and "*" not in sub:
                    self.subdomains.add(sub)

    def get_subdomains_hackertarget(self):
        if not self.utils.is_valid_target():
            print(colored("[WARNING] Invalid target. Quitting...", "light_red"))
            return

        domain = self.utils.get_base_domain(self.url)
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        try:
            r = requests.get(url, timeout=10)
            for line in r.text.splitlines():
                parts = line.split(",")
                if len(parts) > 0:
                    self.subdomains.add(parts[0].strip())

        except Exception:
            return

    def get_subdomains_wayback(self):
        if not self.utils.is_valid_target():
            print(colored("[WARNING] Invalid target. Quitting...", "light_red"))
            return

        domain = self.utils.get_base_domain(self.url)
        wayback_url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original"
        headers = {
            "User-Agent": self.utils.get_random_user_agent()
        }
        try:
            response = requests.get(url=wayback_url, headers=headers, timeout=(5, 10))
            soup = BeautifulSoup(response.text, "html.parser")

            href_links = [a.get("href") for a in soup.find_all("a") if a.get("href")]
            src_links = [tag.get("src") for tag in soup.find_all(src=True)]

            for link in href_links + src_links:
                netloc = self.utils.parse_url(link)['netloc']
                if netloc and domain in netloc:
                    if netloc not in self.subdomains:
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        self.subdomains.add(netloc)

        except requests.exceptions.Timeout:
            print(f"Request timeout for {wayback_url}")
        except Exception as e:
            print(f"Error occurred {e}")

    def print_subdomains(self):
        total = len(self.subdomains)
        for sub in sorted(self.subdomains):
            print(sub)
        print(f"\nFound {total} Subdomains.")

    def print_subdomain_status(self, untested):

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
                #print("\n" + colored(f"[INFO] Checking subdomain: {subdomain}", "yellow"))

                https_result = self.check_url(f"https://{subdomain}")
                http_result = self.check_url(f"http://{subdomain}") if https_result is not True else True

                if https_result or http_result:
                    #print(colored(f"[FOUND] {subdomain} is available.", "light_green"))
                    self.available_subdomains.add(subdomain)
                elif https_result is None or http_result is None:
                    #print(colored(f"[INFO] {subdomain} could not be tested.", "yellow"))
                    next_round.append(subdomain)
                else:
                    #print(colored(f"[INFO] {subdomain} is unavailable.", "yellow"))
                    self.unavailable_subdomains.add(subdomain)

            untested_subdomains = next_round
            retries += 1

        self.untested_subdomains = set(untested_subdomains)
