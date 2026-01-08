import threading
import time
import socket
import requests
from flask import Flask, render_template, jsonify
from dnslib import DNSRecord, QTYPE, RCODE, RR, A
from dnslib.server import DNSServer, DNSHandler, BaseResolver, DNSLogger

# --- KONFIGURATION ---
BLOCKLIST_URL = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
UPSTREAM_DNS = "8.8.8.8"  # Google DNS als Backup
WEB_PORT = 80
DNS_PORT = 53
HOST_IP = "0.0.0.0"  # Auf allen Interfaces lauschen

# --- SPEICHER (In-Memory Database) ---
blocked_domains = set()
logs = []  # Hier speichern wir die letzten Anfragen
stats = {"blocked": 0, "allowed": 0, "total": 0}

app = Flask(__name__)

# --- 1. DER DNS RESOLVER (Die Logik) ---
class GhostResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname).strip('.')
        reply = request.reply()
        
        # LOGGING START
        client_ip = handler.client_address[0]
        timestamp = time.strftime("%H:%M:%S")
        status = "ALLOWED"
        
        # FILTER LOGIK
        if qname in blocked_domains:
            # BLOCKIEREN! (Antworte mit 0.0.0.0)
            reply.rr = []
            reply.add_answer(*RR.fromZone(f"{qname}. 60 A 0.0.0.0"))
            stats["blocked"] += 1
            status = "BLOCKED"
        else:
            # DURCHLASSEN (Frage Google)
            try:
                proxy_r = requests.utils.default_headers()
                # Einfacher Forwarder (vereinfacht für Python pur)
                # In Produktion würde man dnslib's ProxyResolver nutzen
                # Hier simulieren wir den Pass-Through für die Demo
                a_record = socket.gethostbyname(qname)
                reply.add_answer(*RR.fromZone(f"{qname}. 60 A {a_record}"))
                stats["allowed"] += 1
            except:
                reply.header.rcode = RCODE.NXDOMAIN

        stats["total"] += 1
        
        # LIVE LOG SPEICHERN (Max 50 Einträge behalten)
        logs.insert(0, {
            "time": timestamp,
            "client": client_ip,
            "domain": qname,
            "status": status
        })
        if len(logs) > 50: logs.pop()
        
        return reply

# --- 2. DAS WEB DASHBOARD (Flask) ---
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    # Diese API wird vom Dashboard alle 2 Sekunden abgerufen
    return jsonify({
        "stats": stats,
        "logs": logs[:20] # Sende die neuesten 20 Logs
    })

# --- 3. STARTUP SKRIPT ---
def load_gravity():
    print(">>> Lade Blocklisten (Gravity)...")
    try:
        r = requests.get(BLOCKLIST_URL)
        for line in r.text.splitlines():
            if line.startswith("0.0.0.0"):
                parts = line.split()
                if len(parts) >= 2:
                    blocked_domains.add(parts[1])
        print(f">>> {len(blocked_domains)} Domains in die Blacklist geladen.")
    except Exception as e:
        print(f"Fehler beim Laden der Listen: {e}")

def start_dns():
    resolver = GhostResolver()
    server = DNSServer(resolver, port=DNS_PORT, address=HOST_IP)
    server.start_thread()
    print(f">>> DNS Server läuft auf Port {DNS_PORT}")

if __name__ == "__main__":
    print("--- GHOSTSHIELD STARTET ---")
    load_gravity()
    
    # DNS Server in eigenem Thread starten
    dns_thread = threading.Thread(target=start_dns)
    dns_thread.daemon = True
    dns_thread.start()
    
    # Webserver starten
    print(f">>> Dashboard läuft auf http://localhost:{WEB_PORT}")
    try:
        app.run(host=HOST_IP, port=WEB_PORT, debug=False, use_reloader=False)
    except PermissionError:
        print("FEHLER: Bitte mit 'sudo' starten (Port 53/80 brauchen Root-Rechte).")