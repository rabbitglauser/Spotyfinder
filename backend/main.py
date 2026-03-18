import os

import pymysql
from fastapi import FastAPI, HTTPException
from pymysql.cursors import DictCursor
from pymysql.err import InterfaceError, MySQLError, OperationalError

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "spotyfinderdb"),
        "cursorclass": DictCursor,
        "autocommit": True,
    }


@app.get("/api/items")
def get_items():
    try:
        with pymysql.connect(**get_db_config()) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT
                                   t.id,
                                   t.track_uri,
                                   t.duration_ms,
                                   t.popularity,
                                   t.explicit,
                                   a.name AS album_name
                               FROM tracks AS t
                                        LEFT JOIN albums AS a ON a.id = t.album_id
                                   LIMIT 50
                               """)
                items = cursor.fetchall()

        return {"count": len(items), "items": items}

    except (OperationalError, InterfaceError):
        raise HTTPException(status_code=503, detail="Database is not reachable")
    except MySQLError:
        raise HTTPException(status_code=500, detail="Database query failed")