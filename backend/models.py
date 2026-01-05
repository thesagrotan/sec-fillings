from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./companies.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    cik = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    city = Column(String)
    state = Column(String)
    industry = Column(String)
    founded_year = Column(String)
    latest_filing_date = Column(Date)
    revenue_range = Column(String)
    amount_sold = Column(String)
    jurisdiction = Column(String)
    executive_name = Column(String)
    executive_title = Column(String)
    website_url = Column(String)
    careers_url = Column(String)
    
    # New Intelligence Signals
    maturity_info = Column(String) # JSON
    funding_details = Column(String) # JSON
    founder_analysis = Column(String) # JSON
    public_presence_quality = Column(String) # JSON
    hiring_signal = Column(String) # JSON
    design_opportunity = Column(String) # JSON
    engagement_recommendation = Column(String)
    
    # AI Enrichment Status
    enrichment_status = Column(String, default="pending")  # pending, processing, completed, failed

