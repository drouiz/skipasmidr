# Nexus Repository Manager

Gestor de repositorios de artefactos.

## Descripcion

Nexus Repository Manager permite alojar y gestionar artefactos de multiples
formatos: Maven, npm, PyPI, Docker, NuGet, etc.

## Acceso

- **UI**: http://nexus.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Obtener password inicial:
```bash
docker exec nexus cat /nexus-data/admin.password
```

2. Acceder con usuario `admin` y el password obtenido
3. Cambiar password y completar wizard

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| NEXUS_VERSION | latest | Version de Nexus |

## Tipos de repositorio

### Hosted
Almacenar artefactos propios.

### Proxy
Cache de repositorios externos (Maven Central, npmjs, PyPI).

### Group
Combinar multiples repositorios en uno.

## Formatos soportados

- Maven/Gradle (Java)
- npm (JavaScript)
- PyPI (Python)
- NuGet (.NET)
- Docker
- Helm
- Raw (archivos genericos)
- apt/yum (Linux packages)

## Configurar npm

```bash
npm config set registry http://nexus.127.0.0.1.traefik.me:9000/repository/npm-group/
```

## Configurar uv/pip

```bash
# Con uv
uv pip install --index-url http://nexus.127.0.0.1.traefik.me:9000/repository/pypi-group/simple/ paquete

# Con pip
pip install --index-url http://nexus.127.0.0.1.traefik.me:9000/repository/pypi-group/simple/ paquete
```

## Volumenes

- `nexus-data`: Datos y configuracion

## Recursos

Nexus requiere al menos 4GB de RAM para funcionar correctamente.

## Documentacion

- https://help.sonatype.com/repomanager3
