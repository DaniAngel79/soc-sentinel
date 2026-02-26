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
    # Validación: Comprobar que Kubernetes inyectó el Secret correctamente
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Faltan las credenciales de Telegram en las variables de entorno.")
        return

    print(f"[DEBUG] Iniciando envío de alerta...")
    try:
        msg_enc = urllib.parse.quote(mensaje)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg_enc}"
        with urllib.request.urlopen(url, timeout=5) as response:
            print(f"[DEBUG] Telegram respondió código: {response.getcode()}")
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

        # 1. DETECCIÓN DE ATAQUE
        if any(x in path for x in ["admin", "select", "script"]):
            intentos_actuales = contar_intentos_globales(client_ip) + 1
            log_msg = f"ATAQUE: {pod_name} | IP: {client_ip} | INTENTO: {intentos_actuales}"
            
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a") as f:
                f.write(log_msg + "\n")
            
            enviar_telegram(f"🚨 {log_msg}")

        # 2. VERIFICACIÓN DE BANEO
        if contar_intentos_globales(client_ip) >= 3:
            print(f"[BLOQUEO] IP {client_ip} bloqueada.")
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"<h1>403 - BANEADO GLOBALMENTE</h1>")
            return

        # 3. RESPUESTA NORMAL
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"<h1>SOC Sentinel v10.0 - Activo en {pod_name}</h1>".encode())

with socketserver.TCPServer(("0.0.0.0", PORT), SOCHandler) as httpd:
    httpd.serve_forever()
