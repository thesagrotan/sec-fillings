

import requests
from bs4 import BeautifulSoup
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from duckduckgo_search import DDGS

    
def debug_get_company_url(name: str, city: str = None, state: str = None) -> str:
    # Construct query without "Unknown"
    query_parts = [name]
    if city and city != "Unknown":
        query_parts.append(city)
    if state and state != "Unknown":
        query_parts.append(state)
    query_parts.append("official website")
    
    query = " ".join(query_parts)
    
    # 1. Try specific query with location
    found_link = None
    try:
        print(f"DEBUG: Searching with query: {query}")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10, region='us-en'))
        
        found_link = process_results(results, name)
        
        # 2. If no good result, try broader query (Name + official website)
        if not found_link:
             print("DEBUG: No good result with location, trying broader query...")
             simple_query = f"{name} official website"
             with DDGS() as ddgs:
                results = list(ddgs.text(simple_query, max_results=10, region='us-en'))
             found_link = process_results(results, name)
             
    except Exception as e:
        print(f"Error searching for URL for {name}: {e}")
        return None
        
    return found_link

def process_results(results, name):
    from urllib.parse import urlparse
    
    # improved normalization
    normalized_name = name.lower()
    for suffix in [" inc", " llc", " corp", " ltd", " co", "."]:
        normalized_name = normalized_name.replace(suffix, "")
    normalized_name = normalized_name.replace(" ", "").replace(",", "")
    print(f"DEBUG: Normalized name: {normalized_name}")

    # Extended blocklist
    blocklist = [
        'linkedin.com', 'crunchbase.com', 'bloomberg.com', 'facebook.com', 
        'instagram.com', 'twitter.com', 'wikipedia.org', 'exa.ai', 
        'zoominfo.com', 'dnb.com', 'ycombinator.com', 'pitchbook.com', 
        'cbinsights.com', 'zhihu.com', 'stackoverflow.com', 'github.com',
        'medium.com', 'substack.com', 'youtube.com', 'pinterest.com',
        'glassdoor.com', 'comparably.com', 'g2.com', 'capterra.com'
    ]

    for r in results:
        link = r.get('href')
        if not link: continue
        
        domain = urlparse(link).netloc.lower()
        if domain.startswith("www."): domain = domain[4:]
        
        print(f"DEBUG: Checking candidate: {link} (Domain: {domain})")

        if any(b in domain for b in blocklist):
            print(f"DEBUG: Blocklisted: {domain}")
            continue
            
        # Strong match: domain starts with company name
        if domain.startswith(normalized_name):
             print(f"DEBUG: Strong match found: {link}")
             return link
        
        # match inside
        if normalized_name in domain:
            print(f"DEBUG: Weak match found inside domain: {link}")
            return link

    # Return first non-blocked if nothing else matches (dangerous but maybe necessary?)
    # Only if we are fairly sure? For now let's be strict and maybe return None if no domain match?
    # Actually, let's allow it but be careful.
    for r in results:
        link = r.get('href')
        if not link: continue
        domain = urlparse(link).netloc.lower()
        
        if any(b in domain for b in blocklist):
            continue
        
        print(f"DEBUG: Returning first valid non-blocked link: {link}")
        return link
    
    return None

test_cases = [
    {"name": "OpenAI", "city": "San Francisco", "state": "CA"},
    {"name": "Anthropic", "city": "San Francisco", "state": "CA"},
    {"name": "Vercel", "city": "Walnut", "state": "CA"},
    {"name": "Stripe", "city": "South San Francisco", "state": "CA"},
    {"name": "SpaceX", "city": "Hawthorne", "state": "Unknown"},
]

print("Testing debug_get_company_url...")
for company in test_cases:
    print(f"Searching for: {company['name']} ({company['city']}, {company['state']})")
    url = debug_get_company_url(company["name"], company.get("city"), company.get("state"))
    print(f"Found URL: {url}")
    print("-" * 20)

