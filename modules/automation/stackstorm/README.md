# StackStorm

Plataforma de automatizacion event-driven.

## Descripcion

StackStorm (ST2) es una plataforma de automatizacion que conecta servicios
mediante reglas, workflows y acciones.

## Acceso

- **URL**: http://stackstorm.127.0.0.1.traefik.me:9000

## Credenciales por defecto

```
StackStorm:
  - Usuario: st2admin
  - Password: admin123
```

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| STACKSTORM_VERSION | latest | Version |
| ST2_USER | st2admin | Usuario |
| ST2_PASSWORD | admin123 | Password |

## Componentes

- **Sensors**: Detectan eventos externos
- **Rules**: Mapean eventos a acciones
- **Actions**: Tareas ejecutables
- **Workflows**: Secuencias de acciones

## Conceptos

### Pack
Paquete con sensores, reglas y acciones.

### Trigger
Evento que dispara una regla.

### Action
Tarea a ejecutar (script, API call, etc.)

## CLI

```bash
# Login
docker exec -it stackstorm st2 login -u st2admin -p admin123

# Listar packs
docker exec -it stackstorm st2 pack list

# Instalar pack
docker exec -it stackstorm st2 pack install github

# Ejecutar accion
docker exec -it stackstorm st2 run core.local -- hostname
```

## Casos de uso

- Remediation automatica
- ChatOps
- Integracion CI/CD
- Gestion de incidentes
- Runbooks automatizados

## Exchange

Explorar packs en: https://exchange.stackstorm.org/

## Volumenes

- `stackstorm-data`: Packs, configuracion, logs

## Documentacion

- https://docs.stackstorm.com/
