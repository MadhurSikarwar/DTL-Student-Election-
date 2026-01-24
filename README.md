# RVCE E-Vote 🗳️

**Secure, Transparent, and Immutable Student Election Platform**

RVCE E-Vote is a modern, blockchain-based voting application designed to conduct student elections with absolute integrity. By leveraging the Ethereum blockchain (Sepolia Testnet) for vote recording and a robust Flask backend for election management, this platform ensures that every vote is permanent, verifiable, and tamper-proof.

## 🌟 Key Features

### 🔐 Security & Integrity
-   **Blockchain Backed**: Every vote is recorded as a transaction on the Ethereum blockchain, making it immutable.
-   **One-Vote Policy**: Strict checks ensure each student can only vote once per election cycle.
-   **Session Management**: Secure login and session handling to prevent unauthorized access.

### 📱 Modern User Experience
-   **Responsive Design**: Fully optimized for Desktop, Tablet, and Mobile devices (iPhone/Android).
-   **Hamburger Menu**: Smooth, app-like navigation drawer for mobile users.
-   **Glassmorphism UI**: A premium, dark-mode-first aesthetic with vibrant gradients and animations.
-   **Live Results**: Real-time visualization of vote counts with chart animations.

### 🛠️ Admin Control Center
-   **Dashboard**: A comprehensive admin panel to manage the entire election lifecycle.
-   **Candidate Management**: Add, delete, and update candidates with photos and manifestos.
-   **Election Control**: Start new elections, pause/resume voting, and set deadlines.
-   **Activity Logs**: Monitor voting activity in real-time.

---

## 🏗️ Tech Stack

-   **Backend**: Python, Flask
-   **Database**: SQLite (User/Election Data), Ethereum Blockchain (Vote Records)
-   **Frontend**: HTML5, CSS3 (Custom Design System), JavaScript (Vanilla)
-   **Blockchain Interface**: Web3.py, Solidity (Smart Contract)
-   **Visualization**: Chart.js

---

## 📂 Project Structure

```
DTL FINAL PROTOTYPE/
├── app.py                # Main Flask Application Entry Point
├── database_init.py      # Database Initialization Script
├── election.db           # SQLite Database File
├── templates/            # HTML Templates (Login, Dashboard, Vote, etc.)
├── static/               # Static Assets
│   ├── css/              # Stylesheets (variables.css, login.css, hamburger.css...)
│   ├── jss/              # JavaScript Logic
│   └── images/           # Candidate Photos & Icons
└── requirements.txt      # Python Dependencies
```

---

## 🚀 Setup & Installation

### Prerequisites
-   Python 3.8+
-   Node.js (optional, for advanced tooling)
-   An Ethereum Wallet (e.g., MetaMask) or Private Key for Admin actions.

### 1. Clone & Install Dependencies
Navigate to the project directory and install the required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory and add your blockchain credentials:
```env
PRIVATE_KEY=your_wallet_private_key
INFURA_URL=your_infura_or_alchemy_url
CONTRACT_ADDRESS=deployed_contract_address
```

### 3. Initialize Database
Set up the local SQLite database:
```bash
python database_init.py
```

### 4. Run the Application
Start the Flask server:
```bash
python app.py
```
Access the application at: `http://127.0.0.1:5000`

---

## 📖 Usage Guide

### For Students
1.  **Login**: Use your University Email (e.g., `name@rvce.edu.in`).
2.  **Dashboard**: View election status and quick links.
3.  **Vote**: Select your preferred candidate on the voting page. You can view manifestos before deciding.
4.  **Confirm**: Submit your vote. Wait for the blockchain transaction to confirm.
5.  **Results**: Check the live standings on the results page.

### For Admins
1.  **Access**: Navigate to `/admin` or click "Admin Access" on the login page.
2.  **Manage**: Use the dashboard to add candidates or change election settings.
3.  **Monitor**: Watch the voter log and ensure smooth operation.

---

## 🤝 Contributing
This is a prototype compliant with DTL (Design Thinking Lab) requirements. Future improvements may include decentralized identity verification and multi-election support.

---

**Built with ❤️ for RVCE**
