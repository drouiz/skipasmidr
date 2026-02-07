#!/bin/bash
set -e

# Auto-create databases for services that need PostgreSQL
# This script runs on first PostgreSQL initialization

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create databases if they don't exist
    SELECT 'CREATE DATABASE n8n' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'n8n')\gexec
    SELECT 'CREATE DATABASE odoo' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'odoo')\gexec
    SELECT 'CREATE DATABASE keycloak' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'keycloak')\gexec
    SELECT 'CREATE DATABASE airflow' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec
    SELECT 'CREATE DATABASE dagster' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dagster')\gexec
    SELECT 'CREATE DATABASE superset' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'superset')\gexec
    SELECT 'CREATE DATABASE nocodb' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nocodb')\gexec
    SELECT 'CREATE DATABASE prefect' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'prefect')\gexec
    SELECT 'CREATE DATABASE windmill' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'windmill')\gexec
EOSQL

echo "All databases created successfully!"
