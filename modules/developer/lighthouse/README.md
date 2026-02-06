# Google Lighthouse

Auditorias de rendimiento, accesibilidad y SEO.

## Descripcion

Google Lighthouse analiza paginas web y genera informes
sobre rendimiento, accesibilidad, SEO y mejores practicas.

## Acceso

- **Lighthouse CI**: http://lhci.127.0.0.1.traefik.me:9000

## Componentes

1. **lighthouse** - Ejecutor de auditorias
2. **lhci-server** - Dashboard para Lighthouse CI

## Uso CLI

```bash
# Ejecutar auditoria
docker exec lighthouse lighthouse https://example.com --output=json

# Con Chrome headless
docker exec lighthouse lighthouse https://example.com \
  --chrome-flags="--headless" \
  --output=html \
  --output-path=/home/user/reports/report.html
```

## Lighthouse CI

Lighthouse CI permite:
- Tracking historico de metricas
- Integracion con CI/CD
- Comparacion entre builds
- Alertas de regresion

## Uso en CI/CD

```bash
# Instalar CLI
npm install -g @lhci/cli

# Ejecutar y subir
lhci autorun --upload.serverBaseUrl=http://lhci.127.0.0.1.traefik.me:9000
```

## Documentacion

- https://developer.chrome.com/docs/lighthouse/
- https://github.com/GoogleChrome/lighthouse-ci
