import requests
from bs4 import BeautifulSoup
import time
import random
import re
from termcolor import colored
from urllib.parse import urlparse

class NicheFinder:
    def __init__(self):
        self.headers = [
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'},
            {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
        ]

    def find_domains(self, query, num_results=10):
        print(colored(f"[*] Searching for niche: '{query}'...", "cyan"))
        domains = set()
        
        # Using DuckDuckGo Lite version - more scraper friendly
        search_url = f"https://lite.duckduckgo.com/lite/?q={query}"
        
        try:
            header = random.choice(self.headers)
            response = requests.get(search_url, headers=header, timeout=10)
            
            if response.status_code != 200:
                print(colored(f"[!] Search failed with status {response.status_code}", "red"))
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            # DuckDuckGo Lite uses <a> tags with class 'result-link' or just inside table rows
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href']
                
                # Filter out internal DDG links
                if "/l/?kh=" in href:
                    # DDG dynamic link - extract the actual URL
                    from urllib.parse import unquote
                    match = re.search(r'uddg=([^&]+)', href)
                    if match:
                        href = unquote(match.group(1))

                if not href.startswith('http'):
                    continue

                # Clean the domain
                parsed = urlparse(href)
                domain = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
                domain = domain.replace('www.', '')
                
                # Basic filter for common junk domains
                junk = ['duckduckgo.com', 'google.com', 'facebook.com', 'linkedin.com', 'yelp.com', 'yellowpages.com', 'tripadvisor.com', 'instagram.com', 'twitter.com']
                if domain and not any(j in domain for j in junk):
                    domains.add(domain)
                
                if len(domains) >= num_results:
                    break

            print(colored(f"[+] Found {len(domains)} unique business domains.", "green"))
            return list(domains)

        except Exception as e:
            print(colored(f"[!] Niche Finder Error: {e}", "red"))
            return []

if __name__ == "__main__":
    finder = NicheFinder()
    niche = input("Enter your target niche (e.g. 'dentist in londong'): ")
    results = finder.find_domains(niche, num_results=5)
    
    print("\n--- FOUND DOMAINS ---")
    for d in results:
        print(f" - {d}")
