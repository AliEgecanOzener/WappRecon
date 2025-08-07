import time
import random
import socket
import base64
import requests
import validators
import cloudscraper
from termcolor import colored
from urllib.parse import urlparse, urlunparse


def get_query(url, cookie, header, retries=159, delay=5):
    session = cloudscraper.create_scraper()

    if isinstance(cookie, str):
        cookie = convert_string_to_dict(cookie) or {}

    if isinstance(header, str):
        header = convert_string_to_dict(header) or {}

    for attempt in range(retries):
        try:
            response = session.get(url, cookies=cookie, headers=header, timeout=20)
            return response

        except requests.exceptions.ReadTimeout:
            print(colored(f"[-] Read timeout. Retry {attempt + 1}/{retries}", "yellow"))
            time.sleep(delay)

        except requests.exceptions.Timeout:
            print(colored("[-] Request timed out.", "red"))

        except requests.exceptions.ConnectionError:
            print(colored("[-] Connection error occurred.", "red"))

        except requests.exceptions.HTTPError as e:
            print(colored(f"[-] HTTP error: {e}", "red"))

        except requests.exceptions.RequestException as e:
            print(colored(f"[-] Unexpected error: {e}", "red"))

        except:
            print("Unknown error")

    print(colored("[-] Failed after retries.", "red"))
    return None


def post_query(url, cookie, header, data, file):
    if isinstance(cookie, str):
        cookie = convert_string_to_dict(cookie) or {}

    if isinstance(header, str):
        header = convert_string_to_dict(header) or {}

    try:
        session = cloudscraper.create_scraper()

        if file:
            response = session.post(url, cookies=cookie, headers=header, data=data, files=file, timeout=10)
        else:
            response = session.post(url, cookies=cookie, headers=header, data=data, timeout=10)

        return response

    except requests.exceptions.Timeout:
        print(colored("[-] Request timed out.", "red"))
    except requests.exceptions.ConnectionError:
        print(colored("[-] Connection error occurred.", "red"))
    except requests.exceptions.HTTPError as e:
        print(colored(f"[-] HTTP error: {e}", "red"))
    except requests.exceptions.RequestException as e:
        print(colored(f"[-] Unexpected error: {e}", "red"))


def convert_string_to_dict(data): # eklenmedi
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
            key = key.strip()
            value = value.strip()
            converted[key] = value
        elif "=" in pair:
            key, value = pair.split("=", 1)
            key = key.strip()
            value = value.strip()
            converted[key] = value

    return converted

def get_random_user_agent():
    try:
        with open("assets/random_agents", "r", encoding="utf-8") as file:
            user_agents = [line.strip() for line in file if line.strip()]
        return random.choice(user_agents).strip() if user_agents else None
    except FileNotFoundError:
        print(colored("[-] File Not found.", "red"))
        return None

def get_ip_info(target):
  try:
       domain_name = get_domain_name(target)
       ip_addr = socket.gethostbyname(domain_name)
       return ip_addr

  except socket.gaierror:
        print(f"Hostname couldn't resolved: {target}")
        return

def is_valid_url(url):
    if validators.url(url):
        return True
    else:
        return False

def is_valid_domain(domain):
    if validators.domain(domain):
        return domain
    else:
        return

def get_domain_name(target):
    if is_valid_url(target):
        domain_name = urlparse(target).netloc
        return domain_name
    elif is_valid_domain(target):
        return target
    else:
        return

def parse_url(url):

    parsed_url = urlparse(url)

    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    path = parsed_url.path
    query = f"?{parsed_url.query}" if parsed_url.query else ""
    fragment = f"#{parsed_url.fragment}" if parsed_url.fragment else ""

    parsed_dict = {
        "scheme": scheme,
        "netloc": netloc,
        "path": path,
        "query": query,
        "fragment": fragment,
    }

    return parsed_dict


def basic_auth_header(url, cookie, creds):
    encoded_creds = base64.b64encode(creds.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_creds}",
        "User-Agent": get_random_user_agent()
    }

    response = get_query(url, cookie, headers, 1, 1)
    print(response.url)
    print(response.cookies)

    return response.url, response.cookies

url = "https://tr-wiki.metin2.gameforge.com/index/"
url = "https://testpages.eviltester.com/styled/auth/basic-auth-results.html"
url = "https://www.google.com/search?q=linkedin+sitemap"
url = "https://github.com/sitemap"
url = "https://www.diffchecker.com/"

req = get_query(url=url, header="", cookie="")










"""
def basic_auth_url(url, cookie, creds):
    parsed_url = urlparse(url)
    print(parsed_url)
    new_netloc = f"{creds}@{parsed_url.netloc}"
    new_parsed_url = parsed_url._replace(netloc=new_netloc)
    new_url = urlunparse(new_parsed_url)
    print(new_url)
    headers = {
        "User-Agent": get_random_user_agent()
    }

    response = get_query(url, cookie, headers, 1, 1)
    response_url = response.url
    response_cookies = response.headers['Server']

    print(response_url)
    print(response_cookies)
"""