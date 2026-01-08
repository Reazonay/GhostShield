import threading
import time
import socket
from flask import Flask, render_template, jsonify
from dnslib import DNSRecord, QTYPE, RR, A
from dnslib.server import DNSServer, BaseResolver

# --- KONFIGURATION ---
# Wir nutzen eine aggressivere Liste für Werbung, aber lassen Google Dienste leben
BLOCKLIST_URL = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
UPSTREAM_DNS = "8.8.8.8"  # Google DNS
UPSTREAM_PORT = 53
WEB_PORT = 80             # Oder 8080, falls 80 belegt ist
DNS_PORT = 53
HOST_IP = "0.0.0.0"

# --- SPEICHER ---
blocked_domains = set()
logs = []
stats = {"blocked": 0, "allowed": 0, "total": 0}

# Cache für Gerätenamen (damit wir nicht jedes Mal fragen müssen)
device_cache = {}

app = Flask(__name__)

# --- HELFER: GERÄTENAMEN FINDEN ---
def get_device_name(ip):
    if ip in device_cache:
        return device_cache[ip]
    try:
        # Fragt den Router: "Wer ist diese IP?"
        hostname = socket.gethostbyaddr(ip)[0]
        device_cache[ip] = hostname
        return hostname
    except:
        return "Unknown Device"

# --- 1. DER DNS RESOLVER (Die Logik) ---
class GhostResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname).strip('.')
        reply = request.reply()
        
        client_ip = handler.client_address[0]
        device_name = get_device_name(client_ip)
        timestamp = time.strftime("%H:%M:%S")
        status = "ALLOWED"

        # 1. PRÜFUNG: IST ES WERBUNG?
        if qname in blocked_domains:
            reply.rr = []
            reply.add_answer(*RR.fromZone(f"{qname}. 60 A 0.0.0.0"))
            stats["blocked"] += 1
            status = "BLOCKED"
            print(f"[BLOCK] {qname} von {device_name}")
        
        # 2. WENN NICHT: FRAGE GOOGLE (Forwarding)
        else:
            try:
                # Wir leiten die exakte Anfrage an 8.8.8.8 weiter
                upstream_req = request.send(UPSTREAM_DNS, UPSTREAM_PORT, timeout=2)
                reply = DNSRecord.parse(upstream_req)
                stats["allowed"] += 1
            except Exception as e:
                print(f"[ERROR] Forwarding failed: {e}")
                # Wenn Internet weg ist, leere Antwort senden
                reply.header.rcode = 2 # SERVFAIL

        stats["total"] += 1
        
        # LOGGING FÜR DASHBOARD
        logs.insert(0, {
            "time": timestamp,
            "client_ip": client_ip,
            "client_name": device_name, # <-- NEU: Der Name!
            "domain": qname,
            "status": status
        })
        # Behalte nur die letzten 50 Logs im Speicher
        if len(logs) > 50: logs.pop()
        
        return reply

# --- 2. WEB DASHBOARD API ---
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    return jsonify({"stats": stats, "logs": logs})

# --- 3. STARTUP ---
def load_gravity():
    import requests
    print(">>> Lade Blocklisten...")
    try:
        r = requests.get(BLOCKLIST_URL)
        for line in r.text.splitlines():
            if line.startswith("0.0.0.0"):
                parts = line.split()
                if len(parts) >= 2:
                    blocked_domains.add(parts[1])
        print(f">>> {len(blocked_domains)} Domains geblockt.")
    except Exception as e:
        print(f"Fehler beim Laden der Liste: {e}")

if __name__ == "__main__":
    load_gravity()
    
    # DNS Server starten
    resolver = GhostResolver()
    server = DNSServer(resolver, port=DNS_PORT, address=HOST_IP)
    server.start_thread()
    
    # Webserver starten
    print(f">>> Dashboard läuft auf http://<RASPI-IP>:{WEB_PORT}")
    try:
        app.run(host=HOST_IP, port=WEB_PORT, debug=False, use_reloader=False)
    except:
        print("FEHLER: Port belegt? Starte mit 'sudo'!")
