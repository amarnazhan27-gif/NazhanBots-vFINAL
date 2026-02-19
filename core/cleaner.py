# termux_version/core/cleaner.py
import os
import shutil
import time
from datetime import datetime

# CLEANER MODULE (v40 Immortal)
# Prevents storage overflow by rotating logs.

LOG_FILE = os.path.join(os.path.dirname(__file__), '../logs/success.txt')
MAX_SIZE_MB = 5

def self_clean():
    if not os.path.exists(LOG_FILE):
        return

    size_mb = os.path.getsize(LOG_FILE) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"logs/archive_{timestamp}.txt"
        archive_path = os.path.join(os.path.dirname(__file__), f'../{archive_name}')
        
        try:
            shutil.move(LOG_FILE, archive_path)
            # Create fresh file
            open(LOG_FILE, 'w').close()
            print(f"🧹 [CLEANER] Logs rotated: {archive_name}")
            
            # v5000: Delete old archives
            cleanup_old_archives()
            
        except Exception as e:
            print(f"⚠️ [CLEANER] Fail: {e}")

def cleanup_old_archives():
    log_dir = os.path.dirname(LOG_FILE)
    now = time.time()
    retention_days = 7
    
    for filename in os.listdir(log_dir):
        if filename.startswith("archive_") and filename.endswith(".txt"):
            filepath = os.path.join(log_dir, filename)
            # Check age
            if os.stat(filepath).st_mtime < now - (retention_days * 86400):
                try:
                    # v9000: Use Shredder
                    from .shredder import secure_delete
                    secure_delete(filepath)
                except: pass

    # v33000: DEEP CLEAN (Temp Files)
    try:
        root_dir = os.path.dirname(os.path.dirname(__file__))
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".tmp") or file.endswith(".log") or file == "nohup.out":
                    path = os.path.join(root, file)
                    try: os.remove(path)
                    except: pass
    except: pass
