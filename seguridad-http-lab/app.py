#!/usr/bin/env python3

import os
import ssl
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


def load_config(path="config.env"):
    config = {}

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()

    return config


CONFIG = load_config()

APP_HOST = CONFIG.get("APP_HOST", "0.0.0.0")
APP_PORT = int(CONFIG.get("APP_PORT", "9443"))
APP_TOKEN = CONFIG.get("APP_TOKEN", "token-demo")
CERT_FILE = CONFIG.get("CERT_FILE", "certs/server.crt")
KEY_FILE = CONFIG.get("KEY_FILE", "certs/server.key")
LOG_FILE = CONFIG.get("LOG_FILE", "logs/access.log")


class SecurityLabHandler(BaseHTTPRequestHandler):
    server_version = "SecurityLabHTTP/1.0"

    def write_access_log(self, status_code):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

        timestamp = datetime.now().isoformat(timespec="seconds")
        client_ip = self.client_address[0]
        user_agent = self.headers.get("User-Agent", "-")

        line = (
            f'{timestamp} {client_ip} '
            f'"{self.command} {self.path} {self.request_version}" '
            f'{status_code} "{user_agent}"\n'
        )

        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(line)

    def send_json(self, status_code, payload):
        body = json.dumps(payload, indent=2).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))

        # Headers de seguridad básicos para observar con curl -I.
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")

        self.end_headers()
        self.wfile.write(body)

        self.write_access_log(status_code)

    def get_authorization_token(self):
        auth_header = self.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return None

        return auth_header.replace("Bearer ", "", 1).strip()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            self.send_json(200, {
                "message": "Security Lab API",
                "endpoints": ["/public", "/private", "/debug", "/headers"]
            })
            return

        if path == "/public":
            self.send_json(200, {
                "status": "ok",
                "message": "endpoint publico"
            })
            return

        if path == "/private":
            token = self.get_authorization_token()

            if token is None:
                self.send_json(401, {
                    "error": "unauthorized",
                    "message": "falta header Authorization: Bearer <token>"
                })
                return

            if token != APP_TOKEN:
                self.send_json(403, {
                    "error": "forbidden",
                    "message": "token invalido"
                })
                return

            self.send_json(200, {
                "status": "ok",
                "message": "acceso autorizado"
            })
            return

        if path == "/debug":
            # Endpoint corregido: no expone token, rutas internas ni variables sensibles.
            self.send_json(200, {
                "status": "debug disabled",
                "message": "no se expone informacion sensible"
            })
            return

        if path == "/headers":
            safe_headers = {
                "Host": self.headers.get("Host"),
                "User-Agent": self.headers.get("User-Agent"),
                "Accept": self.headers.get("Accept"),
                "Authorization": "present" if self.headers.get("Authorization") else "not present"
            }

            self.send_json(200, {
                "message": "headers recibidos",
                "headers": safe_headers
            })
            return

        self.send_json(404, {
            "error": "not_found",
            "message": "endpoint inexistente"
        })

    def log_message(self, format, *args):
        # Evita el log por defecto en stderr; usamos logs/access.log.
        return


def main():
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        print("ERROR: No se encontraron los certificados.")
        print("Primero generar manualmente:")
        print("  certs/server.key")
        print("  certs/server.crt")
        print()
        print("Ver instrucciones en consignas.md")
        return

    httpd = HTTPServer((APP_HOST, APP_PORT), SecurityLabHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Servidor HTTPS iniciado en https://{APP_HOST}:{APP_PORT}")
    print(f"Token esperado: {APP_TOKEN}")
    print(f"Certificado: {CERT_FILE}")
    print(f"Clave privada: {KEY_FILE}")
    print(f"Log de accesos: {LOG_FILE}")
    print("Presionar Ctrl+C para detener.")

    httpd.serve_forever()


if __name__ == "__main__":
    main()
