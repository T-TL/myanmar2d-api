
import os
import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", "data/market.db")
)


def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True, exist_ok=True
    )

    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_index REAL,
                market_value REAL,
                two_d TEXT,
                market_status TEXT,
                source_time TEXT,
                fetched_at TEXT NOT NULL,
                is_live INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Myanmar 2D API",
    description="Independent Thai SET data API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {
        "name": "Myanmar 2D API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "database": "connected"
    }


@app.get("/api/v1/live")
def get_live():
    with get_connection() as conn:
        row = conn.execute("""
            SELECT * FROM market_data
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

    if row is None:
        return {
            "success": True,
            "data_available": False,
            "is_live": False,
            "message": "Waiting for SET data",
            "data": None
        }

    return {
        "success": True,
        "data_available": True,
        "is_live": bool(row["is_live"]),
        "data": dict(row)
    }


@app.get("/api/v1/history")
def get_history(
    limit: int = Query(default=50, ge=1, le=500)
):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM market_data
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return {
        "success": True,
        "count": len(rows),
        "data": [dict(row) for row in rows]
    }


@app.get("/api/v1/market/status")
def market_status():
    with get_connection() as conn:
        row = conn.execute("""
            SELECT market_status, fetched_at
            FROM market_data
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

    if row is None:
        return {
            "market_status": "UNKNOWN",
            "last_updated": None
        }

    return {
        "market_status": row["market_status"],
        "last_updated": row["fetched_at"]
    }
