import requests
from duckduckgo_search import DDGS
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from datetime import datetime
from .models import SessionLocal, Company
from sec_downloader import Downloader
from bs4 import BeautifulSoup
import re
import time

# SEC FD (Form D) Atom Feed Base URL
SEC_FEED_BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=D&company=&dateb=&owner=include&start=0&output=atom"

def get_company_url(name: str, city: str = None, state: str = None) -> str:
    """
    Searches for the company's website URL using DuckDuckGo (via duckduckgo_search).
    """
    if not name:
        return None
        
    # Construct query without "Unknown"
    query_parts = [name]
    if city and city != "Unknown":
        query_parts.append(city)
    if state and state != "Unknown":
        query_parts.append(state)
    query_parts.append("official website")
    
    query = " ".join(query_parts)
    
    def process_results(results, name):
        # improved normalization
        normalized_name = name.lower()
        for suffix in [" inc", " llc", " corp", " ltd", " co", "."]:
            normalized_name = normalized_name.replace(suffix, "")
        normalized_name = normalized_name.replace(" ", "").replace(",", "")

        # Blocklist
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
            
            if any(b in domain for b in blocklist):
                continue
                
            # Strong match
            if domain.startswith(normalized_name):
                 return link
            
            # match inside
            if normalized_name in domain:
                return link

        # Fallback to first valid
        for r in results:
            link = r.get('href')
            if not link: continue
            domain = urlparse(link).netloc.lower()
            if any(b in domain for b in blocklist):
                continue
            return link
        return None

    try:
        with DDGS() as ddgs:
            # 1. Specific query
            results = list(ddgs.text(query, max_results=10, region='us-en'))
            found = process_results(results, name)
            if found: return found
            
            # 2. Broad query
            simple_query = f"{name} official website"
            results = list(ddgs.text(simple_query, max_results=10, region='us-en'))
            return process_results(results, name)
                
    except Exception as e:
        print(f"Error searching for URL for {name}: {e}")
        return None


def get_careers_url(name: str, website_url: str = None) -> str:
    """
    Searches for the company's careers/jobs page.
    Prioritizes direct website paths and known ATS providers.
    """
    if not name:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 1. Direct Probing
    if website_url:
        common_paths = [
            "/careers", "/jobs", "/join-us", "/work-with-us", "/about/careers", "/company/careers"
        ]
        
        base_url = website_url.rstrip("/")
        for path in common_paths:
            probe_url = f"{base_url}{path}"
            try:
                # Use HEAD request for speed, fallback to GET if needed
                resp = requests.head(probe_url, headers=headers, timeout=3, allow_redirects=True)
                if resp.status_code == 200:
                    return probe_url
            except Exception:
                pass
    
    # 2. Search Engine Search
    query = f"{name} careers jobs"
    
    ats_domains = [
        "geekhunter.com.b", "greenhouse.io", "lever.co", "ashbyhq.com", "workable.com", 
        "bamboohr.com", "breezy.hr", "applytojob.com", "recruitee.com", "smartrecruiters.com"
    ]

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10, region='us-en'))
            
            # Collect all valid links
            candidates = []
            for r in results:
                link = r.get('href')
                if link and link.startswith('http'):
                    candidates.append(link)

            # Prioritize ATS domains
            for link in candidates:
                if any(ats in link for ats in ats_domains):
                    return link
            
            # If no ATS link, prioritize links on the company's own domain if known
            if website_url:
                try:
                    company_domain = urlparse(website_url).netloc.replace("www.", "")
                    for link in candidates:
                         if company_domain in link and ("/careers" in link or "/jobs" in link):
                             return link
                except:
                    pass
    
            # Fallback to the first result
            if candidates:
                return candidates[0]
                
    except Exception as e:
        print(f"Error searching for Careers URL for {name}: {e}")
        return None
    return None

