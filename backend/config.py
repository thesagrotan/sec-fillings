import os

# SEC Configuration
# Defaults to a placeholder if not set, but should be set in production
SEC_USER_AGENT_NAME = os.getenv("SEC_USER_AGENT_NAME", "MyCompanyName")
SEC_USER_AGENT_EMAIL = os.getenv("SEC_USER_AGENT_EMAIL", "email@example.com")

# Industry Filtering
EXCLUDED_INDUSTRIES = [
    "Pooled Investment Fund",
    "REITS and Finance",
    "Oil and Gas",
    "Commercial",
    "Other Real Estate",
    "Real Estate",
    "Commercial Banking",
    "Insurance",
    "Investing",
    "Investment Banking",
    "Coal Mining",
    "Electric Utilities",
    "Construction",
    "Residential",
    "Restaurants"
]

# Web Search & Parsing
ATS_DOMAINS = [
    "geekhunter.com.b", "greenhouse.io", "lever.co", "ashbyhq.com", "workable.com", 
    "bamboohr.com", "breezy.hr", "applytojob.com", "recruitee.com", "smartrecruiters.com"
]

URL_BLOCKLIST = [
    'linkedin.com', 'crunchbase.com', 'bloomberg.com', 'facebook.com', 
    'instagram.com', 'twitter.com', 'wikipedia.org', 'exa.ai', 
    'zoominfo.com', 'dnb.com', 'ycombinator.com', 'pitchbook.com', 
    'cbinsights.com', 'zhihu.com', 'stackoverflow.com', 'github.com',
    'medium.com', 'substack.com', 'youtube.com', 'pinterest.com',
    'glassdoor.com', 'comparably.com', 'g2.com', 'capterra.com',
    'yahoo.com', 'finance.yahoo.com', 'businesswire.com', 'globenewswire.com',
    'marketwatch.com', 'cnbc.com', 'forbes.com', 'wsj.com', 'nytimes.com',
    'reuters.com', 'apnews.com', 'techcrunch.com', 'wired.com',
    'venturebeat.com', 'seekingalpha.com', 'investopedia.com',
    'sec.gov', 'edgar-online.com', 'sec.report',
    'microsoft.com', 'amazon.com', 'googleapis.com', 'docs.google.com'
]

# OpenRouter AI Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
