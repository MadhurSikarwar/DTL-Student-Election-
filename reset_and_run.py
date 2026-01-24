import os
import json
import sys
import subprocess
import time

def cleanup():
    print("🧹 Cleaning up old database and configurations...")
    
    # 1. Delete election.db
    if os.path.exists("election.db"):
        try:
            os.remove("election.db")
            print("✅ Deleted old election.db")
        except Exception as e:
            print(f"❌ Could not delete election.db: {e}")
            
    # 2. Reset election_offsets.json
    print("🔄 Resetting election offsets...")
    with open("election_offsets.json", "w") as f:
        json.dump({"1": [0, 0, 0, 0, 0, 0]}, f, indent=4)
        
    # 3. Reset election_config.json
    print("🔄 Resetting election config...")
    with open("election_config.json", "w") as f:
        json.dump({"currentElectionId": 1}, f, indent=4)
        
    print("✨ Cleanup Complete! Starting App...")
    print("-" * 30)

if __name__ == "__main__":
    cleanup()
    
    # Run app.py
    try:
        subprocess.check_call([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
    except Exception as e:
        print(f"❌ Error running app.py: {e}")
