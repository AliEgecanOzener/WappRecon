import time
import random
import socket
import base64
import requests
import validators
import tldextract
import cloudscraper
from termcolor import colored
from urllib.parse import urlparse, urlunparse


class Utils:
    def __init__(self, url):
        self.url = url

    def convert_string_to_dict(self, data):
        if data is None:
            return None
        if isinstance(data, dict):
            return dict(data)
        if not isinstance(data, str):
            return None

        data = data.strip()
        converted = {}
        pairs = data.split("\n")

        for pair in pairs:
            pair = pair.strip()
            if ":" in pair:
                key, value = pair.split(":", 1)
                converted[key.strip()] = value.strip()
            elif "=" in pair:
                key, value = pair.split("=", 1)
                converted[key.strip()] = value.strip()

        return converted


    def get_random_user_agent(self):
        try:
            with open("assets/random_agents", "r", encoding="utf-8") as file:
                user_agents = [line.strip() for line in file if line.strip()]
            return random.choice(user_agents).strip() if user_agents else None
        except FileNotFoundError:
            print(colored("[-] File Not found.", "red"))
            return None


    def get_ip_info(self, target):
        try:
            domain_name = self.get_domain_name(target)
            return socket.gethostbyname(domain_name)
        except socket.gaierror:
            print(f"Hostname couldn't resolved: {target}")


    def is_valid_url(self, url):
        return validators.url(url)

    def is_valid_domain(self, domain):
        return validators.domain(domain)


    def get_domain_name(self, target):
        if self.is_valid_url(target):
            return urlparse(target).netloc
        elif self.is_valid_domain(target):
            return target

    def get_base_domain(self, url):
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}"


    def parse_url(self, url):
        parsed_url = urlparse(url)

        return {
            "scheme": parsed_url.scheme,
            "netloc": parsed_url.netloc,
            "path": parsed_url.path,
            "query": f"?{parsed_url.query}" if parsed_url.query else "",
            "fragment": f"#{parsed_url.fragment}" if parsed_url.fragment else "",
        }


    def basic_auth_header(self, url, creds):
        encoded_creds = base64.b64encode(creds.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "User-Agent": self.get_random_user_agent()
        }
        response = requests.get(url=url, cookies=self.c)
        if response:
            print(response.url)
            print(response.cookies)
            return response.url, response.cookies
