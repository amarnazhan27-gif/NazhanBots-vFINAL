# termux_version/core/tor_manager.py
import os
import time
import socket
import subprocess

# v17000: SINGULARITY (Tor Circuit Rotation)
# Forces Tor to change IP address dynamically to avoid "Tor Ban".

TOR_CONTROL_PORT = 9051
TOR_PASSWORD = "" # Default is typically empty or 'cookie'

def check_tor_service():
    # Check if Tor is running
    try:
        null = open(os.devnull, 'w')
        subprocess.check_call(["pgrep", "tor"], stdout=null, stderr=null)
        return True
    except:
        return False

def start_tor():
    if not check_tor_service():
        print("🧅 [TOR] Starting Tor Daemon...")
        try:
            subprocess.Popen(["tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5) # Wait for bootstrap
        except Exception as e:
            print(f"⚠️ [TOR] Failed to start: {e}")

def renew_circuit():
    """
    Sends NEWNYM signal to Tor Control Port (9051)
    to force a new Identity (IP).
    """
    try:
        # Requires torrc to have 'ControlPort 9051'
        # Termux default might need config tweak, but we try anyway
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(('127.0.0.1', TOR_CONTROL_PORT))
            
            # Authenticate (Safe fallback)
            s.sendall('AUTHENTICATE "{}"\r\n'.format(TOR_PASSWORD).encode())
            resp = s.recv(1024).decode()
            
            if "250" in resp:
                s.sendall(b'SIGNAL NEWNYM\r\n')
                resp2 = s.recv(1024).decode()
                if "250" in resp2:
                    print("🧅 [TOR] Identity Rotated. New IP Assigned.")
                    return True
            
            print(f"⚠️ [TOR] Signal Failed: {resp}")
            
    except Exception as e:
        # print(f"⚠️ [TOR] Rotation Failed (Is ControlPort 9051 open?): {e}")
        pass
    
    return False

def get_tor_proxy():
    return "socks5://127.0.0.1:9050"
