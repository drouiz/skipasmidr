# MariaDB + phpMyAdmin

Base de datos MySQL/MariaDB con interfaz de administracion phpMyAdmin.

## Descripcion

MariaDB es un fork de MySQL, compatible al 100%. Util para aplicaciones que
requieren MySQL especificamente.

## Acceso

- **phpMyAdmin URL**: http://phpmyadmin.127.0.0.1.traefik.me:9000
- **MariaDB**: localhost:3306 (si EXPOSE_MYSQL_PORT esta habilitado)

## Credenciales por defecto

```
MariaDB:
  - Root Password: admin123
  - Usuario: admin
  - Password: admin123
  - Database: default

phpMyAdmin:
  - Conecta automaticamente como root
```

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| MARIADB_VERSION | 11 | Version de MariaDB |
| MYSQL_ROOT_PASSWORD | admin123 | Password de root |
| MYSQL_USER | admin | Usuario adicional |
| MYSQL_PASSWORD | admin123 | Password del usuario |
| MYSQL_DATABASE | default | Base de datos inicial |
| EXPOSE_MYSQL_PORT | 127.0.0.1:3306 | Puerto expuesto |

## Conexion desde otros servicios

```yaml
environment:
  DATABASE_URL: mysql://admin:admin123@mariadb:3306/mi_db
```

## Volumenes

- `mariadb-data`: Datos de MariaDB

## Backups

```bash
# Backup
docker exec mariadb mysqldump -u root -p mi_db > backup.sql

# Restore
docker exec -i mariadb mysql -u root -p mi_db < backup.sql
```

## Documentacion

- https://mariadb.org/documentation/
- https://www.phpmyadmin.net/docs/
