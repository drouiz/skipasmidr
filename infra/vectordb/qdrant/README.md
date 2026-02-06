# Qdrant

Base de datos vectorial de alto rendimiento.

## Descripcion

Qdrant almacena y busca vectores (embeddings). Esencial para RAG y
busqueda semantica.

## Acceso

- **Dashboard**: http://qdrant.127.0.0.1.traefik.me:9000/dashboard
- **API**: http://qdrant.127.0.0.1.traefik.me:9000

## Uso con Python

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="qdrant", port=6333)

# Crear coleccion
client.create_collection(
    collection_name="documentos",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Insertar vectores
client.upsert(
    collection_name="documentos",
    points=[
        {"id": 1, "vector": [0.1, 0.2, ...], "payload": {"text": "..."}}
    ]
)

# Buscar similares
client.search(
    collection_name="documentos",
    query_vector=[0.1, 0.2, ...],
    limit=5
)
```

## Caracteristicas

- Alto rendimiento
- Filtros en metadata
- API REST y gRPC
- Dashboard web
- Escalable

## Documentacion

- https://qdrant.tech/documentation/
