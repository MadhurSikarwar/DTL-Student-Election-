import shutil
import os

src = r"C:\Users\Madhu\.gemini\antigravity\brain\67022455-1c0d-4266-b3c7-e8e8afdba672\winner_background_premium_1769090362632.png"
dst = r"c:\Users\Madhu\OneDrive\Desktop\DTL\static\images\winner-bg-premium.png"

try:
    shutil.copy2(src, dst)
    print("Image copied successfully.")
except Exception as e:
    print(f"Error moving image: {e}")
