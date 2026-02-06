# ntfy

Servidor de notificaciones push simple.

## Descripcion

ntfy permite enviar notificaciones push a moviles y desktops
via HTTP PUT/POST.

## Acceso

- **Web UI**: http://ntfy.127.0.0.1.traefik.me:9000

## Enviar notificacion

```bash
# Simple
curl -d "Hola mundo!" http://ntfy.127.0.0.1.traefik.me:9000/mi-topic

# Con titulo
curl -H "Title: Alerta!" -d "Mensaje" http://ntfy.127.0.0.1.traefik.me:9000/mi-topic

# Con prioridad
curl -H "Priority: high" -d "Urgente!" http://ntfy.127.0.0.1.traefik.me:9000/mi-topic

# Con click action
curl -H "Click: https://example.com" -d "Click aqui" http://ntfy.127.0.0.1.traefik.me:9000/mi-topic
```

## Apps

- Android: ntfy (Google Play / F-Droid)
- iOS: ntfy
- Web: Acceder a la URL

## Suscribirse

1. Instalar app en movil
2. Añadir servidor: http://ntfy.127.0.0.1.traefik.me:9000
3. Suscribirse a topic: mi-topic

## Integraciones

- Watchtower
- Uptime Kuma
- Grafana
- Scripts propios

## Python

```python
import requests

requests.post(
    "http://ntfy.127.0.0.1.traefik.me:9000/mi-topic",
    data="Notificacion!",
    headers={"Title": "Mi App"}
)
```

## Documentacion

- https://docs.ntfy.sh/
