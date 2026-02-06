# Mailu

Stack de email simple y seguro.

## Descripcion

Mailu es un servidor de email completo: SMTP, IMAP, webmail,
antispam, antivirus, etc.

## Nota importante

Esta es una configuracion simplificada para desarrollo.
Para produccion, usar el setup oficial de Mailu:
https://setup.mailu.io/

## Acceso

- **Webmail**: http://mail.127.0.0.1.traefik.me:9000

## Componentes

- Postfix (SMTP)
- Dovecot (IMAP)
- Roundcube (Webmail)
- Rspamd (Antispam)
- ClamAV (Antivirus)

## Para desarrollo de email

Considera alternativas mas simples:
- **Mailhog**: Captura todos los emails (no envia)
- **Mailpit**: Similar a Mailhog, mas moderno

## Documentacion

- https://mailu.io/
