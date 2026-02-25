import requests
def colored(text, color=None, on_color=None, attrs=None):
    return text
import re
from bs4 import BeautifulSoup

class LeadFinder:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.hunter_url = "https://api.hunter.io/v2/domain-search"

    def find_emails(self, domain):
        """
        Try Hunter.io first. If no key, fail over to Free Scraping.
        """
        if self.api_key:
            return self.find_with_hunter(domain)
        else:
            print(colored("[*] No API Key provided. Switching to FREE SCRAPER Mode...", "yellow"))
            return self.find_with_scraper(domain)

    def find_with_hunter(self, domain):
        print(f"[*] Hunting emails for: {domain} using Hunter.io...")
        params = {
            "domain": domain,
            "api_key": self.api_key,
            "type": "personal",
            "limit": 5
        }
        try:
            response = requests.get(self.hunter_url, params=params)
            if response.status_code == 200:
                data = response.json()
                emails = data.get("data", {}).get("emails", [])
                results = []
                for email in emails:
                    results.append({
                        "name": f"{email.get('first_name', '')} {email.get('last_name', '')}",
                        "email": email.get('value'),
                        "role": email.get('position', 'Unknown')
                    })
                return results
            else:
                print(colored(f"[!] Hunter Error: {response.status_code}. Switching to Scraper...", "red"))
                return self.find_with_scraper(domain)
        except Exception as e:
            return self.find_with_scraper(domain)

    def find_with_scraper(self, domain):
        """
        FREE METHOD: Scans homepage, discovers contact pages automatically, and extracts emails.
        """
        base_url = f"https://{domain}"
        found_emails = {}
        processed_urls = set()
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # Initial queue: Homepage and some guesses
        url_queue = [base_url, f"{base_url}/contact", f"{base_url}/about", f"{base_url}/legal"]
        
        print(f"[*] Starting Deep Search for: {domain}...")
        
        # Limits to prevent infinite loops
        max_pages = 8
        pages_crawled = 0
        
        while url_queue and pages_crawled < max_pages:
            url = url_queue.pop(0)
            if url in processed_urls:
                continue
            
            processed_urls.add(url)
            pages_crawled += 1
            print(f"    - Scanning: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')

                # 1. Discover more promising links (About, Contact, Team, Personnel)
                for a in soup.find_all('a', href=True):
                    href = a['href'].lower()
                    text = a.get_text().lower()
                    
                    # Resolve relative URLs
                    if href.startswith('/'):
                        href = f"{base_url}{href}"
                    elif not href.startswith('http'):
                        href = f"{base_url}/{href}"
                    
                    # Only follow links on the same domain
                    if domain in href:
                        # Prioritize pages likely to have emails
                        if any(k in href or k in text for k in ['contact', 'about', 'team', 'staff', 'people', 'legal', 'privacy']):
                            if href not in processed_urls and href not in url_queue:
                                url_queue.append(href)

                    # 2. Extract 'mailto:' links
                    if 'mailto:' in href:
                        email = href.replace('mailto:', '').split('?')[0].strip()
                        if "@" in email and '.' in email.split('@')[1]:
                            found_emails[email.lower()] = "Decision Maker"

                # 3. Regex Search in text
                text_content = soup.get_text()
                # Improved regex to avoid common false positives
                regex_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', text_content)
                
                for email in regex_emails:
                    email = email.lower().strip()
                    # Filter junk extensions
                    if any(email.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js']):
                        continue
                    
                    # Filter common generic "not an email" patterns
                    if "example.com" in email or "yourdomain" in email:
                        continue
                        
                    # Prioritize emails that likely belong to the domain
                    if domain.split('.')[0] in email or any(x in email for x in ['info@', 'contact@', 'hello@', 'support@', 'admin@', 'office@', 'sales@']):
                        if email not in found_emails:
                            found_emails[email] = "Decision Maker"

            except Exception:
                continue

        if found_emails:
            print(colored(f"[+] Found {len(found_emails)} unique emails for {domain}!", "green"))
            results = []
            for email, role in found_emails.items():
                results.append({"name": "Decision Maker", "email": email, "role": role})
            return results
        else:
            print(colored(f"[-] No leads found for {domain}.", "red"))
            return []

if __name__ == "__main__":
    print("\n--- LEAD FINDER (Hybrid Mode) ---")
    print("Tip: Press ENTER without a key to use the Free Scraper.")
    
    key = input("Enter Hunter.io Key (or press Enter for Free Mode): ").strip()
    target = input("Enter domain (e.g. stripe.com): ").strip()
    
    finder = LeadFinder(key if key else None)
    results = finder.find_emails(target)
    print(f"\n[Final Results] {results}")
