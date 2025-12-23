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
import json
from contextlib import contextmanager
from .config import ATS_DOMAINS, URL_BLOCKLIST, SEC_USER_AGENT_NAME, SEC_USER_AGENT_EMAIL

def analyze_maturity(founded_year: str) -> dict:
    """
    Calculates age and maturity stage based on founded year.
    """
    if not founded_year or founded_year == "Unknown":
        return {"age": "Unknown", "stage": "Unknown", "is_early_stage": False}
    
    try:
        # Handle "On or before 2018"
        if "On or before" in founded_year:
            year = int(founded_year.split()[-1])
        else:
            year = int(founded_year)
            
        current_year = datetime.now().year
        age = current_year - year
        
        is_early_stage = age < 2
        
        if age < 1:
            stage = "Nascent"
        elif age < 3:
            stage = "Early-Stage"
        elif age < 7:
            stage = "Growth"
        else:
            stage = "Established"
            
        return {
            "age": age,
            "stage": stage,
            "is_early_stage": is_early_stage
        }
    except Exception:
        return {"age": "Unknown", "stage": "Unknown", "is_early_stage": False}

def analyze_funding(parsed_data: dict, description_text: str = "") -> dict:
    """
    Extracts funding details and infers execution bottlenecks.
    """
    details = {
        "grant_size": "Unknown",
        "bottlenecks": [],
        "milestones": []
    }
    
    # Simple extraction of implied bottlenecks based on keywords in description or industry
    # Logic: map industry/keywords to typical bottlenecks
    
    industry = parsed_data.get("industry", "")
    bottlenecks = []
    
    if "Technology" in industry or "Biotechnology" in industry:
        bottlenecks.append("Prototype Validation")
        bottlenecks.append("Commercialization")
    
    if "Healthcare" in industry:
        bottlenecks.append("Regulatory Approval")
        bottlenecks.append("Clinical Trials")
        
    revenue = parsed_data.get("revenue_range", "")
    if revenue in ["$1 - $1,000,000", "Decline to Disclose"]:
        bottlenecks.append("Early Customer Traction")
        
    details["bottlenecks"] = bottlenecks
    
    return details



def analyze_founders(executive_name: str) -> dict:
    """
    Analyzes founder background (technical vs design).
    """
    # Placeholder for real search. In a real app we'd trigger a servant agent 
    # to search GitHub/Scholar. For now we assume unknown or infer from title.
    
    technical_mapping = {
        "technical_score": 0,
        "design_score": 0,
        "likely_gaps": ["Design Leadership", "Product Vision"]
    }
    
    if not executive_name or executive_name == "Unknown":
        return technical_mapping
    
    # Simple heuristics on title if we had it, but here we only pass name sometimes.
    # In a real scenario we'd do a search like:
    # results = ddgs.text(f"{executive_name} linkedin github", max_results=5)
    # But to keep it fast and simple for this demo:
    
    return technical_mapping

def analyze_public_presence(website_url: str) -> dict:
    """
    Checks website availability and quality signals.
    """
    presence = {
        "website_status": "Missing", 
        "has_ui_artifacts": False,
        "quality_score": "Low"
    }
    
    if not website_url:
        return presence
    
    try:
        # We perform a quick HEAD request
        headers = {
            "User-Agent": f"{SEC_USER_AGENT_NAME} {SEC_USER_AGENT_EMAIL}"
        }
        resp = requests.head(website_url, headers=headers, timeout=5, allow_redirects=True)
        
        if resp.status_code < 400:
            presence["website_status"] = "Active"
            presence["quality_score"] = "Medium" # Default if active
            
            # If we were to read content we could check for "dashboard", "login", etc.
            # parsing content is expensive so maybe skip for now or do light check
            
    except Exception:
        presence["website_status"] = "Unreachable"

    return presence

def analyze_hiring_signal(careers_url: str, latest_filing_date: datetime.date) -> dict:
    """
    Compares hiring activity to funding.
    """
    signal = {
        "is_hiring": False,
        "hiring_velocity": "Unknown"
    }
    
    if careers_url:
        signal["is_hiring"] = True
        signal["hiring_velocity"] = "Active"
    else:
        # If recently funded but no careers, might be deferring
        if latest_filing_date:
            days_since_funding = (datetime.now().date() - latest_filing_date).days
            if days_since_funding < 90:
                 signal["hiring_velocity"] = "Deferring"
            else:
                 signal["hiring_velocity"] = "Stalled"
                 
    return signal

