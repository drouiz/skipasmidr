# Gatus

Monitor de salud y status page.

## Descripcion

Gatus monitoriza endpoints HTTP, TCP, DNS, ICMP y muestra una pagina de estado.

## Acceso

- **URL**: http://gatus.127.0.0.1.traefik.me:9000

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| GATUS_VERSION | latest | Version |

## Configuracion

Editar `config.yaml` para añadir endpoints:

```yaml
endpoints:
  - name: Mi API
    group: Aplicaciones
    url: "http://mi-api:8080/health"
    interval: 30s
    conditions:
      - "[STATUS] == 200"
      - "[RESPONSE_TIME] < 500"

  - name: Base de datos
    group: Databases
    url: "tcp://postgres:5432"
    interval: 60s
    conditions:
      - "[CONNECTED] == true"
```

## Tipos de checks

### HTTP
```yaml
url: "http://servicio:8080/health"
conditions:
  - "[STATUS] == 200"
  - "[BODY].status == UP"
  - "[RESPONSE_TIME] < 1000"
```

### TCP
```yaml
url: "tcp://servicio:5432"
conditions:
  - "[CONNECTED] == true"
```

### DNS
```yaml
url: "dns://example.com"
dns:
  query-type: A
conditions:
  - "[DNS_RCODE] == NOERROR"
```

## Alertas

```yaml
alerting:
  slack:
    webhook-url: "https://hooks.slack.com/..."
    default-alert:
      enabled: true
      failure-threshold: 3
      success-threshold: 2
```

## Documentacion

- https://github.com/TwiN/gatus
