# Neo4j

Base de datos de grafos con interfaz web integrada.

## Descripcion

Neo4j es una base de datos de grafos nativa. Ideal para modelar relaciones
complejas entre entidades.

## Acceso

- **Neo4j Browser URL**: http://neo4j.127.0.0.1.traefik.me:9000
- **Bolt Protocol**: localhost:7687 (si EXPOSE_NEO4J_BOLT esta habilitado)

## Credenciales por defecto

```
Neo4j:
  - Usuario: neo4j
  - Password: admin123
```

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| NEO4J_VERSION | 5 | Version de Neo4j |
| NEO4J_USER | neo4j | Usuario |
| NEO4J_PASSWORD | admin123 | Password |
| EXPOSE_NEO4J_BOLT | 127.0.0.1:7687 | Puerto Bolt |

## Conexion desde otros servicios

```yaml
environment:
  NEO4J_URI: bolt://neo4j:7687
  NEO4J_USER: neo4j
  NEO4J_PASSWORD: admin123
```

## Plugins incluidos

- **APOC**: Procedimientos y funciones adicionales
- **Graph Data Science**: Algoritmos de machine learning

## Casos de uso

- Redes sociales
- Deteccion de fraude
- Motores de recomendacion
- Knowledge graphs
- Gestion de identidades

## Cypher basico

```cypher
// Crear nodo
CREATE (p:Person {name: 'Alice'})

// Crear relacion
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
CREATE (a)-[:KNOWS]->(b)

// Consultar
MATCH (p:Person)-[:KNOWS]->(friend)
RETURN p.name, friend.name
```

## Volumenes

- `neo4j-data`: Datos de la base de datos
- `neo4j-logs`: Logs

## Documentacion

- https://neo4j.com/docs/
