import os
import json
import time
from flask import Flask, render_template, request, redirect, session, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, auth
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey_rvce_election_2025")

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
    print(f"✅ Admin Wallet Loaded: {ADMIN_ADDRESS}")
except Exception as e:
    print("⚠️ WARNING: Private Key not set correctly yet.")
    ADMIN_ADDRESS = None


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
# 🔒 THE GATEKEEPER (Robust Blacklist System)
# ==========================================================
# ==========================================================
# 🔒 THE GATEKEEPER (Robust Blacklist System)
# ==========================================================
# FIX: Use absolute path so the file is ALWAYS found
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "election_config.json")

def get_current_election_id():
    """Reads the current election ID from config."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get("currentElectionId", 1)
    except:
        return 1

def get_votes_file_path():
    """Returns the correct blacklist file for the current election."""
    eid = get_current_election_id()
    # PRESERVE BACKWARD COMPATIBILITY: ID 1 uses the original file
    if eid == 1:
        return os.path.join(BASE_DIR, "voted_users.json")
    else:
        return os.path.join(BASE_DIR, f"voted_users_{eid}.json")

def has_user_voted(user_id):
    """Checks the JSON file to see if student has voted."""
    votes_file = get_votes_file_path()
    print(f"🔍 Checking blacklist in {os.path.basename(votes_file)} for: {user_id}") 
    
    if not os.path.exists(votes_file):
        print("📂 No blacklist file found yet (First vote?).")
        return False
        
    try:
        with open(votes_file, 'r') as f:
            content = f.read()
            if not content: return False # Handle empty file
            voters = json.loads(content)
            
            if user_id in voters:
                print(f"🚫 BLOCKED: Found {user_id} in blacklist!")
                return True
            else:
                print(f"✅ {user_id} is clear to vote.")
                return False
    except Exception as e:
        print(f"⚠️ Error reading blacklist: {e}")
        return False

def mark_user_as_voted(user_id):
    """Adds student ID to the JSON file safely."""
    votes_file = get_votes_file_path()
    voters = []
    
    # Read existing
    if os.path.exists(votes_file):
        try:
            with open(votes_file, 'r') as f:
                content = f.read()
                if content:
                    voters = json.loads(content)
        except Exception as e:
            print(f"⚠️ Error reading for update: {e}")
            voters = []
    
    # Update and Save
    if user_id not in voters:
        voters.append(user_id)
        try:
            with open(votes_file, 'w') as f:
                json.dump(voters, f, indent=4) # Indent makes it readable
            print(f"💾 SAVED: {user_id} added to {votes_file}")
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Could not save blacklist! {e}")

# ==========================================================
# FIREBASE INITIALIZATION
# ==========================================================
KEY_PATH = os.path.join(BASE_DIR, os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json"))

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized")
    except Exception as e:
        print("❌ Firebase init error:", e)

# ==========================================================
# CANDIDATES
# ==========================================================
CANDIDATES = [
    {"id": 1, "name": "Candidate One", "position": "Class Rep", "image": "cand1.jpg"},
    {"id": 2, "name": "Candidate Two", "position": "Class Rep", "image": "cand2.jpg"},
    {"id": 3, "name": "Candidate Three", "position": "Class Rep", "image": "cand3.jpg"},
    {"id": 4, "name": "Candidate Four", "position": "Class Rep", "image": "cand4.jpg"},
    {"id": 5, "name": "Candidate Five", "position": "Class Rep", "image": "cand5.jpg"},
    {"id": 6, "name": "Candidate Six", "position": "Class Rep", "image": "cand6.jpg"}
]

# ==========================================================
# ROUTES
# ==========================================================

# 🛡️ SECURITY HEADERS
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Strict-Transport-Security (Enable if using HTTPS in prod)
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.route("/")
def home():
    return redirect("/dashboard") if "user_id" in session else redirect("/login")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
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
        print("❌ Login error:", e)
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
    return render_template("vote.html", candidates=CANDIDATES)

# ---------------- RESULTS ----------------
@app.route("/results")
def results():
    if "user_id" not in session: return redirect("/login")
    resp = make_response(render_template("results.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

# ---------------- MANIFESTO ----------------
@app.route("/manifesto/<int:candidate_id>")
def manifesto(candidate_id):
    if "user_id" not in session: return redirect("/login")
    # Validate candidate ID
    if candidate_id < 1 or candidate_id > 6:
        return redirect("/vote")
    return render_template(f"manifesto_candidate{candidate_id}.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- ADMIN ----------------
@app.route("/admin", methods=["GET", "POST"])
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
            print(f"⚠️ UNAUTHORIZED ADMIN ATTEMPT: {email}")
            return jsonify({"status": "error", "message": "Access Denied: Not an Admin"}), 403
            
        # ✅ Grant Admin Access
        session["is_admin"] = True
        session["admin_email"] = email
        print(f"✅ ADMIN LOGGED IN: {email}")
        
        return jsonify({"status": "success", "redirect": "/admin/dashboard"})

    except Exception as e:
        print(f"❌ Admin Login Error: {e}")
        return jsonify({"status": "error", "message": "Authentication Failed"}), 500

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("is_admin"): return redirect("/admin")
    
    # Read Voted Users for Current Election
    voters = []
    votes_file = get_votes_file_path() # Dynamic
    if os.path.exists(votes_file):
        try:
            with open(votes_file, 'r') as f:
                content = f.read()
                if content: voters = json.loads(content)
        except: pass
    
    return render_template("admin_dashboard.html", 
                         voters=voters, 
                         total_votes=len(voters),
                         admin_email=session.get("admin_email"),
                         current_election_id=get_current_election_id())

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
        current_votes = []
        try:
             for i in range(1, 7):
                 count = contract.functions.getVotes(i).call()
                 current_votes.append(count)
             print(f"📸 SNAPSHOT CAPTURED: {current_votes}")
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
            
        print(f"🔄 ELECTION CYCLE UPDATED: {current_id} -> {new_id} with Offsets {current_votes}")
        return jsonify({"status": "success", "new_election_id": new_id})
        
    except Exception as e:
        print(f"❌ Error starting new election: {e}")
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
def submit_vote():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # 🛑 SECURITY: Input Validation
    data = request.get_json()
    if not data or "candidateId" not in data:
         return jsonify({"status": "error", "message": "Invalid Data"}), 400
         
    try:
        candidate_id = int(data.get("candidateId"))
        if candidate_id < 1 or candidate_id > 6:
            raise ValueError("Invalid Candidate ID")
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid Candidate Selection"}), 400

    # 🛑 SECURITY CHECK: Did this student already vote?
    student_id = session["student_id"]
    
    # Check the file strictly before doing anything else
    if has_user_voted(student_id):
        print(f"🚫 BLOCKED REQUEST: {student_id} tried to vote again.")
        return jsonify({"status": "error", "message": "You have already voted!"}), 400

    if not ADMIN_PRIVATE_KEY or "PASTE" in ADMIN_PRIVATE_KEY:
         return jsonify({"status": "error", "message": "Server Config Error: Admin Key missing"}), 500

    # data = request.get_json()  <-- REMOVED (Duplicate)
    # candidate_id = int(data.get("candidateId")) <-- REMOVED (Moved up)
    
    try:
        print(f"🗳️  Processing vote for Candidate {candidate_id} by {student_id}...")

        # 1. Create a FRESH temporary wallet
        temp_account = w3.eth.account.create()
        print(f"👤 Created Temp Voter: {temp_account.address}")

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

        print(f"💸 Funding Temp Wallet... (Tx: {tx_hash_fund.hex()})")
        
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
        
        # FIX: Try camelCase, if fail try snake_case
        try:
            tx_hash_vote = w3.eth.send_raw_transaction(signed_vote_tx.rawTransaction)
        except AttributeError:
            tx_hash_vote = w3.eth.send_raw_transaction(signed_vote_tx.raw_transaction)
        
        print(f"✅ Vote Cast on Blockchain! Hash: {tx_hash_vote.hex()}")

        # Wait for vote receipt (TIMEOUT 300s)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash_vote, timeout=300)

        if receipt.status == 1:
            # ✅ SUCCESS! MARK USER AS VOTED IMMEDIATELY
            mark_user_as_voted(student_id)
            print(f"📝 {student_id} added to blacklist.")
            return jsonify({"status": "success", "tx_hash": tx_hash_vote.hex()})
        else:
            return jsonify({"status": "error", "message": "Transaction reverted on chain"}), 500

    except Exception as e:
        print("❌ Blockchain Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()