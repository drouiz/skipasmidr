# Fail2Ban

Proteccion contra ataques de fuerza bruta.

## Descripcion

Fail2Ban analiza logs y banea IPs con comportamiento sospechoso
usando iptables.

## Nota

Fail2Ban no tiene interfaz web. Usa CLI para gestion.

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| FAIL2BAN_VERSION | latest | Version |

## CLI

```bash
# Ver jails activos
docker exec fail2ban fail2ban-client status

# Ver IPs baneadas
docker exec fail2ban fail2ban-client status sshd

# Banear IP manualmente
docker exec fail2ban fail2ban-client set sshd banip 1.2.3.4

# Desbanear IP
docker exec fail2ban fail2ban-client set sshd unbanip 1.2.3.4
```

## Configuracion

Crear archivos en `/data/jail.d/`:

```ini
[traefik-auth]
enabled = true
filter = traefik-auth
logpath = /var/log/traefik/access.log
maxretry = 5
bantime = 3600
```

## Jails comunes

- sshd
- traefik-auth
- nginx-http-auth
- apache-auth

## Volumenes

- `fail2ban-data`: Configuracion, base de datos de bans

## Documentacion

- https://www.fail2ban.org/wiki/index.php/Main_Page
