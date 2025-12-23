from backend.ingestion import get_careers_url

test_cases = [
    {"name": "Cultivo Land PBC", "url": "https://cultivo.land"},
    {"name": "Anthropic", "url": "https://www.anthropic.com"},
    {"name": "OpenAI", "url": "https://openai.com"},
    {"name": "Stripe", "url": "https://stripe.com"}
]

for test in test_cases:
    print(f"Testing {test['name']} ({test['url']})")
    careers = get_careers_url(test['name'], test['url'])
    print(f"Found: {careers}")
    print("-" * 20)
