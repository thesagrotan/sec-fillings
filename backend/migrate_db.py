import sqlite3
import os

db_path = "companies.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(companies)")
columns = [info[1] for info in cursor.fetchall()]


columns_to_add = {
    "careers_url": "VARCHAR",
    "maturity_info": "VARCHAR",
    "funding_details": "VARCHAR",
    "founder_analysis": "VARCHAR",
    "public_presence_quality": "VARCHAR",
    "hiring_signal": "VARCHAR",
    "design_opportunity": "VARCHAR",
    "engagement_recommendation": "VARCHAR"
}

for col_name, col_type in columns_to_add.items():
    if col_name not in columns:
        print(f"Adding {col_name} column...")
        try:
            cursor.execute(f"ALTER TABLE companies ADD COLUMN {col_name} {col_type}")
            conn.commit()
            print(f"Column {col_name} added.")
        except Exception as e:
            print(f"Error adding {col_name}: {e}")
    else:
        print(f"Column {col_name} already exists.")

conn.close()
