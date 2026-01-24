import sqlite3
import os

# Use absolute path for reliability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "election.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # 1. Create Vote Tracking Table
        # election_id + student_id must be UNIQUE together
        cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            election_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, election_id)
        );
        """)
        
        # 2. Check and clean up legacy info if needed
        # (Optional: Add migration logic here if we were preserving old JSON data)
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized successfully at: {DB_PATH}")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_db()
