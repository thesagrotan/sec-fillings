
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ingestion import get_company_url

test_cases = [
    # Proven Tech Giants (Should work)
    {"name": "OpenAI", "city": "San Francisco", "state": "CA"},
    {"name": "Anthropic", "city": "San Francisco", "state": "CA"},
    
    # Common Names (Tricky)
    {"name": "Dove", "city": "Unknown", "state": "Unknown"}, # Is it soap or chocolate or something else?
    {"name": "Plaid", "city": "San Francisco", "state": "CA"},
    
    # Obscure / Fake-ish (Should return None or be very careful)
    {"name": "Xylophone Artificial Intelligence 44", "city": "Nowhere", "state": "KA"},
    
    # Private / Stealth (Might be hard)
    {"name": "Harvey", "city": "San Francisco", "state": "CA"},
    
    # User reported issue
    {"name": "AristaVue", "city": "Unknown", "state": "Unknown"},
    
    # Hypothetical triggers for "learn.microsoft.com"
    {"name": "Learn", "city": "Unknown", "state": "Unknown"},
    {"name": "Microsoft", "city": "Redmond", "state": "WA"},
]

print("Testing get_company_url with new strict logic...")
print("=" * 60)

for company in test_cases:
    print(f"Searching for: {company['name']} ({company.get('city')}, {company.get('state')})")
    try:
        url = get_company_url(company["name"], company.get("city"), company.get("state"))
        print(f"RESULT: {url}")
    except Exception as e:
        print(f"ERROR: {e}")
    print("-" * 60)

