# Docker Registry + UI

Registry privado de imagenes Docker con interfaz web.

## Descripcion

Registry privado para almacenar imagenes Docker propias.
Esta es una version simplificada. Para Harbor completo, ver seccion al final.

## Acceso

- **UI**: http://registry.127.0.0.1.traefik.me:9000

## Uso

### Configurar Docker para registry inseguro

En Docker Desktop o `/etc/docker/daemon.json`:

```json
{
  "insecure-registries": ["registry.127.0.0.1.traefik.me:9000"]
}
```

Reiniciar Docker despues de cambiar.

### Push imagen

```bash
# Tag
docker tag mi-imagen:latest registry.127.0.0.1.traefik.me:9000/mi-imagen:latest

# Push
docker push registry.127.0.0.1.traefik.me:9000/mi-imagen:latest
```

### Pull imagen

```bash
docker pull registry.127.0.0.1.traefik.me:9000/mi-imagen:latest
```

### En docker-compose

```yaml
services:
  mi-app:
    image: registry.127.0.0.1.traefik.me:9000/mi-imagen:latest
```

## Volumenes

- `registry-data`: Imagenes almacenadas

## Harbor completo

Para instalar Harbor (con autenticacion, vulnerabilidad scanning, etc.):

```bash
# Descargar
wget https://github.com/goharbor/harbor/releases/download/v2.10.0/harbor-offline-installer-v2.10.0.tgz

# Extraer
tar xvf harbor-offline-installer-v2.10.0.tgz

# Configurar
cd harbor
cp harbor.yml.tmpl harbor.yml
# Editar harbor.yml

# Instalar
./install.sh
```

## Documentacion

- https://docs.docker.com/registry/
- https://goharbor.io/docs/
