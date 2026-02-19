# termux_version/core/dashboard.py
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# v11000 SUPREMACY: WEB COMMAND CENTER
# Zero-Dependency HTTP Server (No Flask/Bottle needed for maximum stability)

PORT = 1337
LOG_FILE = os.path.join(os.path.dirname(__file__), '../logs/success.txt')
STATS_FILE = os.path.join(os.path.dirname(__file__), '../logs/dashboard_stats.json')

# HTML Template (Embedded for single-file portability)
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NAZHANBOTS SUPREMACY</title>
    <style>
        body { background-color: #0f0f0f; color: #00ff7f; font-family: 'Courier New', monospace; padding: 20px; }
        h1 { border-bottom: 2px solid #00ff7f; padding-bottom: 10px; }
        .card { background: #1a1a1a; padding: 15px; margin-bottom: 15px; border: 1px solid #333; box-shadow: 0 0 10px rgba(0, 255, 127, 0.2); }
        .stat-value { font-size: 2em; font-weight: bold; }
        .log-box { height: 300px; overflow-y: scroll; background: #000; padding: 10px; border: 1px solid #333; font-size: 0.9em; }
        .btn { background: #00ff7f; color: #000; padding: 10px 20px; border: none; font-weight: bold; cursor: pointer; }
        .btn:hover { background: #fff; }
        .refresh { float: right; cursor: pointer; }
    </style>
    <script>
        function refreshStats() {
            fetch('/api/stats').then(r => r.json()).then(data => {
                document.getElementById('total-sent').innerText = data.total_sent;
                document.getElementById('apis-active').innerText = data.active_apis;
                document.getElementById('uptime').innerText = data.uptime + "s";
                
                let logs = "";
                data.logs.forEach(l => logs += `<div>> ${l}</div>`);
                document.getElementById('logs').innerHTML = logs;
            });
        }
        setInterval(refreshStats, 2000);
    </script>
</head>
<body>
    <h1>NAZHANBOTS v11000 <span class="refresh" onclick="refreshStats()">↻</span></h1>
    
    <div class="card">
        <h3>⚡ SYSTEM STATUS</h3>
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
                <div class="stat-value" id="total-sent">0</div>
                <div>TOTAL ATTACKS</div>
            </div>
            <div>
                <div class="stat-value" id="apis-active">0</div>
                <div>ACTIVE APIS</div>
            </div>
            <div>
                <div class="stat-value" id="uptime">0s</div>
                <div>UPTIME</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h3>📟 LIVE LOGS</h3>
        <div class="log-box" id="logs">Loading...</div>
    </div>
    
    <div class="card">
        <h3>🎮 CONTROLS</h3>
        <p>Use Termux Terminal to start attacks. This panel is for Monitoring.</p>
    </div>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
            
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Gather Stats
            sent = 0
            recent_logs = []
            if os.path.exists(LOG_FILE):
                try:
                    with open(LOG_FILE, 'r') as f:
                        lines = f.readlines()
                        sent = len(lines)
                        recent_logs = [l.strip() for l in lines[-20:]]
                        recent_logs.reverse()
                except: pass
            
            apis = 0
            try:
                with open(os.path.join(os.path.dirname(__file__), '../config/apis.json')) as f:
                    apis = len(json.load(f))
            except: pass
            
            import time
            # Accurate Uptime
            try:
                uptime = int(time.time() - START_TIME)
            except:
                uptime = 0
            
            data = {
                "total_sent": sent,
                "active_apis": apis,
                "uptime": format_uptime(uptime),
                "logs": recent_logs
            }
            self.wfile.write(json.dumps(data).encode())
            
    def log_message(self, format, *args):
        return # Silence console logs

def format_uptime(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s"

# Track start time
START_TIME = time.time()

def start_server():
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"🖥️ [SUPREMACY] Web Dashboard Active: http://localhost:{PORT}")
    server.serve_forever()

def launch_dashboard():
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
