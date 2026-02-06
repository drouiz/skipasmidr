# Keycloak

Gestion de identidades y acceso.

## Descripcion

Keycloak proporciona SSO, OAuth2, OIDC, SAML y gestion de usuarios.

## Acceso

- **URL**: http://keycloak.127.0.0.1.traefik.me:9000
- **Admin Console**: http://keycloak.127.0.0.1.traefik.me:9000/admin

## Credenciales por defecto

```
Admin:
  - Usuario: admin
  - Password: admin123
```

## Dependencias

- PostgreSQL

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| KEYCLOAK_VERSION | latest | Version |
| KEYCLOAK_DB | keycloak | Base de datos |
| KEYCLOAK_USER | admin | Usuario admin |
| KEYCLOAK_PASSWORD | admin123 | Password |

## Crear base de datos

```sql
CREATE DATABASE keycloak;
```

## Caracteristicas

- Single Sign-On (SSO)
- OAuth 2.0 / OpenID Connect
- SAML 2.0
- LDAP / Active Directory
- Social login (Google, GitHub, etc.)
- Multi-factor authentication
- User federation

## Integrar aplicacion

1. Crear Realm
2. Crear Client
3. Configurar redirect URIs
4. Usar client_id y secret

## Ejemplo integracion

```python
# Flask + Keycloak
from flask_oidc import OpenIDConnect

app.config['OIDC_CLIENT_SECRETS'] = 'client_secrets.json'
oidc = OpenIDConnect(app)

@app.route('/protected')
@oidc.require_login
def protected():
    return 'Hello, ' + oidc.user_getfield('email')
```

## Documentacion

- https://www.keycloak.org/documentation
