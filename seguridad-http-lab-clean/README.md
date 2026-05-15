# Seguridad HTTP/TLS Lab

Laboratorio práctico de redes y seguridad para GNU/Linux, diseñado para ejecutarse en VMs pequeñas y compartidas, sin requerir privilegios de `sudo`.

La actividad trabaja sobre una API HTTPS simple ejecutada por cada alumno en un puerto alto. Permite practicar:

- Puertos y servicios TCP.
- HTTP y códigos de estado.
- Headers HTTP.
- Autenticación básica con `Authorization: Bearer`.
- Diferencia entre `401 Unauthorized` y `403 Forbidden`.
- Certificados autofirmados.
- Diferencia entre cifrado, identidad y confianza.
- Uso de `curl` con HTTPS.
- Riesgo de exponer información sensible en endpoints de debug.

## Requisitos

En la VM deben estar disponibles:

- `python3`
- `openssl`
- `curl`
- `bash`

No se requiere `sudo`.

## Estructura del repositorio

```text
seguridad-http-lab/
├── README.md
├── app.py
├── config.env.example
├── tests.sh
├── consignas.md
├── respuestas-template.md
├── .gitignore
├── certs/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
└── scripts/
    ├── package.sh
    └── clean.sh
```

## Uso rápido

1. Copiar el archivo de configuración:

```bash
cp config.env.example config.env
```

2. Editar `config.env` y ajustar el puerto y token asignado:

```bash
nano config.env
```

3. Crear manualmente los certificados siguiendo `consignas.md`.

4. Ejecutar la API:

```bash
python3 app.py
```

5. En otra terminal, ejecutar pruebas:

```bash
chmod +x tests.sh
./tests.sh
```

## Importante

No entregar ni compartir la clave privada `certs/server.key`.

La clave privada debe existir localmente para que el servidor HTTPS funcione, pero no debe subirse a repositorios ni incluirse en entregas.
