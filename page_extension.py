import requests
from urllib.parse import urlparse
from utils import *
class PageExtensionAnalyzer:
    def __init__(self, url, cookies, proxy, http_bauth_creds):

        self.url = url
        self.cookies = cookies
        self.proxy = proxy
        self.creds = http_bauth_creds

        self.result = {
            "language": None,
            "extension": None,
            "success_url": None
        }

    def analyze(self):
        print("**********************************************************")
        print("PAGE EXTENSIONS")

        parsed_url = parse_url(self.url)
        path = parsed_url["path"]

        lang_dict = {
            ".php": "PHP",
            ".asp": "ASP",
            ".aspx": "ASP.NET",
            ".jsp": "Java",
            ".jspx": "Java",
            ".py": "Python",
            ".rb": "Ruby",
        }

        for ext, lang in lang_dict.items():
            if ext in path:
                self.result["language"] = lang
                self.result["extension"] = ext
                self.result["success_url"] = self.url
                print(f"[INFO] URL already contains extension '{ext}'")
                print(f"[FOUND] Programming language: {lang}")
                print(f"[INFO] URL: {self.url}")
                print("**********************************************************")
                return self.result

        print("[INFO] No known extension found in URL.")
        print("[INFO] Trying extensions...")

        base_path = path.rstrip('/') if path.endswith('/') else path

        for ext, lang in lang_dict.items():
            urls_to_try = []

            if path.endswith('/'):
                urls_to_try.append(f"{base_path}{ext}/")
                urls_to_try.append(f"{base_path}{ext}")
            else:
                urls_to_try.append(f"{base_path}{ext}")

            for new_path in urls_to_try:
                new_url = f"{parsed_url['scheme']}://{parsed_url['netloc']}{new_path}{parsed_url['query']}{parsed_url['fragment']}"
                try:
                    response = requests.get(new_url, timeout=5)
                    if 200 <= response.status_code < 300:
                        self.result["language"] = lang
                        self.result["extension"] = ext
                        self.result["success_url"] = new_url
                        print(f"[FOUND] Programming language: {lang}")
                        print(f"[INFO] URL: {new_url}")
                        print("**********************************************************")
                        return self.result
                    else:
                        print(f"[INFO] {ext} extension failed with status {response.status_code}.")
                        print(f"[INFO] URL: {new_url}")

                except requests.RequestException as e:
                    print(f"[ERROR] Request failed for {new_url}: {e}")
                    continue

        print("[INFO] No valid extension found after trying all.")
        print("**********************************************************")
        return self.result


url = "http://10.10.10.18/shepherd/login.jsp"
url = "https://tr-wiki.metin2.gameforge.com/index/"
p = PageExtensionAnalyzer(url,"","","")
a = p.analyze()




