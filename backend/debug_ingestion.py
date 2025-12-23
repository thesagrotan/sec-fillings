import requests
import xml.etree.ElementTree as ET
from sec_downloader import Downloader

# SEC FD (Form D) Atom Feed
SEC_FEED_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=D&company=&dateb=&owner=include&start=0&count=10&output=atom"

def debug_sec_feed():
    dl = Downloader("MyCompanyName", "email@example.com")
    headers = {"User-Agent": "MyCompanyName email@example.com"}
    response = requests.get(SEC_FEED_URL, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch SEC feed: {response.status_code}")
        return

    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = root.findall('atom:entry', ns)

    for entry in entries[:5]:
        title = entry.find('atom:title', ns).text
        print(f"Entry Title: {title}")
        
        link_href = entry.find('atom:link', ns).attrib['href']
        print(f"Link: {link_href}")
        
        try:
            metadatas = dl.get_filing_metadatas(link_href)
        except Exception as e:
            print(f"Skipping {link_href} due to error: {e}")
            continue
        if metadatas:
            metadata = metadatas[0]
            print(f"Metadata Company Name: {metadata.company_name}")
            print(f"Metadata CIK: {metadata.cik}")
            
            # Download HTML to see if name is inside
            html_content = dl.download_filing(url=metadata.primary_doc_url).decode('utf-8', errors='ignore')
            
            # Print a snippet of HTML to understand structure
            print(f"HTML Content Snippet: {html_content[:5000]}")

            # Use the actual parsing function
            from backend.ingestion import parse_form_d
            parsed_data = parse_form_d(html_content)
            print(f"Parsed Data: {parsed_data}")
            print(f"Extracted Issuer Name: {parsed_data.get('issuer_name')}")
            print(f"Extracted Amount Sold: {parsed_data.get('amount_sold')}")
            print(f"Extracted Jurisdiction: {parsed_data.get('jurisdiction')}")
            print(f"Extracted Executive: {parsed_data.get('executive_name')} ({parsed_data.get('executive_title')})")
            
            # Check for specific fields in HTML
            if "Name of Issuer" in html_content:
                print("Found 'Name of Issuer' in HTML")
            if "Entity Name" in html_content:
                print("Found 'Entity Name' in HTML")

if __name__ == "__main__":
    debug_sec_feed()
