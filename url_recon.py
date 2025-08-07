from utils import *
from colorama import init
from termcolor import colored
from bs4 import BeautifulSoup
import validators

init()
def xml_based_link_finder(netloc, xml_text):
    pass

    """
    soup = BeautifulSoup(xml_text, "xml")
    links = set()

    for tag in soup.find_all(True):
        for attr in ["href", "src", "url", "link", "action", "data", "value", "download"]:
            val = tag.get(attr)

            if val and isinstance(val, str) and ("http://" in val or "https://" in val):
                links.add(val)

        tag_text = tag.text.strip()
        parsed_tag_url = urlparse(tag_text)

        if tag.name.lower() in ["loc", "guid", "canonical", "media:content", "enclosure"]:
            if tag_text.startswith("http"):
                if parsed_tag_url.netloc == netloc:
                    links.add(tag_text)
    links = set(links)
    print(links)
    return links
    """
def sitemap_recon(url, cookie):
    parsed_url = parse_url(url)
    print(colored("**********************************************************", "red", attrs=['bold']))
    print(colored("SITEMAP", "red"))
    print("[INFO] Sitemap recon is starting...")
    robots_url = parsed_url['scheme'] + "://" + parsed_url['netloc'] + "/robots.txt"
    headers = {
        "User-Agent": get_random_user_agent()
    }
    print("[INFO] Checking robots.txt file...")
    robots_response = requests.get(url=robots_url, cookies=cookie, headers=headers)
    robots_text = robots_response.text
    if robots_response.status_code < 300 or robots_response.status_code > 199:
        sitemaps = []

        for row in robots_text.splitlines():
            if "sitemap:" in row.lower():
                sitemap_url = row.lower().replace("sitemap:", "").strip()
                sitemaps.append(sitemap_url)
                print(colored(f"[FOUND] {sitemap_url}", "green", attrs=['bold']))

    else:
        print(robots_response.status_code)

    """
        for sitemap in sitemaps:
        if sitemap.endswith('.xml'):
            xml_based_sitemap(sitemap, cookie)
            return

        elif sitemap.endswith('sitemap'):
            print("page based sitemap")
            return
    """




    new_url = parsed_url['scheme'] + "://" + parsed_url['netloc'] + "/sitemap.xml"
    response = requests.get(url=new_url, cookies=cookie)

    if response.status_code < 200 or response.status_code > 299:
        print(f"[INFO] Sitemap.xml couldn't found with status {response.status_code}")

    else:
        xml_based_sitemap(url, cookie)
        return

    new_url = parsed_url['scheme'] + "://" + parsed_url['netloc'] + "/sitemap"
    response = requests.get(url=new_url, cookies=cookie)

    if response.status_code < 200 or response.status_code > 299:
        print(f"[INFO] Sitemap page couldn't found with status {response.status_code}")

    else:
        pass

def xml_based_sitemap(url, cookie):
    pass
    """ 
    sitemaps_list = []
    parsed_url = parse_url(url)
    new_url = parsed_url['scheme'] + "://" + parsed_url['netloc'] + "/sitemap.xml"

    response = requests.get(url=new_url, cookies=cookie)

    if response.status_code < 200 or response.status_code > 299:
        print(f"[INFO] Sitemap.xml couldn't found with status {response.status_code}")
        return

    else:
        response_text = response.text
        netloc = parsed_url['netloc']

        sitemaps = xml_based_link_finder(netloc, response_text)
        sitemaps_list.append(sitemaps)

        return sitemaps_list
    """


url = "https://www.microsoft.com/"
sitemap_recon(url, "")




def page_based_sitemap(url, cookie):
    pass

def link_finder(netloc, response_text):

    soup = BeautifulSoup(response_text, "html.parser")
    sitemap_list = set()

    for tag in soup.find_all(["a", "link", "script", "img", "iframe"]):
        for attr in ["href", "src"]:
            link = tag.get(attr)
            if link:
                sitemap_list.add(link)

