from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .models import Base, engine, SessionLocal, Company
from .ingestion import ingest_filings

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
def trigger_ingest(limit: int = 10):
    """Trigger ingestion of latest Form D filings."""
    count = ingest_filings(limit=limit)
    return {"message": f"Ingested {count} filings"}

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
    db: SessionLocal = Depends(get_db)
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
    if revenue_range:
        query = query.filter(Company.revenue_range == revenue_range)
    if founded_year:
        query = query.filter(Company.founded_year == founded_year)

    if startup_mode:
        excluded_industries = [
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
        query = query.filter(Company.industry.notin_(excluded_industries))
    
    if days_ago is not None:
        from datetime import date, timedelta
        date_threshold = date.today() - timedelta(days=days_ago)
        query = query.filter(Company.latest_filing_date >= date_threshold)
        
    companies = query.order_by(Company.latest_filing_date.desc()).limit(limit).all()
    return companies
