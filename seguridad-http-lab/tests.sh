#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f config.env ]]; then
  echo "ERROR: no existe config.env"
  echo "Copiar primero: cp config.env.example config.env"
  exit 1
fi

source config.env

BASE_URL="https://localhost:${APP_PORT}"

echo
echo "== Test 1: endpoint publico con -k =="
curl -k -i "${BASE_URL}/public"

echo
echo
echo "== Test 2: endpoint privado sin token =="
curl -k -i "${BASE_URL}/private"

echo
echo
echo "== Test 3: endpoint privado con token incorrecto =="
curl -k -i -H "Authorization: Bearer incorrecto" "${BASE_URL}/private"

echo
echo
echo "== Test 4: endpoint privado con token correcto =="
curl -k -i -H "Authorization: Bearer ${APP_TOKEN}" "${BASE_URL}/private"

echo
echo
echo "== Test 5: headers de seguridad =="
curl -k -I "${BASE_URL}/public"

echo
echo
echo "== Test 6: confiar explicitamente en el certificado del laboratorio =="
curl --cacert "${CERT_FILE}" -i "${BASE_URL}/public"

echo
echo
echo "== Test 7: certificado autofirmado, debería fallar sin -k ni --cacert =="
curl -i "${BASE_URL}/public" || true

echo
echo
echo "== Test 8: endpoint inexistente =="
curl -k -i "${BASE_URL}/no-existe"

echo
echo
echo "== Tests finalizados =="
