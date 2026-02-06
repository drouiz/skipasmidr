# Backstage

Developer portal de Spotify.

## Descripcion

Backstage es una plataforma para construir portales de desarrolladores.
Catalogo de servicios, docs y plugins.

## Acceso

- **URL**: http://backstage.127.0.0.1.traefik.me:9000

## Dependencias

- PostgreSQL (opcional pero recomendado)

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| BACKSTAGE_VERSION | latest | Version |

## Caracteristicas

- Software Catalog
- TechDocs (documentacion)
- Templates (scaffolding)
- Search
- Kubernetes plugin
- CI/CD plugins
- Y 100+ plugins

## Software Catalog

Definir servicios en YAML:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: mi-servicio
  description: Mi microservicio
spec:
  type: service
  lifecycle: production
  owner: team-backend
```

## TechDocs

Documentacion como codigo usando MkDocs.

## Templates

Crear nuevos proyectos con templates predefinidos.

## Nota

Backstage requiere configuracion adicional.
La imagen Docker es solo un punto de partida.
Para uso real, crear imagen custom.

## Documentacion

- https://backstage.io/docs/
