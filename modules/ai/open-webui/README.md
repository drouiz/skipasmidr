# Open WebUI

Frontend tipo ChatGPT para modelos locales.

## Descripcion

Open WebUI es una interfaz web moderna para interactuar con LLMs.
Similar a ChatGPT pero para modelos locales via Ollama.

## Acceso

- **URL**: http://chat.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Acceder a la URL
2. Crear cuenta de admin
3. Los modelos de Ollama aparecen automaticamente

## Dependencias

- Ollama (requerido)
- PostgreSQL (opcional, para persistencia)
- Chroma (opcional, para RAG)

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| OPENWEBUI_VERSION | main | Version |
| OPENWEBUI_DB | openwebui | Base de datos |
| OPENAI_API_KEY | - | Para usar OpenAI tambien |

## Caracteristicas

- Chat con multiples modelos
- Historial de conversaciones
- RAG (subir documentos)
- Prompts guardados
- Multi-usuario
- API compatible

## RAG (Documentos)

1. Click en "+" en el chat
2. Subir PDF, TXT, etc.
3. El documento se vectoriza automaticamente
4. Preguntar sobre el contenido

## Conectar con OpenAI

Añadir en .env:
```env
OPENAI_API_KEY=sk-...
```

Podras usar GPT-4 junto a modelos locales.

## Volumenes

- `openwebui-data`: Configuracion, uploads, historial

## Documentacion

- https://docs.openwebui.com/
