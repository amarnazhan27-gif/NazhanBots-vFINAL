# termux_version/core/web_reporter_lite.py
import json
import os
import time

# WEB REPORTER LITE (v110)
# Generates a static index.html for viewing status via simple HTTP server.

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SUPERIOR INFINITY STATUS</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ background: #000; color: #0f0; font-family: monospace; text-align: center; padding: 50px; }}
        h1 {{ font-size: 3rem; text-shadow: 0 0 10px #0f0; }}
        .stat-box {{ border: 2px solid #0f0; padding: 20px; display: inline-block; margin: 10px; }}
        .value {{ font-size: 2rem; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🦅 SUPERIOR INFINITY</h1>
    <div class="stat-box">
        <div>TOTAL HITS</div>
        <div class="value">{hits}</div>
    </div>
    <div class="stat-box">
        <div>ACTIVE APIS</div>
        <div class="value">{apis}</div>
    </div>
    <div class="stat-box">
        <div>LAST UPDATE</div>
        <div class="value">{last_update}</div>
    </div>
    <p>System Online • Protected by Skynet</p>
</body>
</html>
"""

def generate_static_dashboard():
    stats_path = os.path.join(os.path.dirname(__file__), '../logs/stats.json')
    apis_path = os.path.join(os.path.dirname(__file__), '../config/apis.json')
    html_path = os.path.join(os.path.dirname(__file__), '../dashboard.html')
    
    hits = 0
    try:
        with open(stats_path, 'r') as f: hits = json.load(f).get("total_hits", 0)
    except: pass
    
    api_count = 0
    try:
        with open(apis_path, 'r') as f: api_count = len(json.load(f))
    except: pass
    
    html = TEMPLATE.format(
        hits=hits,
        apis=api_count,
        last_update=time.strftime("%H:%M:%S")
    )
    
    with open(html_path, 'w') as f: f.write(html)
