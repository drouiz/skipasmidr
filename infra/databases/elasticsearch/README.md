# Elasticsearch + Kibana

Motor de busqueda y analisis con interfaz de visualizacion.

## Descripcion

Elasticsearch es un motor de busqueda distribuido. Kibana proporciona
visualizacion y exploracion de datos.

## Acceso

- **Kibana URL**: http://kibana.127.0.0.1.traefik.me:9000
- **Elasticsearch**: localhost:9200 (si EXPOSE_ELASTIC_PORT esta habilitado)

## Configuracion

Por defecto, la seguridad esta deshabilitada para desarrollo.

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| ELASTIC_VERSION | 8.12.0 | Version de Elastic Stack |
| EXPOSE_ELASTIC_PORT | 127.0.0.1:9200 | Puerto expuesto |

## Conexion desde otros servicios

```yaml
environment:
  ELASTICSEARCH_URL: http://elasticsearch:9200
```

## Casos de uso

- Busqueda full-text
- Logs centralizados (ELK stack)
- Metricas y analisis
- APM (Application Performance Monitoring)
- SIEM (Security Information)

## API basica

```bash
# Estado del cluster
curl http://localhost:9200/_cluster/health

# Crear indice
curl -X PUT http://localhost:9200/mi-indice

# Indexar documento
curl -X POST http://localhost:9200/mi-indice/_doc -H 'Content-Type: application/json' -d '{"campo": "valor"}'

# Buscar
curl http://localhost:9200/mi-indice/_search?q=campo:valor
```

## Memoria

Por defecto usa 512MB de heap. Ajustar ES_JAVA_OPTS para cambiar:
```yaml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
```

## Volumenes

- `elasticsearch-data`: Datos e indices

## Documentacion

- https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- https://www.elastic.co/guide/en/kibana/current/index.html
