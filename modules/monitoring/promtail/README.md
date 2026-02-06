# Promtail

Agente de recoleccion de logs para Loki.

## Descripcion

Promtail recolecta logs de contenedores Docker automaticamente y los envia a Loki.

## Requisitos

- Loki debe estar corriendo

## Funcionamiento

Promtail detecta automaticamente todos los contenedores Docker y envia sus logs a Loki
con las siguientes labels:

- `container`: Nombre del contenedor
- `container_id`: ID del contenedor
- `service`: Nombre del servicio (docker-compose)
- `project`: Nombre del proyecto (docker-compose)

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| PROMTAIL_VERSION | latest | Version |

## Configuracion

Editar `config.yml` para:
- Cambiar URL de Loki
- Añadir/modificar labels
- Filtrar contenedores
- Parsear logs

## Filtrar contenedores

```yaml
relabel_configs:
  # Solo contenedores con label especifica
  - source_labels: ['__meta_docker_container_label_logging']
    regex: 'true'
    action: keep
```

## Parsear logs JSON

```yaml
pipeline_stages:
  - json:
      expressions:
        level: level
        message: msg
  - labels:
      level:
```

## Ver en Grafana

1. Ir a Explore
2. Seleccionar Loki
3. Usar LogQL:
```logql
{container="mi-contenedor"}
{service="n8n"} |= "error"
```

## Documentacion

- https://grafana.com/docs/loki/latest/send-data/promtail/
