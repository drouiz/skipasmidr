# Paperless-ngx

Sistema de gestion documental con OCR.

## Descripcion

Paperless-ngx escanea, indexa y archiva documentos fisicos
digitalizados, con OCR automatico y busqueda full-text.

## Acceso

- **URL**: http://paperless.127.0.0.1.traefik.me:9000
- **Usuario**: admin
- **Password**: admin123

## Dependencias

- PostgreSQL
- Redis

## Caracteristicas

- OCR automatico (Tesseract)
- Busqueda full-text
- Etiquetas y correspondientes
- Fechas automaticas
- Consumo automatico de archivos
- API REST

## Uso

1. Acceder a la URL
2. Subir documentos manualmente o via carpeta consume
3. Paperless procesa y extrae texto
4. Buscar y organizar documentos

## Carpeta consume

Los archivos en la carpeta `consume` se procesan automaticamente.

## Documentacion

- https://docs.paperless-ngx.com/
