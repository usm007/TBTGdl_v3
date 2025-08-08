import traceback
from datetime import datetime

def log_crash(e):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"crash_log_{timestamp}.txt"
    with open(log_filename, "w", encoding="utf-8") as f:
        f.write("❌ TELEGRAM VIDEO DOWNLOADER - CRASH LOG\n")
        f.write(f"🕒 Timestamp: {timestamp}\n")
        f.write(f"💥 Exception Type: {type(e).__name__}\n")
        f.write(f"📝 Error Message: {str(e)}\n\n")
        f.write("🔍 Full Traceback:\n")
        f.write(traceback.format_exc())
    print(f"\n[!] The script crashed. Details saved in '{log_filename}'.")
