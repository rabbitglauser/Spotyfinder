import pymysql
from fastapi import APIRouter, HTTPException
from pymysql.err import InterfaceError, MySQLError, OperationalError

from db import get_db_config

router = APIRouter()


@router.get("/api/items")
def get_items():
    try:
        with pymysql.connect(**get_db_config()) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        t.id,
                        t.spotify_track_id,
                        t.track_uri,
                        t.name,
                        t.duration_ms,
                        t.popularity,
                        t.explicit,
                        a.name AS album_name
                    FROM tracks AS t
                    LEFT JOIN albums AS a ON a.id = t.album_id
                    LIMIT 50
                    """
                )
                items = cursor.fetchall()

        return {"count": len(items), "items": items}

    except (OperationalError, InterfaceError):
        raise HTTPException(status_code=503, detail="Database is not reachable")
    except MySQLError:
        raise HTTPException(status_code=500, detail="Database query failed")