def infer_design_opportunity(maturity: dict, funding: dict, founders: dict, presence: dict, hiring: dict) -> dict:
    """
    Infers the specific design opportunity and actionable recommendation.
    """
    stage = maturity.get("stage", "Unknown")
    is_early = maturity.get("is_early_stage", False)
    bottlenecks = funding.get("bottlenecks", [])
    
    opportunity = {
        "phase": stage,
        "needs": [],
        "priority": "Medium"
    }
    
    recommendation = "Engage to explore general design support."
    
    # Logic Map
    if stage == "Nascent" or stage == "Early-Stage":
        opportunity["needs"] = ["Pitch Deck Design", "Conceptual Prototyping", "Grant Visuals"]
        recommendation = "Offer conceptual prototyping to visualize their initial vision for investors."
        
        if "Prototype Validation" in bottlenecks:
            opportunity["needs"].append("User Testing scaffolding")
            opportunity["priority"] = "High"
            recommendation = "Propose rapid prototyping to validate their core technology assumptions."
            
    elif stage == "Growth":
        opportunity["needs"] = ["Product UI Polish", "Design System", "Marketing Website"]
        recommendation = "Audit their current product UI for scalability and consistency."
        
        if presence.get("website_status") == "Missing" or presence.get("quality_score") == "Low":
             opportunity["needs"].append("Brand Identity")
             recommendation = "Pitch a complete brand and web presence overhaul to match their growth stage."
             
    elif stage == "Established":
        opportunity["needs"] = ["UX Research", "Accessibility Audit", "Enterprise Dashboarding"]
        recommendation = "Discuss optimizing complex workflows or enterprise-grade accessibility."

    if hiring.get("hiring_velocity") == "Deferring":
        # They have money but no team yet -> Augmentation
        opportunity["priority"] = "High"
        recommendation += " Position as an immediate design partner while they ramp up hiring."

    return {
        "design_opportunity": opportunity,
        "engagement_recommendation": recommendation
    }

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
        blocklist = URL_BLOCKLIST

        for r in results:
            link = r.get('href')
            if not link: continue
            
            domain = urlparse(link).netloc.lower()
            if domain.startswith("www."): domain = domain[4:]
            
            if any(b in domain for b in blocklist):
                continue
                
            # STRICT MATCHING ONLY
            # 1. Domain starts with normalized name
            if domain.startswith(normalized_name):
                 # Try verification
                 if verify_website_content(link, name):
                     return link
                 
                 # FALLBACK: If verification failed (maybe 403) but it's an EXACT match
                 # Only allowed if the domain parts are few (e.g. openai.com -> ['openai', 'com'])
                 # This prevents 'learn.microsoft.com' (parts=['learn', 'microsoft', 'com']) from matching 'Learn'
                 
                 parts = domain.split('.')
                 if len(parts) == 2:
                     if parts[0] == normalized_name:
                         return link
                         
                 # Special case for .co.uk etc? 
                 # If len is 3 and last two are short? e.g. google.co.uk
                 # Let's keep it simple and safe for now. 2 parts is best for strict fallback.
                 
            # 2. Normalized name matched inside? verification MUST pass.
            if normalized_name in domain:
                 if verify_website_content(link, name):
                     return link
                 # No fallback for loose matches. verification required.

        # REMOVED FALLBACK to first valid link
        # This was the cause of random websites.
        return None
        return None

    try:
        with DDGS() as ddgs:
            # 1. Simple query (Often best for exact matches)
            query = name
            results = list(ddgs.text(query, max_results=10, region='us-en'))
            found = process_results(results, name)
            if found: return found
            
            # 2. Specific query with location (if available)
            if city and city != "Unknown" and state and state != "Unknown":
                loc_query = f"{name} {city} {state} website"
                results = list(ddgs.text(loc_query, max_results=10, region='us-en'))
                found = process_results(results, name)
                if found: return found

            # 3. "Official Website" query as fallback
            simple_query = f"{name} official website"
            results = list(ddgs.text(simple_query, max_results=10, region='us-en'))
            return process_results(results, name)
                
    except Exception as e:
        print(f"Error searching for URL for {name}: {e}")
        return None
    return None