def parse_form_d(content: str) -> dict:
    """
    Parses Form D HTML/XML content to extract metadata.
    """
    data = {
        "issuer_name": None,
        "city": "Unknown",
        "state": "Unknown",
        "industry": "Unknown",
        "founded_year": "Unknown",
        "revenue_range": "Unknown",
        "amount_sold": "Unknown",
        "jurisdiction": "Unknown",
        "executive_name": "Unknown",
        "executive_title": "Unknown"
    }
    
    # Try XML parsing first for structured data
    try:
        xml_content = content.strip()
        root = ET.fromstring(xml_content)
        
        def get_text(element, path):
            found = element.find(path)
            if found is not None and found.text:
                return found.text.strip()
            return None

        # Issuer Name
        issuer_name = get_text(root, ".//primaryIssuer/entityName")
        if issuer_name:
            data["issuer_name"] = issuer_name
            
        # City
        city = get_text(root, ".//primaryIssuer/issuerAddress/city")
        if city:
            data["city"] = city
            
        # State
        state = get_text(root, ".//primaryIssuer/issuerAddress/stateOrCountry")
        if state:
            data["state"] = state
            
        # Founded Year
        founded_year = get_text(root, ".//primaryIssuer/yearOfInc/value")
        if founded_year:
            data["founded_year"] = founded_year
            
        # Industry
        industry = get_text(root, ".//offeringData/industryGroup/industryGroupType")
        if industry:
            data["industry"] = industry
            
        # Revenue Range
        revenue_range = get_text(root, ".//offeringData/issuerSize/revenueRange")
        if not revenue_range:
             revenue_range = get_text(root, ".//offeringData/issuerSize/aggregateNetAssetValueRange")

        if revenue_range:
            data["revenue_range"] = revenue_range

        # Amount Sold
        amount_sold = get_text(root, ".//offeringData/offeringSalesAmounts/totalAmountSold")
        if amount_sold:
            data["amount_sold"] = amount_sold

        # Jurisdiction
        jurisdiction = get_text(root, ".//primaryIssuer/jurisdictionOfInc")
        if jurisdiction:
            data["jurisdiction"] = jurisdiction

        # Executive Name and Title
        related_person = root.find(".//relatedPersonsList/relatedPersonInfo")
        if related_person is not None:
            first_name = get_text(related_person, "relatedPersonName/firstName")
            last_name = get_text(related_person, "relatedPersonName/lastName")
            if first_name or last_name:
                data["executive_name"] = f"{first_name or ''} {last_name or ''}".strip()
            
            title = get_text(related_person, "relatedPersonRelationshipList/relationship")
            if title:
                data["executive_title"] = title
            
        return data

    except ET.ParseError:
        pass

    soup = BeautifulSoup(content, 'html.parser')

    text_content = soup.get_text(" ", strip=True)

    # Industry
    industries = ["Technology", "Healthcare", "Energy", "Retailing", "Biotechnology", 
                  "Commercial Banking", "Telecommunications", "Real Estate", "Manufacturing"]
    
    for ind in industries:
        if ind in text_content:
            data["industry"] = ind
            break

    # Revenue Range
    revenue_ranges = [
        "$1 - $1,000,000", "$1,000,001 - $5,000,000", "$5,000,001 - $25,000,000",
        "$25,000,001 - $100,000,000", "Over $100,000,000", "Decline to Disclose"
    ]
    for rev in revenue_ranges:
        if rev in text_content:
            data["revenue_range"] = rev
            break
            
    # City and State
    try:
        for tag in soup.find_all(['td', 'span', 'div']):
            text = tag.get_text(strip=True)
            if "City" == text or "City of Principal Place of Business" in text:
                next_tag = tag.find_next(string=True).find_next(string=True)
                if next_tag:
                    data["city"] = next_tag.strip()
            
            if "State" in text and "Country" in text: 
                 next_tag = tag.find_next(string=True).find_next(string=True)
                 if next_tag:
                     data["state"] = next_tag.strip()
    except:
        pass

    # Year of Incorporation/Organization
    if "Year of Incorporation/Organization" in text_content:
         if "Over Five Years Ago" in text_content:
             data["founded_year"] = "On or before 2018"
         else:
             year_match = re.search(r'(20\d{2}|19\d{2})', text_content)
             if year_match:
                 data["founded_year"] = year_match.group(1)

    return data

