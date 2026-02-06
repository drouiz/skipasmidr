# Odoo

Suite de aplicaciones empresariales.

## Descripcion

Odoo es un ERP/CRM completo con modulos de ventas, compras, inventario,
contabilidad, RRHH, proyectos, etc.

## Acceso

- **URL**: http://odoo.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Acceder a la URL
2. Crear base de datos
3. Configurar email y password admin
4. Seleccionar apps a instalar

## Dependencias

- PostgreSQL

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| ODOO_VERSION | 17.0 | Version (17.0, 16.0, etc.) |

## Modulos incluidos

- CRM
- Ventas
- Compras
- Inventario
- Contabilidad
- Proyectos
- RRHH
- Website
- eCommerce
- Y muchos mas...

## Addons personalizados

Montar en `/mnt/extra-addons`:

```yaml
volumes:
  - ./my-addons:/mnt/extra-addons
```

## Desarrollo

```bash
# Scaffold nuevo modulo
docker exec odoo odoo scaffold my_module /mnt/extra-addons
```

## Base de datos

Odoo crea su propia base de datos durante el setup inicial.

## Volumenes

- `odoo-data`: Filestore, sesiones
- `odoo-addons`: Modulos personalizados

## Documentacion

- https://www.odoo.com/documentation/17.0/
