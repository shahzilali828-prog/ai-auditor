import os
from niche_finder import NicheFinder

def scale_discovery():
    finder = NicheFinder()
    niche = "personal injury lawyers new york"
    limit = 50 # Let's go big!
    
    print(f"[*] Starting High-Volume Search: {niche}")
    domains = finder.find_domains(niche, num_results=limit)
    
    output_file = os.path.join(os.path.dirname(__file__), "scale_leads.txt")
    with open(output_file, "w") as f:
        for domain in domains:
            f.write(f"{domain}\n")
    
    print(f"\n[SUCCESS] Found {len(domains)} targets.")
    print(f"[SUCCESS] Saved to: {output_file}")

if __name__ == "__main__":
    scale_discovery()