def verify_website_content(url: str, company_name: str) -> bool:
    """
    Verifies if the website content actually relates to the company.
    Checks title and h1 for fuzzy match of company name.
    Returns True if match confirmed.
    """
    try:
        # Use a more realistic browser User-Agent to avoid 403s
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=5)
        
        # If we get a 403/401, we can't verify, so we should assume False 
        # UNLESS the caller handles this case. But here we just return False.
        if resp.status_code >= 400:
            return False
            
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Check Title
        title = soup.title.string if soup.title else ""
        
        # Check H1
        h1 = soup.find('h1')
        h1_text = h1.get_text() if h1 else ""
        
        # Normalize for comparison
        normalized_name = company_name.lower().replace("inc", "").replace("llc", "").replace("corp", "").strip()
        normalized_name_parts = normalized_name.split()
        
        content_text = (title + " " + h1_text).lower()
        
        # Check if reasonably significant parts of the name appear
        # If name is "Acme Corp", "acme" should appear.
        # If name is "United Airlines", "united" might be too common, but let's try strict first.
        
        # Strategy: At least the first word (if > 3 chars) or full name if short
        match_score = 0
        for part in normalized_name_parts:
            if len(part) < 3: continue
            if part in content_text:
                match_score += 1
                
        if match_score > 0:
            return True
            
        return False
        
    except Exception:
        return False


def get_careers_url(name: str, website_url: str = None) -> str:
    """
    Searches for the company's careers/jobs page.
    Prioritizes direct website paths and known ATS providers.
    """
    if not name:
        return None

    headers = {
        "User-Agent": f"{SEC_USER_AGENT_NAME} {SEC_USER_AGENT_EMAIL}"
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
    
    ats_domains = ATS_DOMAINS

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10, region='us-en'))
            
            # Collect all valid links
            candidates = []
            blocklist = URL_BLOCKLIST
            
            for r in results:
                link = r.get('href')
                if not link: continue
                
                domain = urlparse(link).netloc.lower()
                if domain.startswith("www."): domain = domain[4:]
                
                if any(b in domain for b in blocklist):
                     # Exception: LinkedIn is okay for careers? 
                     # Actually, maybe we want LinkedIn for careers.
                     # But we definitely don't want "answers.microsoft.com"
                     
                     # Let's allow LinkedIn for careers but block others?
                     if "linkedin.com" in domain:
                         pass
                     else:
                         continue
                
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
    
            # Fallback? 
            # If we returned None for website, we probably shouldn't guess a random careers page unless it's a known ATS or LinkedIn.
            # Returning the first random link (like a news article or Q&A) is bad.
            
            # Stricter fallback:
            # Only return if it contains company name?
            normalized_name = name.lower().replace(" ", "")
            
            for link in candidates:
                # Check for strict ATS/Social match or domain match
                domain = urlparse(link).netloc.lower()
                
                # If it's a known ATS (covered above)
                
                # If it's LinkedIn, allow it (common for startups to only have LI)
                if "linkedin.com" in domain:
                    return link
                    
                # If domain matches company name strictly
                if normalized_name in domain.replace("-",""):
                    return link
                    
            return None
                
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
    # Initialize Downloader
    dl = Downloader(SEC_USER_AGENT_NAME, SEC_USER_AGENT_EMAIL)
    
    # Fetch Feed
    # Ensure we fetch enough entries from RSS
    rss_count = max(limit, 100) # Minimum 100 to be safe
    feed_url = f"{SEC_FEED_BASE_URL}&count={rss_count}"
    
    headers = {"User-Agent": f"{SEC_USER_AGENT_NAME} {SEC_USER_AGENT_EMAIL}"}
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

                # Run Intelligence Analysis
                maturity = analyze_maturity(parsed_data.get("founded_year"))
                funding = analyze_funding(parsed_data)
                founders = analyze_founders(parsed_data.get("executive_name"))
                presence = analyze_public_presence(website_url)
                hiring = analyze_hiring_signal(careers_url, datetime.strptime(metadata.filing_date, "%Y-%m-%d").date())
                
                opportunity_inference = infer_design_opportunity(maturity, funding, founders, presence, hiring)
                
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
                    careers_url=careers_url,
                    
                    # Intelligence Signals
                    maturity_info=json.dumps(maturity),
                    funding_details=json.dumps(funding),
                    founder_analysis=json.dumps(founders),
                    public_presence_quality=json.dumps(presence),
                    hiring_signal=json.dumps(hiring),
                    design_opportunity=json.dumps(opportunity_inference["design_opportunity"]),
                    engagement_recommendation=opportunity_inference["engagement_recommendation"]
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
