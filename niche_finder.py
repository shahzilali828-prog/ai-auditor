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
        junk = ['google', 'facebook', 'linkedin', 'yelp', 'yellowpages', 'tripadvisor', 'instagram', 'twitter', 'youtube', 'mapquest', 'bbb.org']
        
        # Using Google Search - more reliable than DDG right now
        search_url = f"https://www.google.com/search?q={query}&num={num_results + 10}"
        
        try:
            header = random.choice(self.headers)
            response = requests.get(search_url, headers=header, timeout=10)
            
            if response.status_code != 200:
                print(colored(f"[!] Search failed with status {response.status_code}. Retry in 5s...", "red"))
                time.sleep(5)
                # Try one more time with a different header
                header = random.choice(self.headers)
                response = requests.get(search_url, headers=header, timeout=10)
                if response.status_code != 200:
                    return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Google results are typically in <a> tags within <div>s
            # We look for links that look like business websites
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                # Google often wraps external links
                if href.startswith('/url?q='):
                    href = href.split('/url?q=')[1].split('&')[0]
                
                if not href.startswith('http') or 'google.com' in href:
                    continue

                # Clean the domain
                parsed = urlparse(href)
                domain = parsed.netloc.replace('www.', '')
                
                # Filter out junk and common directories slowing us down
                if domain and not any(j in domain for j in junk):
                    domains.add(domain)
                
                if len(domains) >= num_results:
                    break

            if not domains:
                # Fallback to a simpler regex if soup fails
                links = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', response.text)
                for link in links:
                    domain = urlparse(link).netloc.replace('www.', '')
                    if domain and not any(j in domain for j in junk) and 'google' not in domain:
                        domains.add(domain)
                        if len(domains) >= num_results: break

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
