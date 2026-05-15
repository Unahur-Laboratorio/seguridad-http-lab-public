#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_NAME="seguridad-http-lab.tar.gz"

cd "${ROOT_DIR}/.."

tar czf "${PACKAGE_NAME}" seguridad-http-lab \
  --exclude='seguridad-http-lab/.git' \
  --exclude='seguridad-http-lab/config.env' \
  --exclude='seguridad-http-lab/certs/*.key' \
  --exclude='seguridad-http-lab/certs/*.crt' \
  --exclude='seguridad-http-lab/certs/*.csr' \
  --exclude='seguridad-http-lab/logs/*.log' \
  --exclude='seguridad-http-lab/__pycache__'

echo "Paquete generado: ${PACKAGE_NAME}"
