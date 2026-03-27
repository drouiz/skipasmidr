"""Minimal DuckDB REST API server."""
import duckdb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="DuckDB API")
conn = duckdb.connect("/data/duckdb.db")


class Query(BaseModel):
    sql: str


@app.get("/health")
def health():
    return {"status": "ok", "db": "/data/duckdb.db"}


@app.post("/query")
def query(q: Query):
    try:
        result = conn.execute(q.sql).fetchall()
        columns = [desc[0] for desc in conn.description] if conn.description else []
        return {"columns": columns, "rows": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tables")
def tables():
    result = conn.execute("SHOW TABLES").fetchall()
    return {"tables": [r[0] for r in result]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
