
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Company

DATABASE_URL = "sqlite:///companies.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

companies = db.query(Company).all()
print(f"Found {len(companies)} companies.")
for c in companies[:5]:
    print(f"Name: {c.name}, Industry: {c.industry}, Rev: {c.revenue_range}, City: {c.city}")
