# Tempo

Sistema de trazas distribuidas.

## Descripcion

Grafana Tempo almacena y consulta trazas. Soporta multiples protocolos:
OTLP, Jaeger, Zipkin.

## Acceso

- **API**: http://tempo.127.0.0.1.traefik.me:9000

## Puertos de ingesta

| Puerto | Protocolo |
|--------|-----------|
| 4317 | OTLP gRPC |
| 4318 | OTLP HTTP |
| 14268 | Jaeger HTTP |
| 14250 | Jaeger gRPC |
| 9411 | Zipkin |

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| TEMPO_VERSION | latest | Version |

## Enviar trazas

### Python (OpenTelemetry)
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://tempo:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("mi-operacion"):
    # codigo...
    pass
```

## Visualizar en Grafana

1. Añadir Tempo como data source (http://tempo:3200)
2. Ir a Explore
3. Seleccionar Tempo
4. Buscar por TraceID o usar TraceQL

## TraceQL

```
{ span.http.status_code = 500 }
{ resource.service.name = "mi-app" && duration > 100ms }
```

## Volumenes

- `tempo-data`: Trazas almacenadas

## Documentacion

- https://grafana.com/docs/tempo/latest/
