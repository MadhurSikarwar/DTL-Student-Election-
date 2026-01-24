import sqlite3
import os

# Use absolute path for reliability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "election.db")

def init_db(db_path=None):
    if db_path is None:
        db_path = DB_PATH
        
    try:
        conn = sqlite3.connect(db_path)
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

        # 2. Create Candidates Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            image TEXT NOT NULL,
            manifesto TEXT,
            active BOOLEAN DEFAULT 1
        );
        """)

        # 3. Seed Default Candidates (if empty)
        cur.execute("SELECT COUNT(*) FROM candidates")
        if cur.fetchone()[0] == 0:
            print("🌱 Seeding default candidates...")
            defaults = [
                (1, "Candidate One", "Class Rep", "cand1.jpg", "Make the campus greener!"),
                (2, "Candidate Two", "Class Rep", "cand2.jpg", "Better canteen food for all."),
                (3, "Candidate Three", "Class Rep", "cand3.jpg", "More sports equipment."),
                (4, "Candidate Four", "Class Rep", "cand4.jpg", "Study rooms open 24/7."),
                (5, "Candidate Five", "Class Rep", "cand5.jpg", "Upgrade tech labs."),
                (6, "Candidate Six", "Class Rep", "cand6.jpg", "Free Wi-Fi everywhere.")
            ]
            cur.executemany("INSERT INTO candidates (id, name, position, image, manifesto) VALUES (?, ?, ?, ?, ?)", defaults)

        # 4. Create Election Settings Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS election_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            election_id INTEGER NOT NULL UNIQUE,
            is_paused BOOLEAN DEFAULT 0,
            deadline DATETIME NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Insert default settings for election 1 if missing
        cur.execute("INSERT OR IGNORE INTO election_settings (election_id, is_paused) VALUES (1, 0)")


        
        # 2. Check and clean up legacy info if needed
        # (Optional: Add migration logic here if we were preserving old JSON data)
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized successfully at: {db_path}")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_db()
