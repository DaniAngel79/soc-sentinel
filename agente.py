import http.server
import socketserver
import os
import urllib.parse
import urllib.request
import platform

PORT = 8080
LOG_PATH = "/app/logs/ataques_v2.log"

# --- SEGURIDAD: Obtenemos credenciales inyectadas por Kubernetes ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Faltan credenciales de Telegram.")
        return

    try:
        msg_enc = urllib.parse.quote(mensaje)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg_enc}"
        with urllib.request.urlopen(url, timeout=5) as response:
            pass
    except Exception as e:
        print(f"[ERROR] Telegram falló: {e}")

def contar_intentos_globales(ip):
    if not os.path.exists(LOG_PATH): return 0
    try:
        with open(LOG_PATH, "r") as f:
            return f.read().count(f"IP: {ip}")
    except: return 0

class SOCHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        path = urllib.parse.unquote(self.path)
        pod_name = platform.node()

        intentos_previos = contar_intentos_globales(client_ip)

        # 1. VERIFICACIÓN DE BANEO (Filtro Silencioso - Drop)
        if intentos_previos >= 3:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"<h1>403 - BANEADO GLOBALMENTE</h1>")
            return

        # 2. DETECCIÓN DE ATAQUE
        if any(x in path for x in ["admin", "select", "script"]):
            intentos_actuales = intentos_previos + 1
            log_msg = f"ATAQUE: {pod_name} | IP: {client_ip} | INTENTO: {intentos_actuales}"
            
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a") as f:
                f.write(log_msg + "\n")
            
            if intentos_actuales == 3:
                enviar_telegram(f"🚨 [IP BLOQUEADA DEFINITIVAMENTE] {log_msg}")
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"<h1>403 - BANEADO GLOBALMENTE</h1>")
                return
            else:
                enviar_telegram(f"⚠️ [ADVERTENCIA] {log_msg}")

        # 3. RESPUESTA NORMAL
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"<h1>SOC Sentinel v10.0 - Activo en {pod_name}</h1>".encode())

# --- INICIO DEL SERVIDOR (LO QUE FALTABA) ---
with socketserver.TCPServer(("0.0.0.0", PORT), SOCHandler) as httpd:
    print(f"[*] Servidor SOC Sentinel escuchando en el puerto {PORT}")
    httpd.serve_forever()