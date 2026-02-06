# Chroma

Base de datos vectorial simple y facil de usar.

## Descripcion

Chroma es una vector DB diseñada para ser simple. Ideal para
prototipos y proyectos pequeños.

## Acceso

- **API**: http://chroma.127.0.0.1.traefik.me:9000

## Uso con Python

```python
import chromadb

client = chromadb.HttpClient(host="chroma", port=8000)

# Crear coleccion
collection = client.create_collection("documentos")

# Añadir documentos (embeddings automaticos)
collection.add(
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)

# Buscar
results = collection.query(
    query_texts=["busqueda"],
    n_results=5
)
```

## Con LangChain

```python
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    base_url="http://ollama:11434",
    model="llama3.2:1b"
)

vectorstore = Chroma(
    collection_name="docs",
    embedding_function=embeddings,
    client=chromadb.HttpClient(host="chroma", port=8000)
)
```

## Caracteristicas

- API simple
- Embeddings automaticos
- Persistencia
- Integracion LangChain

## Documentacion

- https://docs.trychroma.com/
