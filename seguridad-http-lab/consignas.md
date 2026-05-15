# Laboratorio: Seguridad HTTP/TLS con certificados autofirmados

## Contexto

En la clase anterior se trabajaron conceptos de redes TCP/IP en GNU/Linux: procesos, sockets, puertos, direcciones IP, HTTP, headers, códigos de estado y uso de `curl`.

En este laboratorio se agrega una capa de seguridad sobre esos conceptos: HTTPS/TLS, certificados, headers de autorización y exposición de información sensible.

La actividad está diseñada para ejecutarse en una VM compartida, sin usar `sudo`.

---

## Objetivos

Al finalizar el laboratorio deberías poder:

- Levantar una API HTTPS en un puerto alto.
- Generar manualmente una clave privada.
- Crear una solicitud de certificado.
- Crear un certificado autofirmado.
- Probar una API HTTPS con `curl`.
- Explicar por qué un certificado autofirmado no es confiable por defecto.
- Usar `Authorization: Bearer <token>`.
- Diferenciar `401 Unauthorized` y `403 Forbidden`.
- Identificar información sensible que no debería exponerse en una respuesta HTTP.

---

## Requisitos

La VM debe tener disponibles:

```bash
python3
openssl
curl
bash
```

No se requiere `sudo`.

---

## 1. Preparar el laboratorio

Descomprimir el archivo entregado por el docente:

```bash
tar xzf seguridad-http-lab.tar.gz
cd seguridad-http-lab
```

Copiar la configuración de ejemplo:

```bash
cp config.env.example config.env
```

Editar el archivo:

```bash
nano config.env
```

Modificar el puerto y token asignados por el docente:

```bash
APP_PORT=9443
APP_TOKEN=token-alumno01
```

Si la VM es compartida, cada alumno o grupo debe usar un puerto distinto.

---

## 2. Crear directorio de certificados

```bash
mkdir -p certs
```

---

## 3. Crear la clave privada

```bash
openssl genrsa -out certs/server.key 2048
```

Verificar:

```bash
ls -l certs/server.key
```

La clave privada identifica al servidor y no debe compartirse.

---

## 4. Crear archivo de configuración del certificado

Crear el archivo:

```bash
nano certs/server.cnf
```

Contenido:

```ini
[ req ]
default_bits       = 2048
prompt             = no
default_md         = sha256
distinguished_name = dn
req_extensions     = req_ext

[ dn ]
C  = AR
ST = Buenos Aires
L  = Buenos Aires
O  = Laboratorio SO y Redes
OU = Seguridad
CN = localhost

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
IP.1  = 127.0.0.1
```

---

## 5. Crear CSR

```bash
openssl req -new \
  -key certs/server.key \
  -out certs/server.csr \
  -config certs/server.cnf
```

Verificar:

```bash
ls -l certs/server.csr
```

El archivo `server.csr` es una solicitud de certificado.

En un caso real, se enviaría a una Autoridad Certificante. En este laboratorio, lo vamos a firmar nosotros mismos.

---

## 6. Crear certificado autofirmado

```bash
openssl x509 -req \
  -in certs/server.csr \
  -signkey certs/server.key \
  -out certs/server.crt \
  -days 7 \
  -sha256 \
  -extensions req_ext \
  -extfile certs/server.cnf
```

Verificar:

```bash
ls -l certs/
```

Deberían existir:

```text
server.cnf
server.crt
server.csr
server.key
```

---

## 7. Inspeccionar el certificado

Ver sujeto, emisor y fechas:

```bash
openssl x509 -in certs/server.crt -noout -subject -issuer -dates
```

Ver Subject Alternative Name:

```bash
openssl x509 -in certs/server.crt -noout -text | grep -A2 "Subject Alternative Name"
```

---

## 8. Ejecutar la API HTTPS

```bash
python3 app.py
```

Deberías ver un mensaje similar a:

```text
Servidor HTTPS iniciado en https://0.0.0.0:9443
Token esperado: token-alumno01
```

Dejar esta terminal abierta.

---

## 9. Probar desde otra terminal

Entrar nuevamente al directorio del laboratorio:

```bash
cd seguridad-http-lab
source config.env
```

### 9.1 Probar sin confiar en el certificado

```bash
curl https://localhost:${APP_PORT}/public
```

Debe fallar por certificado autofirmado.

### 9.2 Probar ignorando la validación

```bash
curl -k https://localhost:${APP_PORT}/public
```

Debe responder correctamente.

### 9.3 Probar confiando explícitamente en el certificado

```bash
curl --cacert certs/server.crt https://localhost:${APP_PORT}/public
```

Debe responder correctamente.

---

## 10. Probar autenticación con token

### Endpoint privado sin token

```bash
curl -k -i https://localhost:${APP_PORT}/private
```

Debe responder `401 Unauthorized`.

### Endpoint privado con token incorrecto

```bash
curl -k -i \
  -H "Authorization: Bearer incorrecto" \
  https://localhost:${APP_PORT}/private
```

Debe responder `403 Forbidden`.

### Endpoint privado con token correcto

```bash
curl -k -i \
  -H "Authorization: Bearer ${APP_TOKEN}" \
  https://localhost:${APP_PORT}/private
```

Debe responder `200 OK`.

---

## 11. Ejecutar script de pruebas

```bash
chmod +x tests.sh
./tests.sh
```

Guardar la salida en un archivo:

```bash
./tests.sh > evidencia.txt 2>&1
```

---

## 12. Revisar logs

Ver el archivo de logs generado por la aplicación:

```bash
cat logs/access.log
```

Responder:

- ¿Qué información aparece en el log?
- ¿Aparece el token?
- ¿Sería seguro guardar tokens completos en logs?

---

## 13. Entrega

Entregar un archivo `.tar.gz` con:

```text
seguridad-http-lab/
├── app.py
├── config.env
├── certs/
│   ├── server.cnf
│   ├── server.csr
│   └── server.crt
├── evidencia.txt
└── respuestas.md
```

No entregar:

```text
certs/server.key
logs/access.log
```

La clave privada no debe compartirse.

---

## 14. Preguntas a responder

Usar `respuestas-template.md` como base.

Preguntas:

1. ¿Qué archivo representa la clave privada del servidor?
2. ¿Qué archivo representa la solicitud de certificado?
3. ¿Qué archivo usa el servidor para presentarse ante el cliente?
4. ¿Por qué `curl` falla si no usamos `-k` ni `--cacert`?
5. ¿Qué diferencia hay entre usar `-k` y usar `--cacert`?
6. ¿Por qué un certificado autofirmado no es confiable por defecto?
7. ¿Qué información muestra el campo `Subject`?
8. ¿Qué significa `Subject Alternative Name`?
9. ¿HTTPS reemplaza la autenticación con token?
10. ¿Qué protege TLS y qué no protege?
11. ¿Qué diferencia hay entre `401 Unauthorized` y `403 Forbidden`?
12. ¿Por qué un endpoint `/debug` no debería mostrar tokens, rutas internas o variables del sistema?
13. ¿Qué headers de seguridad devuelve el servidor?
14. ¿Qué información aparece en `logs/access.log`?
15. ¿Por qué no se debe entregar `server.key`?
