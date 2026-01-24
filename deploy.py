import os
import sys
import subprocess

# Ensure libraries are installed
try:
    import solcx
    from web3 import Web3
    from dotenv import load_dotenv
except ImportError:
    print("Installing missing libraries...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "py-solc-x", "web3", "python-dotenv"])
    import solcx
    from web3 import Web3
    from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Configuration
RPC_URL = "https://ethereum-sepolia.publicnode.com"
PRIVATE_KEY = os.getenv("PRIVATE_KEY") or os.getenv("ADMIN_PRIVATE_KEY")
SOL_FILE = "Election.sol"

def deploy():
    print("--- 🚀 Starting Python Deployment ---")
    
    # 1. Check Private Key
    if not PRIVATE_KEY:
        print("❌ ERROR: PRIVATE_KEY or ADMIN_PRIVATE_KEY not found in .env file.")
        print("Please check your .env file.")
        return

    # 2. Install Solidity Compiler
    target_version = "0.8.0"
    print(f"📦 Checking for Solidity Compiler (v{target_version})...")
    
    try:
        installed_versions = solcx.get_installed_solc_versions()
        if target_version not in [str(v) for v in installed_versions]:
            print(f"⬇️  Installing solc v{target_version}...")
            solcx.install_solc(target_version)
            print(f"✅ solc v{target_version} installed successfully.")
        else:
            print(f"✅ solc v{target_version} is already installed.")
            
    except Exception as e:
        print(f"❌ ERROR: Failed to install Solidity Compiler (v{target_version}).")
        print(f"   Reason: {e}")
        print("   👉 Please check your internet connection or install it manually.")
        sys.exit(1)

    # 3. Compile Contract
    print("🔨 Compiling Election.sol...")
    with open(SOL_FILE, "r") as f:
        source = f.read()

    compiled = solcx.compile_standard({
        "language": "Solidity",
        "sources": {SOL_FILE: {"content": source}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
    }, solc_version="0.8.0")

    bytecode = compiled["contracts"][SOL_FILE]["Election"]["evm"]["bytecode"]["object"]
    abi = compiled["contracts"][SOL_FILE]["Election"]["abi"]
    print("✅ Compilation Successful!")

    # 4. Connect to Blockchain
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    connected = False
    if hasattr(w3, 'is_connected'):
        connected = w3.is_connected()
    elif hasattr(w3, 'isConnected'):
        connected = w3.isConnected()
        
    if not connected:
         print(f"❌ Could not connect to {RPC_URL}")
         return 
             
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"👤 Deploying from: {account.address}")
    
    # helper to get balance
    balance = w3.eth.get_balance(account.address)
    
    # Compatibility for from_wei / fromWei
    from_wei = w3.from_wei if hasattr(w3, "from_wei") else w3.fromWei
    print(f"💰 Balance: {from_wei(balance, 'ether')} ETH")
    
    if balance == 0:
        print("❌ ERROR: Wallet has 0 ETH. You need Sepolia ETH to deploy.")
        return

    # 5. Build & Send Transaction
    print("🚀 Sending Deployment Transaction...")
    Election = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Compatibility helpers
    get_tx_count = w3.eth.get_transaction_count if hasattr(w3.eth, "get_transaction_count") else w3.eth.getTransactionCount
    gas_price = w3.eth.gas_price if hasattr(w3.eth, "gas_price") else w3.eth.gasPrice
    
    # Build
    constructor_call = Election.constructor()
    build_txn_method = constructor_call.build_transaction if hasattr(constructor_call, "build_transaction") else constructor_call.buildTransaction
    
    construct_txn = build_txn_method({
        "from": account.address,
        "nonce": get_tx_count(account.address),
        "gasPrice": gas_price
    })
    
    # Sign
    # v6: sign_transaction, v5: signTransaction
    sign_txn = w3.eth.account.sign_transaction if hasattr(w3.eth.account, "sign_transaction") else w3.eth.account.signTransaction
    signed = sign_txn(construct_txn, private_key=PRIVATE_KEY)
    
    # Send
    # v6: send_raw_transaction, v5: sendRawTransaction
    send_raw = w3.eth.send_raw_transaction if hasattr(w3.eth, "send_raw_transaction") else w3.eth.sendRawTransaction
    tx_hash = send_raw(signed.rawTransaction)
    
    print(f"⏳ Transaction Sent! Hash: {tx_hash.hex()}")
    print("Waiting for confirmation...")
    
    # Wait for receipt
    wait_for_receipt = w3.eth.wait_for_transaction_receipt if hasattr(w3.eth, "wait_for_transaction_receipt") else w3.eth.waitForTransactionReceipt
    tx_receipt = wait_for_receipt(tx_hash)
    
    print("-" * 30)
    print("✅ DEPLOYMENT COMPLETE!")
    print(f"📄 NEW CONTRACT ADDRESS: {tx_receipt.contractAddress}")
    print("-" * 30)
    print("👉 Please update your .env file with this address.")

if __name__ == "__main__":
    deploy()
