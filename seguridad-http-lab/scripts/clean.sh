#!/usr/bin/env bash
set -euo pipefail

rm -f config.env
rm -f evidencia.txt respuestas.md
rm -f certs/*.key certs/*.crt certs/*.csr certs/*.pem certs/*.srl
rm -f logs/*.log
rm -rf __pycache__

echo "Laboratorio limpiado."
