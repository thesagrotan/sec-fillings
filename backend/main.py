from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import Base, engine, SessionLocal, Company
from .ingestion import ingest_filings
from .enrichment import enrich_company_profile, enrich_pending_companies
from .config import EXCLUDED_INDUSTRIES
from sqlalchemy.orm import Session

app = FastAPI(title="Startup Discovery API") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Startup Discovery API"}

@app.post("/ingest")
def trigger_ingest(limit: int = 10, background_tasks: BackgroundTasks = None):
    """Trigger ingestion of latest Form D filings and auto-enrich."""
    count = ingest_filings(limit=limit)
    
    # Automatically trigger AI enrichment for new companies
    if background_tasks and count > 0:
        background_tasks.add_task(enrich_pending_companies)
    
    return {"message": f"Ingested {count} filings", "enrichment_triggered": count > 0}

@app.post("/companies/{company_id}/enrich")
def trigger_enrichment(company_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger AI enrichment for a specific company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Reset status to pending if it was failed
    if company.enrichment_status == "failed":
        company.enrichment_status = "pending"
        db.commit()
    
    background_tasks.add_task(enrich_company_profile, company_id)
    return {"status": "processing", "company_id": company_id}

@app.get("/companies/{company_id}/enrichment-status")
def get_enrichment_status(company_id: int, db: Session = Depends(get_db)):
    """Get enrichment status for a specific company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {
        "company_id": company_id,
        "enrichment_status": company.enrichment_status or "pending"
    }

@app.post("/enrich-all")
def trigger_enrich_all(background_tasks: BackgroundTasks):
    """Trigger AI enrichment for all pending companies."""
    background_tasks.add_task(enrich_pending_companies)
    return {"status": "processing", "message": "Enrichment started for all pending companies"}

@app.get("/companies")
def get_companies(
    industry: str = None, 
    city: str = None, 
    state: str = None, 
    revenue_range: str = None,
    founded_year: str = None,
    limit: int = 100,
    days_ago: int = None,
    startup_mode: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Company)
    
    if industry:
        query = query.filter(Company.industry == industry)
    if city:
        query = query.filter(Company.city == city)
    if state:
        query = query.filter(Company.state == state)
    if revenue_range:
        query = query.filter(Company.revenue_range == revenue_range)
    if founded_year:
        query = query.filter(Company.founded_year == founded_year)

    if startup_mode:
        query = query.filter(Company.industry.notin_(EXCLUDED_INDUSTRIES))
    
    if days_ago is not None:
        from datetime import date, timedelta
        date_threshold = date.today() - timedelta(days=days_ago)
        query = query.filter(Company.latest_filing_date >= date_threshold)
        
    companies = query.order_by(Company.latest_filing_date.desc()).limit(limit).all()
    return companies
