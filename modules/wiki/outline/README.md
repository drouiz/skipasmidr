# Outline

Wiki moderno para equipos.

## Descripcion

Outline es un wiki/knowledge base moderno, rapido y bonito
para equipos, similar a Notion o Confluence.

## Acceso

- **URL**: http://outline.127.0.0.1.traefik.me:9000

## Dependencias

- PostgreSQL
- Redis
- Keycloak (para autenticacion OIDC)

## Caracteristicas

- Editor WYSIWYG moderno
- Markdown
- Busqueda full-text
- Colaboracion en tiempo real
- Integraciones (Slack, etc.)
- API

## Configuracion

Outline requiere autenticacion OIDC. Opciones:
1. Keycloak (incluido en este stack)
2. Google OAuth
3. Slack OAuth
4. SAML

## Configurar con Keycloak

1. En Keycloak, crear cliente "outline"
2. Configurar redirect URI
3. Actualizar variables de entorno

## Documentacion

- https://docs.getoutline.com/
