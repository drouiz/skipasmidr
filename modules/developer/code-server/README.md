# Code Server

VS Code en el navegador.

## Descripcion

Code Server permite ejecutar VS Code en un servidor remoto
y acceder via navegador.

## Acceso

- **URL**: http://code.127.0.0.1.traefik.me:9000
- **Password**: admin123

## Caracteristicas

- VS Code completo en el navegador
- Extensiones
- Terminal integrado
- Git integration

## Uso

1. Acceder a la URL
2. Introducir password
3. Usar como VS Code normal

## Montar proyectos

Modifica el docker-compose para montar tu directorio de proyectos:

```yaml
volumes:
  - /tu/directorio/proyectos:/home/coder/projects
```

## Documentacion

- https://coder.com/docs/code-server
