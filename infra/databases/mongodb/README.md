# MongoDB + Mongo Express

Base de datos NoSQL orientada a documentos con interfaz web.

## Descripcion

MongoDB es una base de datos NoSQL que almacena datos en documentos JSON flexibles.
Ideal para aplicaciones con esquemas dinamicos.

## Acceso

- **Mongo Express URL**: http://mongo.127.0.0.1.traefik.me:9000
- **MongoDB**: localhost:27017 (si EXPOSE_MONGO_PORT esta habilitado)

## Credenciales por defecto

```
MongoDB:
  - Usuario: admin
  - Password: admin123

Mongo Express:
  - Sin autenticacion basica (desarrollo)
```

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| MONGO_VERSION | 7 | Version de MongoDB |
| MONGO_USER | admin | Usuario administrador |
| MONGO_PASSWORD | admin123 | Password |
| EXPOSE_MONGO_PORT | 127.0.0.1:27017 | Puerto expuesto |

## Conexion desde otros servicios

```yaml
environment:
  MONGODB_URL: mongodb://admin:admin123@mongodb:27017/mi_db?authSource=admin
```

## Volumenes

- `mongodb-data`: Datos de MongoDB

## Backups

```bash
# Backup
docker exec mongodb mongodump --out /dump
docker cp mongodb:/dump ./backup

# Restore
docker cp ./backup mongodb:/dump
docker exec mongodb mongorestore /dump
```

## Documentacion

- https://www.mongodb.com/docs/
- https://github.com/mongo-express/mongo-express
