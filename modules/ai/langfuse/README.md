# Langfuse

Observabilidad para aplicaciones LLM.

## Descripcion

Langfuse proporciona trazas, metricas y analytics para aplicaciones
que usan LLMs. Esencial para debugging y optimizacion.

## Acceso

- **URL**: http://langfuse.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Acceder a la URL
2. Crear cuenta
3. Crear proyecto
4. Obtener API keys

## Dependencias

- PostgreSQL

## Uso con Python

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-...",
    secret_key="sk-...",
    host="http://langfuse:3000"
)

# Trazar una generacion
trace = langfuse.trace(name="my-app")

generation = trace.generation(
    name="chat",
    model="llama3.2:1b",
    input={"messages": [...]},
    output="respuesta"
)
```

## Con LangChain

```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler(
    public_key="pk-...",
    secret_key="sk-...",
    host="http://langfuse:3000"
)

# Usar en chains
chain.invoke(input, config={"callbacks": [handler]})
```

## Metricas

- Latencia
- Tokens usados
- Costes
- Scores de calidad
- Trazas completas

## Documentacion

- https://langfuse.com/docs
