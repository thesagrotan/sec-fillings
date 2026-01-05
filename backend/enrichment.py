"""
AI Enrichment module using OpenRouter API.
Provides async background enrichment of company profiles.
"""
import httpx
import json
from .models import SessionLocal, Company
from .config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL


def build_enrichment_prompt(company: Company) -> str:
    """
    Constructs a structured prompt for AI enrichment using company data.
    """
    # Parse existing JSON fields
    maturity = json.loads(company.maturity_info) if company.maturity_info else {}
    funding = json.loads(company.funding_details) if company.funding_details else {}
    hiring = json.loads(company.hiring_signal) if company.hiring_signal else {}
    presence = json.loads(company.public_presence_quality) if company.public_presence_quality else {}
    opportunity = json.loads(company.design_opportunity) if company.design_opportunity else {}
    
    prompt = f"""You are a business intelligence analyst specializing in startup evaluation and design opportunities.

Analyze the following company and provide enhanced insights for a design agency looking to engage with them.

## Company Profile
- **Name**: {company.name}
- **Location**: {company.city}, {company.state}
- **Industry**: {company.industry}
- **Founded**: {company.founded_year}
- **Revenue Range**: {company.revenue_range}
- **Amount Raised**: {company.amount_sold}
- **Executive**: {company.executive_name} ({company.executive_title})
- **Website**: {company.website_url or 'Not available'}
- **Careers Page**: {company.careers_url or 'Not available'}

## Current Intelligence
- **Maturity Stage**: {maturity.get('stage', 'Unknown')} (Age: {maturity.get('age', 'Unknown')} years)
- **Hiring Velocity**: {hiring.get('hiring_velocity', 'Unknown')}
- **Web Presence Quality**: {presence.get('quality_score', 'Unknown')}
- **Current Priority**: {opportunity.get('priority', 'Medium')}
- **Identified Needs**: {', '.join(opportunity.get('needs', [])) or 'None identified'}
- **Current Bottlenecks**: {', '.join(funding.get('bottlenecks', [])) or 'None detected'}

## Your Task
Provide a JSON response with the following structure:
{{
    "founder_insights": "Brief analysis of the founder/executive background and what it implies for their design needs",
    "market_positioning": "Assessment of their market position and competitive landscape implications",
    "design_opportunities": ["List of 3-5 specific design opportunities"],
    "engagement_strategy": "A refined, actionable recommendation for how a design agency should approach this company",
    "confidence_score": "high/medium/low based on data quality",
    "key_questions": ["2-3 questions to ask in initial outreach"]
}}

Respond ONLY with valid JSON, no additional text."""

    return prompt


def call_openrouter_api(prompt: str) -> dict:
    """
    Makes synchronous HTTP POST request to OpenRouter API.
    Returns parsed JSON response or error dict.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://startup-discovery.local",
        "X-Title": "Startup Discovery AI Enrichment"
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"}
    }
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # Parse the AI response
            return json.loads(content)
            
    except httpx.HTTPStatusError as e:
        print(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        print(f"Failed to parse AI response: {e}")
        return {"error": "Invalid JSON response from AI"}
    except Exception as e:
        print(f"OpenRouter API call failed: {e}")
        return {"error": str(e)}


def enrich_company_profile(company_id: int):
    """
    Main enrichment function that processes a single company.
    Updates the company record with AI-generated insights.
    """
    db = SessionLocal()
    
    try:
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            print(f"Company {company_id} not found")
            return
        
        # Set status to processing
        company.enrichment_status = "processing"
        db.commit()
        
        # Build prompt and call AI
        prompt = build_enrichment_prompt(company)
        ai_response = call_openrouter_api(prompt)
        
        if "error" in ai_response:
            company.enrichment_status = "failed"
            db.commit()
            print(f"Enrichment failed for company {company_id}: {ai_response['error']}")
            return
        
        # Update company with enriched data
        # Merge AI insights into existing design_opportunity
        existing_opportunity = json.loads(company.design_opportunity) if company.design_opportunity else {}
        
        enriched_opportunity = {
            **existing_opportunity,
            "ai_design_opportunities": ai_response.get("design_opportunities", []),
            "founder_insights": ai_response.get("founder_insights", ""),
            "market_positioning": ai_response.get("market_positioning", ""),
            "confidence_score": ai_response.get("confidence_score", "medium"),
            "key_questions": ai_response.get("key_questions", [])
        }
        
        company.design_opportunity = json.dumps(enriched_opportunity)
        
        # Update engagement recommendation with AI-enhanced strategy
        if ai_response.get("engagement_strategy"):
            company.engagement_recommendation = ai_response["engagement_strategy"]
        
        company.enrichment_status = "completed"
        db.commit()
        
        print(f"Successfully enriched company {company_id}: {company.name}")
        
    except Exception as e:
        print(f"Error enriching company {company_id}: {e}")
        try:
            company = db.query(Company).filter(Company.id == company_id).first()
            if company:
                company.enrichment_status = "failed"
                db.commit()
        except:
            pass
    finally:
        db.close()


def enrich_pending_companies():
    """
    Enriches all companies with pending status.
    Called as a background task after ingestion.
    """
    db = SessionLocal()
    
    try:
        pending_companies = db.query(Company).filter(
            Company.enrichment_status == "pending"
        ).all()
        
        company_ids = [c.id for c in pending_companies]
        
    finally:
        db.close()
    
    print(f"Starting enrichment for {len(company_ids)} companies...")
    
    for company_id in company_ids:
        enrich_company_profile(company_id)
    
    print(f"Completed enrichment batch of {len(company_ids)} companies")
