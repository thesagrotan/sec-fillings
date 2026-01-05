"""
Database migration script to add enrichment_status column to existing companies.
"""
from sqlalchemy import text
from .models import engine

def migrate():
    """Add enrichment_status column if it doesn't exist."""
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("PRAGMA table_info(companies)"))
        columns = [row[1] for row in result.fetchall()]
        
        if "enrichment_status" not in columns:
            conn.execute(text("ALTER TABLE companies ADD COLUMN enrichment_status VARCHAR DEFAULT 'pending'"))
            conn.commit()
            print("Added enrichment_status column")
        else:
            print("enrichment_status column already exists")

if __name__ == "__main__":
    migrate()
