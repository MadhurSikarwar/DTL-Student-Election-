import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "election.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create Users Table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    eth_address TEXT NOT NULL
);
""")

# Create Local Votes Table (safe fallback)
cur.execute("""
CREATE TABLE IF NOT EXISTS local_votes (
    candidate_id INTEGER PRIMARY KEY,
    count INTEGER DEFAULT 0
);
""")

# Insert default vote records if missing
cur.execute("INSERT OR IGNORE INTO local_votes (candidate_id, count) VALUES (1, 0)")
cur.execute("INSERT OR IGNORE INTO local_votes (candidate_id, count) VALUES (2, 0)")
cur.execute("INSERT OR IGNORE INTO local_votes (candidate_id, count) VALUES (3, 0)")

conn.commit()
conn.close()

print("Database initialized successfully at:", DB_PATH)
