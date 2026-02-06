-- Script para crear las bases de datos de los servicios
-- Se ejecuta automaticamente al iniciar PostgreSQL por primera vez

-- Bases de datos para servicios
CREATE DATABASE IF NOT EXISTS odoo;
CREATE DATABASE IF NOT EXISTS n8n;
CREATE DATABASE IF NOT EXISTS keycloak;
CREATE DATABASE IF NOT EXISTS airflow;
CREATE DATABASE IF NOT EXISTS dagster;
CREATE DATABASE IF NOT EXISTS superset;
CREATE DATABASE IF NOT EXISTS nocodb;
CREATE DATABASE IF NOT EXISTS prefect;
CREATE DATABASE IF NOT EXISTS windmill;
CREATE DATABASE IF NOT EXISTS mastodon;
CREATE DATABASE IF NOT EXISTS mixpost;
CREATE DATABASE IF NOT EXISTS postiz;
CREATE DATABASE IF NOT EXISTS hoppscotch;

-- Nota: Este script se ejecuta solo la primera vez
-- Para crear bases de datos adicionales, usar pgAdmin o psql
