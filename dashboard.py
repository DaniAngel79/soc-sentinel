import http.server
import socketserver
import os

PORT = 8081
LOG_PATH = "/app/logs/ataques.log"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        contenido_logs = "Sin ataques registrados."
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r") as f:
                lines = f.readlines()
                # Tomar los últimos 10 ataques
                contenido_logs = "<br>".join(lines[-10:])

        html = f"""
        <html>
        <body style='font-family: sans-serif; background-color: #0d1117; color: white; padding: 20px;'>
            <h1>📊 SOC-Sentinel Dashboard</h1>
            <div style='background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 5px;'>
                <h3>Últimas Alertas del IPS:</h3>
                <pre style='color: #ff7b72;'>{contenido_logs}</pre>
            </div>
            <p>Actualizado en tiempo real desde el PVC compartido.</p>
        </body>
        </html>
        """
        self.wfile.write(bytes(html, "utf8"))

with socketserver.TCPServer(("0.0.0.0", PORT), DashboardHandler) as httpd:
    print(f"📈 Dashboard SOC activo en el puerto {PORT}")
    httpd.serve_forever()