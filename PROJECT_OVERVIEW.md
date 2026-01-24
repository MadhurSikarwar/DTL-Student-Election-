# Project Overview – DTL Student Election

## Table of Contents
- [Project Summary](#project-summary)
- [Technology Stack](#technology-stack)
- [Architecture Overview](#architecture-overview)
- [Key Features](#key-features)
- [Blockchain Integration](#blockchain-integration)
- [Environment & Configuration](#environment--configuration)
- [Directory Structure](#directory-structure)
- [API Endpoints & Template Mapping](#api-endpoints--template-mapping)
- [Deployment Workflow](#deployment-workflow)
- [Testing & Verification](#testing--verification)
- [Contribution Guidelines](#contribution-guidelines)

---

## Project Summary
The **DTL Student Election** application is a Flask‑based web platform that enables students to securely vote for class representatives. It leverages **Firebase Authentication** for user identity and **Ethereum Sepolia testnet** (via Web3) to record votes on‑chain, ensuring immutability and transparency. Admins can create new election cycles, view results, and manage the voting process.

---

## Technology Stack
| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, Flask, python‑dotenv |
| Authentication | Firebase Admin SDK |
| Blockchain | Web3.py, Sepolia testnet (public node) |
| Data Storage | JSON files (`election_config.json`, `election_offsets.json`, per‑election vote blacklists) |
| Database (optional) | SQLite (`database.db`) |
| Deployment | Docker, Gunicorn, Heroku, Render |
| CI/CD | GitHub Actions (docker‑publish.yml) |
| Frontend | HTML5, Jinja2 templates, vanilla CSS (custom design) |

---

## Architecture Overview
```mermaid
flowchart TD
    subgraph Frontend
        UI[HTML Templates & CSS]
    end
    subgraph Backend
        FlaskApp[Flask (app.py)]
        Firebase[Firebase Admin SDK]
        Web3[Web3 (Sepolia)]
        JSONStore[JSON Files]
    end
    UI -->|HTTP Requests| FlaskApp
    FlaskApp -->|Auth Verify| Firebase
    FlaskApp -->|Vote Tx| Web3
    Web3 -->|Read/Write| JSONStore
    FlaskApp -->|Read/Write| JSONStore
    FlaskApp -->|Render| UI
```

---

## Key Features
- **User Authentication** – Firebase ID token verification for login/registration.
- **Secure Voting** – One‑time vote per student enforced via per‑election blacklist JSON files.
- **Admin Dashboard** – View live vote counts, start new election cycles, and manage admin session.
- **Manifesto Pages** – Individual candidate manifesto HTML pages.
- **Result Page** – Real‑time results view (no‑cache headers).
- **Blockchain Auditing** – Votes are recorded on Sepolia via a smart contract (`vote(uint256)` & `getVotes(uint256)`).
- **Multi‑Election Support** – `election_config.json` tracks current election ID; offsets stored in `election_offsets.json`.

---

## Blockchain Integration
- **Contract Address** – `0x585a1801372e73BabAf4144D306bAF80A7496ae9` (default, configurable via `.env`).
- **Functions**:
  - `vote(uint256 candidateId)` – called from `/submit_vote` after funding a temporary wallet.
  - `getVotes(uint256 candidateId)` – used by admin dashboard to display totals.
- **Workflow**:
  1. Admin private key loaded from `ADMIN_PRIVATE_KEY`.
  2. Temporary wallet created per vote, funded with 0.005 ETH.
  3. Transaction signed and sent; receipt awaited.
  4. On success, student ID added to blacklist JSON.

---

## Environment & Configuration
Create a `.env` file (add to `.gitignore`):
```
FLASK_SECRET_KEY=super_secret_key
RPC_URL=https://ethereum-sepolia.publicnode.com
ADMIN_PRIVATE_KEY=your_admin_private_key
CONTRACT_ADDRESS=0x...
FIREBASE_CREDENTIALS_PATH=firebase_credentials.json
ALLOWED_ADMIN_EMAIL=madhurrishis.is24@rvce.edu.in
```
- `python-dotenv` loads these at runtime.
- `firebase_credentials.json` must be present (or set as a secret in deployment).

---

## Directory Structure
```
DTL FINAL PROTOTYPE/
├─ app.py                 # Flask entry point
├─ requirements.txt       # Python deps
├─ .env (ignored)        # Env vars
├─ firebase_credentials.json
├─ election_config.json   # {"currentElectionId": N}
├─ election_offsets.json  # {"N": [votes per candidate]}
├─ voted_users.json       # Blacklist for election 1
├─ voted_users_2.json ... # Blacklist per election
├─ static/                # CSS, images, JS
├─ templates/            # HTML/Jinja2 files
│   ├─ dashboard.html
│   ├─ login.html
│   ├─ vote.html
│   ├─ results.html
│   ├─ manifesto_candidateX.html
│   └─ ...
└─ README.md (original)
```

---

## API Endpoints & Template Mapping
| Route | Method | Purpose | Template |
|-------|--------|---------|----------|
| `/` | GET | Redirect to dashboard or login | – |
| `/login` | GET/POST | Firebase login flow | `login.html` |
| `/register` | GET | Registration page | `register.html` |
| `/dashboard` | GET | User home with election ID | `dashboard.html` |
| `/vote` | GET | Show candidate cards | `vote.html` |
| `/submit_vote` | POST | Process vote, blockchain tx | – |
| `/results` | GET | Show results (no‑cache) | `results.html` |
| `/manifesto/<int:id>` | GET | Candidate manifesto page | `manifesto_candidate{id}.html` |
| `/admin` | GET/POST | Admin login (Firebase) | `admin_login.html` |
| `/admin/dashboard` | GET | Admin view of votes & start new election | `admin_dashboard.html` |
| `/admin/start-new-election` | POST | Snapshot current votes, increment ID | – |
| `/api/offsets` | GET | Return offsets JSON for current election | – |

---

## Deployment Workflow
1. **Local Development**
   ```bash
   pip install -r requirements.txt
   flask run
   ```
2. **Docker** (recommended)
   ```bash
   docker build -t dtl-election .
   docker run -p 5000:5000 --env-file .env dtl-election
   ```
3. **Heroku / Render** – set environment variables via dashboard, push repo, and enable the provided `Procfile`.
4. **CI/CD** – GitHub Actions builds and pushes the Docker image to GHCR on each push to `main`.

---

## Testing & Verification
- **Manual**: Navigate through login → vote → results; ensure a student cannot vote twice.
- **Blockchain**: Verify transaction hash appears on Sepolia explorer and `getVotes` reflects the new count.
- **Admin**: Start a new election and confirm `election_config.json` and `election_offsets.json` update.
- **Automated** (optional): Add Flask test client scripts to hit each route and assert expected status codes.

---

## Contribution Guidelines
1. Fork the repository and create a feature branch.
2. Follow the existing code style (PEP8, type hints optional).
3. Add/modify tests for new functionality.
4. Update `PROJECT_OVERVIEW.md` if you add major features.
5. Submit a pull request with a clear description.

---

*Generated on 2026‑01‑24.*
