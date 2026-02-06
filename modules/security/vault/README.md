# HashiCorp Vault

Gestion de secretos empresarial.

## Descripcion

Vault gestiona secretos, tokens, passwords, certificados y
claves de encriptacion.

## Acceso

- **UI**: http://vault.127.0.0.1.traefik.me:9000

## Token (modo dev)

En modo desarrollo, el token es `root` (o VAULT_TOKEN).

## CLI

```bash
# Login
docker exec -it vault vault login root

# Escribir secreto
docker exec -it vault vault kv put secret/mi-app password=secreto

# Leer secreto
docker exec -it vault vault kv get secret/mi-app
```

## Caracteristicas

- Secrets engines (KV, databases, PKI, etc.)
- Dynamic secrets
- Encriptacion como servicio
- Leasing y revocacion
- Auditoria
- Politicas de acceso

## Nota

En produccion, NO usar modo dev. Configurar storage
backend (Consul, S3, etc.) y unseal keys.

## Documentacion

- https://developer.hashicorp.com/vault/docs
