import os
import json
import time
import time
import logging
import threading
from flask import Flask, render_template, request, redirect, session, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, auth
from web3 import Web3
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from database_init import init_db

# Load environment variables from .env file
# Load environment variables from .env file
load_dotenv()

# FIX: Use absolute path so the file is ALWAYS found
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "election_config.json")
DB_PATH = os.path.join(BASE_DIR, "election.db")


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey_rvce_election_2025")

# ==========================================================
# 🛡️ RATE LIMITING
# ==========================================================
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================================
# ⚙️ BLOCKCHAIN CONFIGURATION (FAST MODE 🚀)
# ==========================================================

# 1. Connect to Sepolia (Using a fast public node + 60s timeout)
RPC_URL = os.getenv("RPC_URL", "https://ethereum-sepolia.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'timeout': 60}))

# 2. Your Admin Wallet (Loaded from .env file)
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY")

try:
    ADMIN_ADDRESS = w3.eth.account.from_key(ADMIN_PRIVATE_KEY).address
    logger.info(f"✅ Admin Wallet Loaded: {ADMIN_ADDRESS}")
except Exception as e:
    logger.warning("⚠️ WARNING: Private Key not set correctly yet.")
    logger.warning("⚠️ WARNING: Private Key not set correctly yet.")
    ADMIN_ADDRESS = None

# 🔒 MUTEX LOCK for Admin Nonce (Prevents race conditions)
NONCE_LOCK = threading.Lock()


# 3. Your Contract Details (Loaded from .env file)
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x585a1801372e73BabAf4144D306bAF80A7496ae9")
CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "uint256","name": "candidateId","type": "uint256"}],
        "name": "vote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256","name": "candidateId","type": "uint256"}],
        "name": "getVotes",
        "outputs": [{"internalType": "uint256","name": "","type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address","name": "","type": "address"}],
        "name": "hasVoted",
        "outputs": [{"internalType": "bool","name": "","type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# ==========================================================
# 🔥 FIREBASE ADMIN INITIALIZATION
# ==========================================================
firebase_cred_path = os.path.join(BASE_DIR, "firebase_credentials.json")
if os.path.exists(firebase_cred_path):
    try:
        cred = credentials.Certificate(firebase_cred_path)
        firebase_admin.initialize_app(cred)
        logger.info("✅ Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Firebase initialization failed: {e}")
else:
    logger.warning(f"⚠️ Firebase credentials not found at {firebase_cred_path}")

# ==========================================================
# 🔒 THE GATEKEEPER (SQLite Database System)
# ==========================================================
import sqlite3

def get_db_connection():
    """Returns a connection to the SQLite database."""
    # DB_PATH is now defined globally at the top
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_current_election_id():
    """Reads the current election ID from config."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get("currentElectionId", 1)
    except:
        return 1

def has_user_voted(student_id):
    """Checks the database to see if student has voted in the CURRENT election."""
    eid = get_current_election_id()
    try:
        conn = get_db_connection()
        vote = conn.execute(
            "SELECT id FROM votes WHERE student_id = ? AND election_id = ?",
            (student_id, eid)
        ).fetchone()
        conn.close()
        
        if vote:
            logger.info(f"🚫 BLOCKED: {student_id} already voted in Election #{eid}.")
            return True
        return False
    except Exception as e:
        logger.error(f"⚠️ Database Read Error: {e}")
        return False # Fail open or closed? Safer to allow retry if DB is down, but risk double vote.

def mark_user_as_voted(student_id):
    """Records the vote in SQLite with Atomic Transaction."""
    eid = get_current_election_id()
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO votes (student_id, election_id) VALUES (?, ?)",
            (student_id, eid)
        )
        conn.commit()
        conn.close()
        conn.commit()
        conn.close()
        logger.info(f"💾 SAVED: {student_id} voted in Election #{eid}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"❌ DOUBLE VOTE PREVENTED: {student_id} tried to vote twice.")
        return False
    except Exception as e:
        logger.error(f"❌ CRITICAL DATABASE ERROR: {e}")
        return False

def unmark_user_as_voted(student_id):
    """ROLLBACK: Removes the vote record if blockchain tx fails."""
    eid = get_current_election_id()
    try:
        conn = get_db_connection()
        conn.execute(
            "DELETE FROM votes WHERE student_id = ? AND election_id = ?",
            (student_id, eid)
        )
        conn.commit()
        conn.close()
        logger.info(f"↩️ ROLLBACK: Unmarked {student_id} (TX Failed)")
        return True
    except Exception as e:
        logger.error(f"❌ ROLLBACK FAILED for {student_id}: {e}")
        return False

# 🔧 AUTO-INIT DATABASE (Critical for Render/Cloud)
if not os.path.exists(DB_PATH):
    logger.info(f"⚙️ Database MISSING at {DB_PATH}. Running init_db(DB_PATH)...")
    success = init_db(DB_PATH)
    if success: logger.info("✅ Init DB Success")
    else: logger.error("❌ Init DB Failed")
else:
    logger.info(f"📂 Database FOUND at {DB_PATH}. Verifying tables...")
    init_db(DB_PATH)

# ==========================================================
# 📋 CANDIDATE MANAGEMENT (DB)
# ==========================================================
def get_all_candidates():
    """Fetches all candidates from the database."""
    try:
        conn = get_db_connection()
        candidates = conn.execute("SELECT * FROM candidates WHERE active = 1").fetchall()
        conn.close()
        return [dict(cand) for cand in candidates]
    except Exception as e:
        logger.error(f"⚠️ DB Read Error (Candidates): {e}")
        return []

def get_candidate_by_id(cid):
    """Fetches a single candidate by ID."""
    try:
        conn = get_db_connection()
        candidate = conn.execute("SELECT * FROM candidates WHERE id = ?", (cid,)).fetchone()
        conn.close()
        return dict(candidate) if candidate else None
    except Exception as e:
        logger.error(f"⚠️ DB Read Error (One Candidate): {e}")
        return None

def add_candidate(name, position, image, manifesto):
    """Adds a new candidate to the database."""
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO candidates (name, position, image, manifesto) VALUES (?, ?, ?, ?)",
            (name, position, image, manifesto)
        )
        conn.commit()
        conn.close()
        return True, "Success"
    except Exception as e:
        logger.error(f"❌ Error Adding Candidate: {e}")
        return False, str(e)

def delete_candidate(cid):
    """Soft deletes a candidate (sets active=0)."""
    try:
        conn = get_db_connection()
        conn.execute("UPDATE candidates SET active = 0 WHERE id = ?", (cid,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Error Deleting Candidate: {e}")
        return False

# ==========================================================
# ⏰ ELECTION CONTROL (Pause/Resume & Deadline)
# ==========================================================
from datetime import datetime

def get_election_settings(election_id):
    """Fetches settings for a specific election."""
    try:
        conn = get_db_connection()
        settings = conn.execute(
            "SELECT * FROM election_settings WHERE election_id = ?", 
            (election_id,)
        ).fetchone()
        conn.close()
        return dict(settings) if settings else None
    except Exception as e:
        logger.error(f"⚠️ Error fetching election settings: {e}")
        return None

def update_pause_status(election_id, is_paused):
    """Update pause status for an election."""
    try:
        conn = get_db_connection()
        conn.execute(
            "UPDATE election_settings SET is_paused = ? WHERE election_id = ?",
            (1 if is_paused else 0, election_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Error updating pause status: {e}")
        return False

def set_election_deadline(election_id, deadline_str):
    """Set deadline for an election. deadline_str should be in ISO format."""
    try:
        conn = get_db_connection()
        conn.execute(
            "UPDATE election_settings SET deadline = ? WHERE election_id = ?",
            (deadline_str, election_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Error setting deadline: {e}")
        return False

def is_voting_allowed():
    """Check if voting is currently allowed (not paused & before deadline)."""
    eid = get_current_election_id()
    settings = get_election_settings(eid)
    
    if not settings:
        # If no settings exist, create default and allow voting
        try:
            conn = get_db_connection()
            conn.execute("INSERT OR IGNORE INTO election_settings (election_id, is_paused) VALUES (?, 0)", (eid,))
            conn.commit()
            conn.close()
        except:
            pass
        return True, "Voting is open"
    
    # Check if paused
    if settings.get('is_paused'):
        return False, "⏸️ Voting is currently paused by admin"
    
    # Check deadline
    deadline = settings.get('deadline')
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline)
            if datetime.now() > deadline_dt:
                return False, f"⏰ Voting ended at {deadline_dt.strftime('%Y-%m-%d %H:%M')}"
        except:
            pass
    
    return True, "Voting is open"

# ==========================================================
# ROUTES
# ==========================================================

# 🛡️ SECURITY HEADERS
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# 💉 CONTEXT PROCESSOR: Inject Contract Address into ALL templates
@app.context_processor
def inject_contract_config():
    return {
        "CONTRACT_ADDRESS": CONTRACT_ADDRESS
    }

@app.route("/")
def home():
    return redirect("/dashboard") if "user_id" in session else redirect("/login")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if request.method == "GET":
        return render_template("login.html")
    try:
        data = request.get_json()
        id_token = data.get("idToken")
        if not id_token:
            return jsonify({"status": "error", "message": "Missing ID Token"}), 400
        decoded = auth.verify_id_token(id_token, check_revoked=True, clock_skew_seconds=60)
        session["user_id"] = decoded["uid"]
        session["email"] = decoded["email"]
        session["student_id"] = decoded["email"].split("@")[0]
        return jsonify({"status": "success", "redirect": "/dashboard"})
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return jsonify({"status": "error", "message": "Login failed"}), 500

# ---------------- REGISTER ----------------
@app.route("/register", endpoint="register")
def register_page():
    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect("/login")
    return render_template("dashboard.html", 
                         student_id=session["student_id"], 
                         email=session["email"],
                         current_election_id=get_current_election_id())

# ---------------- ARCHITECTURE ----------------
@app.route("/architecture")
def architecture():
    if "user_id" not in session: return redirect("/login")
    return render_template("architecture.html")

# ---------------- VOTE PAGE ----------------
@app.route("/vote")
def vote():
    if "user_id" not in session: return redirect("/login")
    candidates = get_all_candidates()
    return render_template("vote.html", candidates=candidates)

# ---------------- RESULTS ----------------
@app.route("/results")
def results():
    if "user_id" not in session: return redirect("/login")
    candidates = get_all_candidates()
    resp = make_response(render_template("results.html", candidates=candidates))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

# ---------------- MANIFESTO ----------------
@app.route("/manifesto/<int:candidate_id>")
def manifesto(candidate_id):
    if "user_id" not in session: return redirect("/login")
    
    # Validate candidate ID via DB
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        return redirect("/vote")
    
    return render_template(f"manifesto.html", candidate=candidate)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- ADMIN ----------------
@app.route("/admin", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin():
    # 1. GET: Show Admin Login Page
    if request.method == "GET":
        if session.get("is_admin"):
            return redirect("/admin/dashboard")
        return render_template("admin_login.html")

    # 2. POST: Handle Firebase Token Authentication
    try:
        data = request.get_json()
        id_token = data.get("idToken")
        if not id_token:
            return jsonify({"status": "error", "message": "Missing ID Token"}), 400
        
        # Verify Token
        decoded = auth.verify_id_token(id_token, check_revoked=True, clock_skew_seconds=60)
        email = decoded.get("email")
        
        # 🔒 STRICT ACCESS CONTROL (Loaded from .env file)
        ALLOWED_ADMIN_EMAIL = os.getenv("ALLOWED_ADMIN_EMAIL", "madhurrishis.is24@rvce.edu.in")
        
        if email != ALLOWED_ADMIN_EMAIL:
            logger.warning(f"⚠️ UNAUTHORIZED ADMIN ATTEMPT: {email}")
            return jsonify({"status": "error", "message": "Access Denied: Not an Admin"}), 403
            
        # ✅ Grant Admin Access
        session["is_admin"] = True
        session["admin_email"] = email
        logger.info(f"✅ ADMIN LOGGED IN: {email}")
        
        return jsonify({"status": "success", "redirect": "/admin/dashboard"})

    except Exception as e:
        logger.error(f"❌ Admin Login Error: {e}")
        return jsonify({"status": "error", "message": "Authentication Failed"}), 500

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("is_admin"): return redirect("/admin")
    
    # Read Total Voters
    total_votes = 0
    eid = get_current_election_id()
    candidates = get_all_candidates()

    try:
        conn = get_db_connection()
        row = conn.execute("SELECT COUNT(*) FROM votes WHERE election_id = ?", (eid,)).fetchone()
        total_votes = row[0]
        conn.close()
    except Exception as e:
        logger.error(f"⚠️ DB Error in Admin Dashboard: {e}")
    
    return render_template("admin_dashboard.html", 
                         total_votes=total_votes,
                         admin_email=session.get("admin_email"),
                         current_election_id=eid,
                         candidates=candidates)

# ---------------- ADMIN CANDIDATE MANAGEMENT ----------------
@app.route("/admin/candidates/add", methods=["POST"])
def admin_add_candidate():
    if not session.get("is_admin"): return jsonify({"status": "error"}), 403
    
    try:
        name = request.form.get("name")
        position = request.form.get("position")
        manifesto_text = request.form.get("manifesto")  # Text input
        image_file = request.files.get("image")
        manifesto_file = request.files.get("manifesto_file") # File input

        # Handle Image
        image_filename = "default.jpg"
        if image_file:
            # FIX: Ensure images directory exists
            images_dir = os.path.join(BASE_DIR, "static/images")
            os.makedirs(images_dir, exist_ok=True)
            
            image_filename = f"{int(time.time())}_{image_file.filename}"
            image_path = os.path.join(images_dir, image_filename)
            image_file.save(image_path)

        # Handle Manifesto (File vs Text)
        manifesto_value = manifesto_text # Default to text
        
        if manifesto_file and manifesto_file.filename:
            # Ensure static/docs exists
            docs_dir = os.path.join(BASE_DIR, "static/docs")
            os.makedirs(docs_dir, exist_ok=True)
            
            # Save file
            manifesto_filename = f"{int(time.time())}_{manifesto_file.filename}"
            manifesto_path = os.path.join(docs_dir, manifesto_filename)
            manifesto_file.save(manifesto_path)
            manifesto_value = manifesto_filename
            
        success, msg = add_candidate(name, position, image_filename, manifesto_value)
        if success:
            return jsonify({"status": "success", "message": "Candidate Added!"})
        else:
            return jsonify({"status": "error", "message": f"DB Error: {msg}"})
    except Exception as e:
        logger.error(f"Error adding candidate: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/admin/candidates/delete", methods=["POST"])
def admin_delete_candidate():
    if not session.get("is_admin"): return jsonify({"status": "error"}), 403
    cid = request.form.get("id")
    if delete_candidate(cid):
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

# ---------------- ADMIN ELECTION CONTROL ----------------
@app.route("/admin/election/pause", methods=["POST"])
def admin_pause_election():
    if not session.get("is_admin"): return jsonify({"status": "error"}), 403
    eid = get_current_election_id()
    if update_pause_status(eid, True):
        logger.info(f"⏸️ Election #{eid} PAUSED by {session.get('admin_email')}")
        return jsonify({"status": "success", "message": "Election paused"})
    return jsonify({"status": "error", "message": "Failed to pause"})

@app.route("/admin/election/resume", methods=["POST"])
def admin_resume_election():
    if not session.get("is_admin"): return jsonify({"status": "error"}), 403
    eid = get_current_election_id()
    if update_pause_status(eid, False):
        logger.info(f"▶️ Election #{eid} RESUMED by {session.get('admin_email')}")
        return jsonify({"status": "success", "message": "Election resumed"})
    return jsonify({"status": "error", "message": "Failed to resume"})

@app.route("/admin/election/set-deadline", methods=["POST"])
def admin_set_deadline():
    if not session.get("is_admin"): return jsonify({"status": "error"}), 403
    
    data = request.get_json()
    deadline = data.get("deadline")  # expects ISO format string
    
    if not deadline:
        return jsonify({"status": "error", "message": "Missing deadline"}), 400
    
    eid = get_current_election_id()
    if set_election_deadline(eid, deadline):
        logger.info(f"⏰ Deadline set for Election #{eid}: {deadline}")
        return jsonify({"status": "success", "message": "Deadline set"})
    return jsonify({"status": "error", "message": "Failed to set deadline"})

@app.route("/admin/election/get-status", methods=["GET"])
def admin_get_election_status():
    if not session.get("is_admin"): return jsonify({"status": "error"}), 403
    eid = get_current_election_id()
    settings = get_election_settings(eid)
    allowed, message = is_voting_allowed()
    
    return jsonify({
        "status": "success",
        "is_paused": settings.get('is_paused', 0) if settings else 0,
        "deadline": settings.get('deadline') if settings else None,
        "voting_allowed": allowed,
        "message": message
    })

# FIX: Absolute path for offsets
OFFSETS_FILE = os.path.join(BASE_DIR, "election_offsets.json")

def get_current_offsets(eid):
    """Returns the offsets for a specific election ID."""
    if not os.path.exists(OFFSETS_FILE): return [0]*6
    try:
        with open(OFFSETS_FILE, 'r') as f:
             data = json.load(f)
             return data.get(str(eid), [0]*6)
    except: return [0]*6

@app.route("/api/offsets")
def api_offsets():
    """Returns offsets for the CURRENT election."""
    eid = get_current_election_id()
    offsets = get_current_offsets(eid)
    return jsonify({"election_id": eid, "offsets": offsets})

@app.route("/admin/start-new-election", methods=["POST"])
def start_new_election():
    if not session.get("is_admin"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
    try:
        # 0. FETCH CURRENT BLOCKCHAIN TOTALS (The Snapshot)
        # 0. FETCH CURRENT BLOCKCHAIN TOTALS (The Snapshot)
        current_votes = []
        try:
             # FIX: Fetch ALL active candidates, not just 1-6
             all_cands = get_all_candidates()
             # We need to snapshot votes for EVERY candidate in the DB
             # Assuming candidate IDs correspond to contract IDs
             
             for cand in all_cands:
                 cid = cand['id']
                 try:
                    count = contract.functions.getVotes(cid).call()
                    current_votes.append(count)
                 except Exception as sub_e:
                    logger.warning(f"⚠️ Could not fetch votes for ID {cid}: {sub_e}")
                    current_votes.append(0) # Default to 0 if error for this specific ID
                 
             logger.info(f"📸 SNAPSHOT CAPTURED: {current_votes}")
        except Exception as e:
             return jsonify({"status": "error", "message": f"Blockchain Read Failed: {str(e)}"}), 500

        # 1. Read Current ID
        current_id = 1
        if os.path.exists(CONFIG_FILE):
             with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                current_id = data.get("currentElectionId", 1)
        
        # 2. Increment ID
        new_id = current_id + 1
        
        # 3. Save Offset for the NEW ID
        # The offset for Cycle N is the Total Votes at end of Cycle N-1
        all_offsets = {}
        if os.path.exists(OFFSETS_FILE):
             try:
                 with open(OFFSETS_FILE, 'r') as f: all_offsets = json.load(f)
             except: pass
        
        all_offsets[str(new_id)] = current_votes
        
        with open(OFFSETS_FILE, 'w') as f:
            json.dump(all_offsets, f, indent=4)

        # 4. Save Config (Atomic-ish)
        new_config = {"currentElectionId": new_id}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(new_config, f, indent=4)
            
        new_config = {"currentElectionId": new_id}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(new_config, f, indent=4)
            
        logger.info(f"🔄 ELECTION CYCLE UPDATED: {current_id} -> {new_id} with Offsets {current_votes}")
        return jsonify({"status": "success", "new_election_id": new_id})
        
    except Exception as e:
        logger.error(f"❌ Error starting new election: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_email", None)
    return redirect("/admin")

# ---------------- ERROR HANDLERS ----------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ==========================================================
# 🚀 NEW SERVER-SIDE VOTING LOGIC (SECURE + ROBUST)
# ==========================================================
@app.route("/submit_vote", methods=["POST"])
@limiter.limit("5 per minute")
def submit_vote():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # 🛑 CHECK: Is voting currently allowed?
    allowed, reason = is_voting_allowed()
    if not allowed:
        logger.warning(f"Vote blocked for {session.get('student_id')}: {reason}")
        return jsonify({"status": "error", "message": reason}), 403

    # 🛑 SECURITY: Input Validation
    data = request.get_json()
    if not data or "candidateId" not in data:
         return jsonify({"status": "error", "message": "Invalid Data"}), 400
         
    try:
        candidate_id = int(data.get("candidateId"))
        # Check if candidate exists in DB and is active
        cand = get_candidate_by_id(candidate_id)
        if not cand:
             raise ValueError("Candidate not found")
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid Candidate Selection"}), 400

    # 🛑 SECURITY CHECK: Did this student already vote?
    student_id = session["student_id"]
    
    # Check the file strictly before doing anything else
    if has_user_voted(student_id):
        logger.warning(f"🚫 BLOCKED REQUEST: {student_id} tried to vote again.")
        return jsonify({"status": "error", "message": "You have already voted!"}), 400

    if not ADMIN_PRIVATE_KEY or "PASTE" in ADMIN_PRIVATE_KEY:
         return jsonify({"status": "error", "message": "Server Config Error: Admin Key missing"}), 500

    # data = request.get_json()  <-- REMOVED (Duplicate)
    # candidate_id = int(data.get("candidateId")) <-- REMOVED (Moved up)
    
    try:
        logger.info(f"🗳️  Processing vote for Candidate {candidate_id} by {student_id}...")

        # 🔒 OPTIMISTIC LOCKING: Mark as voted FIRST to prevent race conditions
        if not mark_user_as_voted(student_id):
            return jsonify({"status": "error", "message": "You have already voted!"}), 400

        # 1. Create a FRESH temporary wallet
        temp_account = w3.eth.account.create()
        logger.info(f"👤 Created Temp Voter: {temp_account.address}")
        
        try: 
            # 🔒 CRITICAL SECTION: Only one thread can use Admin Nonce at a time
            with NONCE_LOCK:
                # 2. Fund the Temp Wallet
                nonce = w3.eth.get_transaction_count(ADMIN_ADDRESS)
                
                # 🔥 BOOST: Pay 50% more gas to be faster
                current_gas_price = w3.eth.gas_price
                boosted_gas_price = int(current_gas_price * 1.5) 

                # Calculate amount manually: 0.005 ETH = 0.005 * 10^18 Wei
                amount_in_wei = int(0.005 * 10**18)

                fund_tx = {
                    'to': temp_account.address,
                    'value': amount_in_wei, 
                    'gas': 21000,
                    'gasPrice': boosted_gas_price,
                    'nonce': nonce,
                    'chainId': 11155111
                }
                signed_fund_tx = w3.eth.account.sign_transaction(fund_tx, ADMIN_PRIVATE_KEY)
                
                # FIX: Try camelCase, if fail try snake_case (Universal fix)
                try:
                    tx_hash_fund = w3.eth.send_raw_transaction(signed_fund_tx.rawTransaction)
                except AttributeError:
                    tx_hash_fund = w3.eth.send_raw_transaction(signed_fund_tx.raw_transaction)

            logger.info(f"💸 Funding Temp Wallet... (Tx: {tx_hash_fund.hex()})")
            
            # Wait for funding (TIMEOUT 300s)
            w3.eth.wait_for_transaction_receipt(tx_hash_fund, timeout=300)

            # 3. Cast the Vote
            contract_function = contract.functions.vote(candidate_id)
            
            tx_params = {
                'from': temp_account.address,
                'nonce': 0, 
                'gas': 300000,
                'gasPrice': boosted_gas_price,
                'chainId': 11155111
            }

            # 🛠️ UNIVERSAL BUILD TRANSACTION FIX
            try:
                built_vote_tx = contract_function.build_transaction(tx_params)
            except AttributeError:
                built_vote_tx = contract_function.buildTransaction(tx_params)
            
            signed_vote_tx = w3.eth.account.sign_transaction(built_vote_tx, temp_account.key)
            
            try:
                tx_hash_vote = w3.eth.send_raw_transaction(signed_vote_tx.rawTransaction)
            except AttributeError:
                tx_hash_vote = w3.eth.send_raw_transaction(signed_vote_tx.raw_transaction)
            
            logger.info(f"✅ Vote Cast on Blockchain! Hash: {tx_hash_vote.hex()}")

            # Wait for vote receipt (TIMEOUT 300s)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash_vote, timeout=300)

            if receipt.status == 1:
                # ✅ SUCCESS! (User is already marked voted, so we just return)
                logger.info(f"📝 Vote Confirmed for {student_id}")
                
                # Ensure hash has 0x prefix for Etherscan compatibility
                tx_hash_str = tx_hash_vote.hex() if isinstance(tx_hash_vote.hex(), str) else str(tx_hash_vote.hex())
                if not tx_hash_str.startswith('0x'):
                    tx_hash_str = '0x' + tx_hash_str
                return jsonify({"status": "success", "tx_hash": tx_hash_str})
            else:
                # ❌ REVERTED ON CHAIN -> ROLLBACK
                logger.error("Transaction reverted on chain")
                unmark_user_as_voted(student_id)
                return jsonify({"status": "error", "message": "Transaction reverted on chain"}), 500

        except Exception as inner_e:
            # ❌ BLOCKCHAIN ERROR -> ROLLBACK
            logger.error(f"Blockchain failure: {inner_e}")
            unmark_user_as_voted(student_id) # Unlock user so they can try again
            raise inner_e

    except Exception as e:
        logger.error(f"❌ Blockchain Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Initialize DB on start
    from database_init import init_db
    init_db()
    app.run()