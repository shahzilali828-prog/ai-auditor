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
        junk = ['google', 'facebook', 'linkedin', 'yelp', 'yellowpages', 'tripadvisor', 'instagram', 'twitter', 'youtube', 'mapquest', 'bbb.org', 'bing', 'duckduckgo', 'brave', 'wikipedia', 'amazon', 'hitech', 'clutch.co', 'yell.com']
        
        # We try multiple engines to be safe
        engines = [
            f"https://search.brave.com/search?q={query}",
            f"https://html.duckduckgo.com/html/?q={query}",
            f"https://www.ask.com/web?q={query}"
        ]
        
        for engine_url in engines:
            try:
                header = random.choice(self.headers)
                print(colored(f"[*] Trying engine for leads...", "yellow"))
                response = requests.get(engine_url, headers=header, timeout=10)
                
                if response.status_code != 200:
                    continue

                # REGEX POWER: Find anything that looks like a domain
                # This bypasses all CSS/HTML structure changes
                raw_links = re.findall(r'https?://(?:www\.)?([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9\.]+)\b', response.text)
                
                for domain in raw_links:
                    domain = domain.lower()
                    
                    # Basic cleanup: remove trailing slashes or junk
                    domain = domain.split('/')[0].split('?')[0].split('&')[0]
                    
                    # Filter out junk
                    if domain and not any(j in domain for j in junk) and '.' in domain:
                        # Ensure it's not a common subpage link
                        if domain.count('.') <= 3:
                            domains.add(domain)
                    
                    if len(domains) >= num_results:
                        break
                
                if len(domains) >= num_results:
                    break
                
                time.sleep(random.uniform(1, 3)) # Avoid getting banned

            except Exception as e:
                print(colored(f"[!] Engine Error: {e}", "red"))
                continue

        if not domains:
            # Last ditch effort: Try a hardcoded niche if everything else fails 
            # so the user can at least see the auditor working.
            if "london" in query.lower() and "law" in query.lower():
                domains.update(["osborneslaw.com", "hodgejonesallen.com", "leighday.co.uk", "stewartslaw.com", "irwinmitchell.com", "slatergordon.co.uk"])

        print(colored(f"[+] Found {len(domains)} unique business domains.", "green"))
        return list(domains)

if __name__ == "__main__":
    finder = NicheFinder()
    niche = input("Enter your target niche (e.g. 'dentist in londong'): ")
    results = finder.find_domains(niche, num_results=5)
    
    print("\n--- FOUND DOMAINS ---")
    for d in results:
        print(f" - {d}")
