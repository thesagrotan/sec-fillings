
import sys
import os
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models import SessionLocal, Company, engine
from backend.ingestion import get_company_url, get_careers_url, analyze_public_presence
import json

def fix_all_companies():
    db = SessionLocal()
    try:
        companies = db.query(Company).filter(Company.name.ilike("%EPEP IV%")).all()
        print(f"Found {len(companies)} companies with URLs to check/fix.")
        
        for company in companies:
            print(f"Processing {company.name}...")
            
            # Reset website
            new_url = get_company_url(company.name, company.city, company.state)
            
            if new_url != company.website_url:
                print(f"  [UPDATE] Website: {company.website_url} -> {new_url}")
                company.website_url = new_url
                
                # If website changed, re-check valid presence
                presence = analyze_public_presence(new_url)
                company.public_presence_quality = json.dumps(presence)
                
                # And re-check careers if we have a new website
                new_careers = get_careers_url(company.name, new_url)
                if new_careers != company.careers_url:
                     print(f"  [UPDATE] Careers: {company.careers_url} -> {new_careers}")
                     company.careers_url = new_careers
            else:
                print(f"  [KEEP] Website {company.website_url} is still the best match (or None).")
                # Also check careers if website didn't change (might have bad careers link)
                new_careers = get_careers_url(company.name, new_url)
                if new_careers != company.careers_url:
                     print(f"  [UPDATE] Careers: {company.careers_url} -> {new_careers}")
                     company.careers_url = new_careers
                
            db.commit()
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_companies()
