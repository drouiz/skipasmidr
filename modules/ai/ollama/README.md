# Ollama

Servidor de modelos LLM local.

## Descripcion

Ollama permite ejecutar modelos de lenguaje localmente con una API compatible
con OpenAI. Es la base del stack de IA.

## Acceso

- **API**: http://ollama.127.0.0.1.traefik.me:9000
- **API directa**: http://localhost:11434

## Configuracion

Editar `.env` para configurar:

```env
# Modelo a descargar automaticamente
OLLAMA_MODEL=llama3.2:1b

# Para GPU NVIDIA
OLLAMA_GPU=true
```

## Modelos recomendados

| Modelo | Tamaño | Uso | RAM minima |
|--------|--------|-----|------------|
| llama3.2:1b | 1.3GB | Chat rapido | 4GB |
| llama3.2:3b | 2GB | Chat general | 6GB |
| llama3.1:8b | 4.7GB | Chat avanzado | 10GB |
| mistral:7b | 4.1GB | Chat, codigo | 10GB |
| codellama:7b | 3.8GB | Codigo | 10GB |
| phi3:mini | 2.3GB | Chat rapido | 5GB |

## CLI

```bash
# Listar modelos instalados
docker exec ollama ollama list

# Descargar modelo
docker exec ollama ollama pull mistral:7b

# Borrar modelo
docker exec ollama ollama rm llama3.2:1b

# Chat interactivo
docker exec -it ollama ollama run mistral
```

## API (compatible OpenAI)

```bash
# Chat
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [{"role": "user", "content": "Hola!"}]
  }'

# Embeddings
curl http://localhost:11434/api/embeddings \
  -d '{"model": "llama3.2:1b", "prompt": "texto a embedear"}'
```

## Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://ollama:11434/v1",
    api_key="ollama"  # no se usa pero es requerido
)

response = client.chat.completions.create(
    model="llama3.2:1b",
    messages=[{"role": "user", "content": "Hola!"}]
)
```

## GPU NVIDIA

1. Instalar nvidia-container-toolkit
2. Editar docker-compose.yml y descomentar deploy.resources
3. Configurar OLLAMA_GPU=true

## Volumenes

- `ollama-data`: Modelos descargados (~GB por modelo)

## Documentacion

- https://ollama.com/library
- https://github.com/ollama/ollama/blob/main/docs/api.md
