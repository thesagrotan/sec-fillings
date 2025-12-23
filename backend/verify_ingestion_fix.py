
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ingestion import get_company_url, get_careers_url

companies = [
    {"name": "OpenAI", "city": "San Francisco", "state": "CA"},
    {"name": "Anthropic", "city": "San Francisco", "state": "CA"},
]

print("Verifying backend/ingestion.py functions...")
for c in companies:
    print(f"Testing {c['name']}...")
    url = get_company_url(c["name"], c["city"], c["state"])
    print(f"  Website URL: {url}")
    
    if url:
        careers = get_careers_url(c["name"], url)
        print(f"  Careers URL: {careers}")
    print("-" * 20)
