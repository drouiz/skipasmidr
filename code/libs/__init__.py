"""Shared Python libraries for data pipelines."""
import os


def get_db_connection_string(db_type: str = "postgres") -> str:
    """Get database connection string from environment."""
    if db_type == "postgres":
        user = os.getenv("POSTGRES_USER", "admin")
        password = os.getenv("POSTGRES_PASSWORD", "admin123")
        host = os.getenv("POSTGRES_HOST", "postgres-infra")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "postgres")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    if db_type == "mariadb":
        user = os.getenv("MYSQL_USER", "admin")
        password = os.getenv("MYSQL_PASSWORD", "admin123")
        host = os.getenv("MYSQL_HOST", "mariadb-infra")
        port = os.getenv("MYSQL_PORT", "3306")
        db = os.getenv("MYSQL_DATABASE", "mysql")
        return f"mysql://{user}:{password}@{host}:{port}/{db}"

    return ""
