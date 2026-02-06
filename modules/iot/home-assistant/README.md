# Home Assistant

Plataforma de automatizacion del hogar.

## Descripcion

Home Assistant es la plataforma de domotica open source mas popular.
Integra miles de dispositivos y servicios.

## Acceso

- **URL**: http://hass.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Acceder a la URL
2. Crear cuenta de admin
3. Configurar ubicacion y unidades

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| HASS_VERSION | stable | Version |

## Integraciones populares

- Philips Hue
- Zigbee (via ZHA o Zigbee2MQTT)
- Z-Wave
- Google Home
- Amazon Alexa
- MQTT
- ESPHome

## Automatizaciones

```yaml
automation:
  - alias: "Encender luces al atardecer"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: light.turn_on
        target:
          entity_id: light.salon
```

## Add-ons

Para desarrollo, considera usar HACS (Home Assistant Community Store)
para instalar integraciones adicionales.

## Volumenes

- `hass-config`: Configuracion completa

## Documentacion

- https://www.home-assistant.io/docs/
