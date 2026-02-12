# Node-RED

Herramienta de programacion basada en flujos.

## Descripcion

Node-RED es una herramienta de programacion visual para conectar dispositivos,
APIs y servicios. Popular en IoT.

## Acceso

- **URL**: http://nodered.127.0.0.1.traefik.me:9000

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| NODERED_VERSION | latest | Version |

## Primera configuracion

1. Acceder a la URL
2. Configurar credenciales en Settings > Users
3. Habilitar seguridad en settings.js

## Caracteristicas

- Programacion visual con nodos
- MQTT, HTTP, WebSocket
- Ideal para IoT
- Extensible con npm
- Dashboard UI

## Instalar nodos adicionales

Via UI: Menu > Manage palette > Install

O via CLI:
```bash
docker exec -it node-red npm install node-red-contrib-nombre
```

## Nodos populares

- `node-red-dashboard`: UI dashboard
- `node-red-contrib-home-assistant`: Home Assistant
- `node-red-contrib-influxdb`: InfluxDB
- `node-red-contrib-telegrambot`: Telegram
- `node-red-contrib-mongodb`: MongoDB

## Casos de uso

- Automatizacion IoT
- Integracion Home Assistant
- Prototipado rapido
- Data flows
- APIs y webhooks

## Seguridad

Editar `settings.js` para:
- Habilitar autenticacion
- Configurar HTTPS
- Restringir acceso

## Volumenes

- `nodered-data`: Flows, configuracion, nodes instalados

## Documentacion

- https://nodered.org/docs/
