# Watchtower

Actualizacion automatica de contenedores Docker.

## Descripcion

Watchtower monitoriza contenedores y los actualiza automaticamente
cuando hay nuevas imagenes disponibles.

## Funcionamiento

- Revisa imagenes cada 24h (configurable)
- Descarga nuevas versiones
- Recrea contenedores con la nueva imagen
- Limpia imagenes antiguas

## Configuracion

| Variable | Default | Descripcion |
|----------|---------|-------------|
| WATCHTOWER_POLL_INTERVAL | 86400 | Segundos entre checks (24h) |
| WATCHTOWER_CLEANUP | true | Eliminar imagenes antiguas |
| WATCHTOWER_INCLUDE_STOPPED | false | Actualizar contenedores parados |

## Excluir contenedores

Añadir label al contenedor:
```yaml
labels:
  - "com.centurylinklabs.watchtower.enable=false"
```

## Solo ciertos contenedores

```yaml
environment:
  - WATCHTOWER_LABEL_ENABLE=true
```

Y añadir a contenedores deseados:
```yaml
labels:
  - "com.centurylinklabs.watchtower.enable=true"
```

## Notificaciones

- Slack
- Email
- Gotify
- ntfy
- Y mas...

## Nota

Watchtower no tiene UI. Solo corre en background.

## Documentacion

- https://containrrr.dev/watchtower/