def ingest_filings(limit: int = 10):
    """
    Fetches recent Form D filings from SEC RSS feed,
    downloads details using sec-downloader,
    and saves new companies to the DB.
    """
    # Initialize Downloader
    dl = Downloader("MyCompanyName", "email@example.com")
    
    # Fetch Feed
    # Ensure we fetch enough entries from RSS
    rss_count = max(limit, 100) # Minimum 100 to be safe
    feed_url = f"{SEC_FEED_BASE_URL}&count={rss_count}"
    
    headers = {"User-Agent": "MyCompanyName email@example.com"}
    response = requests.get(feed_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch SEC feed: {response.status_code}")
        return 0

    root = ET.fromstring(response.content)
    # Atom feed namespace
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    entries = root.findall('atom:entry', ns)
    
    db = SessionLocal()
    count = 0
    
    for entry in entries[:limit]:
        link_href = entry.find('atom:link', ns).attrib['href']
        
        try:
            metadatas = dl.get_filing_metadatas(link_href)
            if not metadatas:
                continue
            
            metadata = metadatas[0]
            
            existing = db.query(Company).filter(Company.cik == metadata.cik).first()
            if not existing:
                try:
                    html_content = dl.download_filing(url=metadata.primary_doc_url).decode('utf-8', errors='ignore')
                    parsed_data = parse_form_d(html_content)
                except Exception as e:
                    print(f"Failed to download/parse HTML for {metadata.cik}: {e}")
                    parsed_data = {
                        "issuer_name": None,
                        "city": "Unknown",
                        "state": "Unknown",
                        "industry": "Unknown",
                        "founded_year": "Unknown",
                        "revenue_range": "Unknown",
                        "amount_sold": "Unknown",
                        "jurisdiction": "Unknown",
                        "executive_name": "Unknown",
                        "executive_title": "Unknown"
                    }

                # Retrieve website URL
                company_name = parsed_data.get("issuer_name") or metadata.company_name
                website_url = get_company_url(company_name, parsed_data.get("city"), parsed_data.get("state"))
                
                # Sleep to respect rate limits
                time.sleep(1) 
                
                # Retrieve Careers URL
                careers_url = get_careers_url(company_name, website_url)
                
                # Sleep to respect rate limits
                time.sleep(1)

                company = Company(
                    cik=metadata.cik,
                    name=company_name,
                    latest_filing_date=datetime.strptime(metadata.filing_date, "%Y-%m-%d").date(),
                    industry=parsed_data["industry"], 
                    city=parsed_data["city"],
                    state=parsed_data["state"],
                    founded_year=parsed_data["founded_year"],
                    revenue_range=parsed_data["revenue_range"],
                    amount_sold=parsed_data["amount_sold"],
                    jurisdiction=parsed_data["jurisdiction"],
                    executive_name=parsed_data["executive_name"],
                    executive_title=parsed_data["executive_title"],
                    website_url=website_url,
                    careers_url=careers_url
                )
                db.add(company)
                count += 1
            else:
                existing.latest_filing_date = datetime.strptime(metadata.filing_date, "%Y-%m-%d").date()
                if not existing.careers_url:
                     company_name = existing.name
                     website_url = existing.website_url
                     careers_url = get_careers_url(company_name, website_url)
                     existing.careers_url = careers_url
                     time.sleep(1) 

        
        except Exception as e:
            print(f"Error processing {link_href}: {e}")
            continue

    db.commit()
    db.close()
    return count
