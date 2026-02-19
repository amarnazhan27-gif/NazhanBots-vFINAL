# SKYNET GUARDIAN (v100 IMMORTAL)
# Auto-Restarts, Auto-Updates, and Auto-Heals the Server.

echo -e "\e[1;31m👁️ SKYNET GUARDIAN ACTIVE [IMMORTAL MODE]\e[0m"
echo -e "\e[1;30mMonitoring 'main.py' process...\e[0m"

# Prevent Sleep
termux-wake-lock

while true; do
    # v2000: Check for Vanish Lock (Poison Pill)
    if [ -f ".vanish_lock" ]; then
        echo -e "\e[1;31m💀 VANISH PROTOCOL DETECTED. GUARDIAN TERMINATING.\e[0m"
        # Delete self (Guardian)
        rm -- "$0"
        exit 0
    fi

    if pgrep -f "python main.py" > /dev/null; then
        # Process is running, sleep 5s
        sleep 5
    else
        echo -e "\e[1;33m⚠️ Server Down! Initiating Resurrection Protocol...\e[0m"
        
        # v100: Auto Update
        git pull origin main > /dev/null 2>&1
        
        # v100: Auto-Install Deps
        pip install -r requirements.txt --disable-pip-version-check --no-python-version-warning > /dev/null 2>&1
        
        # v9999: Start Tor
        if ! pgrep -x "tor" > /dev/null; then
             tor > /dev/null 2>&1 &
        fi

        # v9000: GHOST LAUNCH
        # We use a trick to change argv[0] to look like a system service
        # Note: 'exec -a' works for bash, but python process title needs setproctitle module (added in main.py)
        # Here we just launch normally, main.py handles the rest.
        python main.py --guardian &
        echo -e "\e[1;32m✅ Server Resurrected. (PID: $!)\e[0m"
    fi
    sleep 10
done
