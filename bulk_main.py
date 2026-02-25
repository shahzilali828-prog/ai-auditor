import time
import csv
import os
from termcolor import colored
from scanner import GDPRScanner
from lead_finder import LeadFinder
from auto_emailer import AutoEmailer
from niche_finder import NicheFinder
from templates import get_ceo_templates

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "outreach_history.csv")
EMAIL_DELAY = 60 # Seconds between emails to avoid spam filters

def log_to_history(domain, status, emails_found, email_sent):
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Domain", "Status", "Emails Found", "Email Sent"])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), domain, status, emails_found, email_sent])

def is_already_contacted(domain):
    if not os.path.isfile(HISTORY_FILE):
        return False
    with open(HISTORY_FILE, mode='r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[1] == domain:
                return True
    return False

def main():
    print(colored("\n=================================================", "cyan", attrs=['bold']))
    print(colored("   AI AUDITOR - BULK AUTOMATION ENGINE v1.0", "cyan", attrs=['bold']))
    print(colored("=================================================\n", "cyan", attrs=['bold']))

    # 1. Setup
    print(colored("[1] Target Selection", "yellow"))
    print("1. Discovery Mode (Search a Niche)")
    print("2. Import Mode (Load from domains.txt)")
    print("3. CEO MODE (High-Ticket Industries)")
    choice = input("Select mode (1/2/3): ").strip()
    
    domains = []
    if choice == '1':
        niche = input("Enter target niche (e.g. 'lawyers in london'): ").strip()
        limit = int(input("How many businesses to target? (e.g. 10): ") or 10)
        finder = NicheFinder()
        domains = finder.find_domains(niche, num_results=limit)
    elif choice == '3':
        finder = NicheFinder()
        niches = finder.get_premium_niches()
        print(colored("\n--- SELECT HIGH-TICKET INDUSTRY ---", "cyan"))
        for k, v in niches.items():
            print(f"{k}. {v['name']}")
        
        cat_id = input("Select Industry (1-3): ").strip()
        if cat_id in niches:
            niche_info = niches[cat_id]
            print(colored(f"\n[CEO TIP] {niche_info['tip']}", "magenta", attrs=['bold']))
            print(colored("[PRICE GOAL] Target $1,250 - $4,500 per Audit.", "green", attrs=['bold']))
            
            query = finder.generate_premium_query(cat_id)
            limit = int(input(f"Targeting '{query}'. How many results? (default 10): ") or 10)
            domains = finder.find_domains(query, num_results=limit)
    else:
        # Use absolute path to ensure file is found regardless of execution directory
        file_path = os.path.join(BASE_DIR, "domains.txt")
        if not os.path.isfile(file_path):
            print(colored(f"[-] {file_path} not found. Create it with one domain per line.", "red"))
            return
        with open(file_path, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        print(colored(f"[+] Loaded {len(domains)} domains from {file_path}", "green"))

    if not domains:
        print(colored("[-] No domains found to process.", "red"))
        return

    run_email_mode = input("\nDo you want to send REAL emails? (y/n): ").lower()
    
    # 3. Initialize Components
    scanner = GDPRScanner()
    lead_finder = LeadFinder() # Using Free Scraper by default
    emailer = None
    
    sender_name = "AI Compliance Auditor"
    if run_email_mode == 'y':
        sender_name = input("Enter your Professional Sender Name (e.g. 'Shahzil | AI Auditor'): ").strip() or "AI Compliance Auditor"
        sender_email = input("Enter your sender email (Gmail recommended): ").strip()
        sender_pass = input("Enter your App Password (16 characters): ").strip().replace(" ", "")
        emailer = AutoEmailer("smtp.gmail.com", 587, sender_email, sender_pass)

    ceo_mode = (choice == '3')
    use_templates = None
    if ceo_mode:
        use_templates = get_ceo_templates()
        print(colored("\n--- SELECT CEO PITCH TEMPLATE ---", "cyan"))
        # Show keys
        template_keys = list(use_templates.keys())
        for i, k in enumerate(template_keys):
            print(f"{i+1}. {k.capitalize()} Template")
        t_choice = int(input("Select Template # (default 1): ") or 1) - 1
        selected_template_key = template_keys[t_choice]
        selected_template = use_templates[selected_template_key]
        print(colored(f"[+] Using {selected_template_key} pitch.", "green"))

    ignore_history = input("\n[DEBUG] Ignore history and rescan everything? (y/n): ").lower() == 'y'

    print(colored(f"\n[*] Starting Bulk Run on {len(domains)} targets...", "yellow"))
    
    for i, domain in enumerate(domains):
        print(colored(f"\n[{i+1}/{len(domains)}] Processing: {domain}", "blue", attrs=['bold']))
        
        if not ignore_history and is_already_contacted(domain):
            print(colored(f"[-] Already contacted {domain}. Skipping.", "yellow"))
            continue

        # Step A: Scan
        scan_result = scanner.audit_site(f"https://{domain}")
        if scan_result["status"] == "SECURE":
            log_to_history(domain, "SECURE", 0, False)
            continue
        
        if scan_result["status"] == "ERROR":
            print(colored(f"[!] Could not scan {domain}: {', '.join(scan_result.get('errors', []))}", "red"))
            continue

        # Step B: Find Leads
        leads = lead_finder.find_emails(domain)
        if not leads:
            log_to_history(domain, "VULNERABLE (No Leads)", 0, False)
            continue
        
        # Step C: Email
        email_sent = False
        if emailer:
            # For simplicity, we pitch the first lead found
            target_email = leads[0]['email']
            target_name = leads[0]['name'] or "Business Owner"
            print(colored(f"[*] Pitching: {target_email}", "cyan"))
            
            # CEO MODE OVERRIDE
            if ceo_mode and selected_template:
                subj = selected_template['subject'].format(domain=domain)
                body = selected_template['body'].format(name=target_name, domain=domain, sender_name=sender_name)
                success = emailer.send_pitch(target_email, target_name, domain, from_name=sender_name, subject=subj, body=body)
            else:
                success = emailer.send_pitch(target_email, target_name, domain, from_name=sender_name)
            
            if success:
                email_sent = True
                print(colored(f"[+] Email sent successfully!", "green"))
                # Delay to prevent spam flags
                if i < len(domains) - 1:
                    print(f"[*] Sleeping for {EMAIL_DELAY}s...")
                    time.sleep(EMAIL_DELAY)
            else:
                print(colored(f"[!] Failed to send email.", "red"))
        else:
            print(colored(f"[DEMO] Would have emailed: {leads[0]['email']}", "white"))

        # Step D: Log
        log_to_history(domain, "VULNERABLE", len(leads), email_sent)

    print(colored("\n=================================================", "cyan"))
    print(colored("   BULK RUN COMPLETE. CHECK THE LOGS.", "cyan"))
    print(colored("=================================================", "cyan"))

if __name__ == "__main__":
    main()
