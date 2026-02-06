# Frigate

NVR con deteccion de objetos mediante AI.

## Descripcion

Frigate es un NVR que usa deteccion de objetos en tiempo real
para camaras de seguridad.

## Acceso

- **URL**: http://frigate.127.0.0.1.traefik.me:9000

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| FRIGATE_VERSION | stable | Version |

## Configuracion

Editar `config.yml`:

```yaml
cameras:
  entrada:
    ffmpeg:
      inputs:
        - path: rtsp://user:pass@192.168.1.100:554/stream
          roles:
            - detect
            - record
    detect:
      enabled: true
      width: 1280
      height: 720
    record:
      enabled: true
      retain:
        days: 7

detectors:
  cpu1:
    type: cpu
```

## Deteccion

- person
- car
- dog
- cat
- Y mas...

## Hardware Acceleration

Soporta:
- Intel GPU (OpenVINO)
- NVIDIA GPU (TensorRT)
- Google Coral TPU

## Integracion Home Assistant

Usar la integracion oficial de Frigate en HACS.

## Volumenes

- `frigate-media`: Grabaciones y snapshots

## Documentacion

- https://docs.frigate.video/
