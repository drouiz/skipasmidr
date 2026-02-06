# Flowise

Constructor visual de aplicaciones LLM/RAG.

## Descripcion

Flowise permite construir pipelines de LangChain visualmente.
Ideal para crear chatbots RAG sin codigo.

## Acceso

- **URL**: http://flowise.127.0.0.1.traefik.me:9000

## Credenciales

```
Usuario: admin
Password: admin123
```

## Dependencias

- PostgreSQL

## Como crear un RAG

1. Arrastrar nodo "Document Loaders" (PDF, etc.)
2. Arrastrar "Text Splitter"
3. Arrastrar "Embeddings" (Ollama)
4. Arrastrar "Vector Store" (Qdrant/Chroma)
5. Arrastrar "Chat Model" (Ollama)
6. Arrastrar "Conversational Retrieval QA Chain"
7. Conectar todo
8. Guardar y probar

## Configurar Ollama

En el nodo "Chat Ollama":
- Base URL: http://ollama:11434
- Model: llama3.2:1b

## API

Cada chatflow tiene un endpoint:
```bash
curl -X POST http://flowise:3000/api/v1/prediction/{chatflowId} \
  -H "Content-Type: application/json" \
  -d '{"question": "Pregunta"}'
```

## Documentacion

- https://docs.flowiseai.com/
