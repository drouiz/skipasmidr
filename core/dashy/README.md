# Dashy

Dashboard de aplicaciones altamente personalizable.

## Descripcion

Dashy es el dashboard central de la infraestructura. Muestra todos los servicios activos
agrupados por categoria. Se auto-genera basandose en los servicios levantados.

## Acceso

- **URL**: http://dashy.127.0.0.1.traefik.me:9000

## Auto-generacion

Cuando ejecutas `deploy.py up/add/down`, el script:

1. Lee los archivos `dashy.fragment.json` de cada modulo activo
2. Combina todos los fragmentos
3. Genera el archivo `conf.yml`
4. Dashy recarga la configuracion automaticamente

## Estructura de un fragment

Cada modulo tiene un `dashy.fragment.json`:

```json
{
  "name": "Mi Servicio",
  "icon": "fas fa-cube",
  "url": "http://mi-servicio.127.0.0.1.traefik.me:9000",
  "category": "MI-CATEGORIA",
  "tags": ["tag1", "tag2"]
}
```

## Categorias

- CORE: Servicios base (traefik, dashy, portainer)
- INFRA: Bases de datos, mensajeria, storage
- DATA: Herramientas de datos
- AUTOMATION: Automatizacion y workflows
- MONITORING: Monitorizacion y observabilidad
- SECURITY: Seguridad
- AUTH: Autenticacion
- SOCIAL: Redes sociales
- IOT: Internet of Things
- LOWCODE: Plataformas low-code
- DEVELOPER: Herramientas de desarrollo
- CORPORATIVO: ERP y herramientas corporativas

## Personalizacion

Edita `conf.yml` directamente para personalizaciones avanzadas:
- Temas: nord, dark, light, colorful, etc.
- Layouts: auto, horizontal, vertical
- Iconos: FontAwesome, Material Icons, emojis

## Documentacion

- https://dashy.to/docs/
