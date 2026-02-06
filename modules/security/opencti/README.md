# OpenCTI

Plataforma de Cyber Threat Intelligence.

## Descripcion

OpenCTI es una plataforma para organizar, almacenar y visualizar
inteligencia de ciberamenazas.

## Acceso

- **URL**: http://opencti.127.0.0.1.traefik.me:9000

## Credenciales por defecto

```
Admin:
  - Email: admin@opencti.io
  - Password: admin123
```

## Dependencias

- Elasticsearch
- Redis
- MinIO

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| OPENCTI_VERSION | latest | Version |
| OPENCTI_ADMIN_EMAIL | admin@opencti.io | Email admin |
| OPENCTI_ADMIN_PASSWORD | admin123 | Password |

## Caracteristicas

- Modelado STIX2
- Integracion con feeds de amenazas
- Grafos de relaciones
- Playbooks
- Dashboards
- API GraphQL

## Conectores

Instalar conectores para importar datos:
- MITRE ATT&CK
- AlienVault OTX
- AbuseIPDB
- VirusTotal
- Y muchos mas...

## Requisitos

OpenCTI requiere bastante memoria (8GB+ recomendado).

## Documentacion

- https://docs.opencti.io/
