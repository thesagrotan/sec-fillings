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

if "careers_url" not in columns:
    print("Adding careers_url column...")
    cursor.execute("ALTER TABLE companies ADD COLUMN careers_url VARCHAR")
    conn.commit()
    print("Column added.")
else:
    print("Column careers_url already exists.")

conn.close()
