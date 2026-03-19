import base64
import csv
import os
import tempfile
import time
from pathlib import Path

import pymysql
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pymysql.cursors import DictCursor
from pymysql.err import InterfaceError, MySQLError, OperationalError

load_dotenv()

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
        "autocommit": False,
    }


@app.get("/api/items")
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


# =========================================================
# SPOTIFY HELPERS START
# =========================================================

_spotify_token_cache = {
    "access_token": None,
    "expires_at": 0,
}


def get_spotify_client_id():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="SPOTIFY_CLIENT_ID is missing in backend/.env")
    return client_id


def get_spotify_client_secret():
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_secret:
        raise HTTPException(status_code=500, detail="SPOTIFY_CLIENT_SECRET is missing in backend/.env")
    return client_secret


def get_spotify_access_token():
    now = time.time()

    if (
        _spotify_token_cache["access_token"]
        and now < _spotify_token_cache["expires_at"]
    ):
        return _spotify_token_cache["access_token"]

    client_id = get_spotify_client_id()
    client_secret = get_spotify_client_secret()

    raw = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = "Basic " + base64.b64encode(raw).decode("utf-8")

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=20,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Spotify token request failed: {response.text}",
        )

    payload = response.json()
    access_token = payload["access_token"]
    expires_in = int(payload.get("expires_in", 3600))

    _spotify_token_cache["access_token"] = access_token
    _spotify_token_cache["expires_at"] = now + max(expires_in - 60, 1)

    return access_token


def extract_track_id(track_uri: str | None):
    if not track_uri:
        return None

    track_uri = track_uri.strip()

    if track_uri.startswith("spotify:track:"):
        return track_uri.split(":")[-1]

    if "open.spotify.com/track/" in track_uri:
        return track_uri.rstrip("/").split("/")[-1].split("?")[0]

    return track_uri


def get_spotify_track(spotify_track_id: str, market: str = "CH"):
    token = get_spotify_access_token()

    response = requests.get(
        f"https://api.spotify.com/v1/tracks/{spotify_track_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"market": market},
        timeout=20,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Spotify track request failed: {response.text}",
        )

    return response.json()


def get_spotify_artist(spotify_artist_id: str):
    token = get_spotify_access_token()

    response = requests.get(
        f"https://api.spotify.com/v1/artists/{spotify_artist_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )

    if response.status_code != 200:
        return None

    return response.json()


def get_first_image_url(images):
    if not images:
        return None
    return images[0].get("url")


@app.get("/api/spotify/token-test")
def spotify_token_test():
    token = get_spotify_access_token()
    return {"status": "ok", "token_preview": token[:12] + "..."}


@app.get("/api/spotify/tracks/{spotify_track_id}")
def spotify_track_by_id(spotify_track_id: str):
    return get_spotify_track(spotify_track_id)


# =========================================================
# SPOTIFY HELPERS END
# =========================================================


# =========================================================
# CSV IMPORT HELPERS START
# =========================================================

def clean_text(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == "-":
        return None
    return text


def parse_bool(value):
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y"}


def parse_int(value):
    if value in (None, "", "-"):
        return None
    return int(float(value))


def parse_float(value):
    if value in (None, "", "-"):
        return None
    return float(value)


def parse_date(value):
    return clean_text(value)


def parse_timestamp(value):
    text = clean_text(value)
    if not text:
        return None
    return text.replace("Z", "+00:00")


def split_artists(value):
    text = clean_text(value)
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def split_genres(value):
    text = clean_text(value)
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def fetch_one_id(cursor, query, params):
    cursor.execute(query, params)
    row = cursor.fetchone()
    if not row:
        return None
    return int(row["id"])


def ensure_playlist(cursor, playlist_name):
    existing_id = fetch_one_id(
        cursor,
        "SELECT id FROM playlists WHERE name = %s LIMIT 1",
        (playlist_name,),
    )
    if existing_id:
        return existing_id

    cursor.execute(
        "INSERT INTO playlists (spotify_playlist_id, name) VALUES (%s, %s)",
        (None, playlist_name),
    )
    return int(cursor.lastrowid)


def ensure_record_label(cursor, label_name):
    if not label_name:
        return None

    existing_id = fetch_one_id(
        cursor,
        "SELECT id FROM record_labels WHERE name = %s LIMIT 1",
        (label_name,),
    )
    if existing_id:
        return existing_id

    cursor.execute(
        "INSERT INTO record_labels (name) VALUES (%s)",
        (label_name,),
    )
    return int(cursor.lastrowid)


def ensure_album(cursor, spotify_album_id, album_name, release_date, label_id, image_url):
    if not album_name and not spotify_album_id:
        return None

    if spotify_album_id:
        existing_id = fetch_one_id(
            cursor,
            "SELECT id FROM albums WHERE spotify_album_id = %s LIMIT 1",
            (spotify_album_id,),
        )
        if existing_id:
            cursor.execute(
                """
                UPDATE albums
                SET name = COALESCE(%s, name),
                    release_date = COALESCE(%s, release_date),
                    label_id = COALESCE(%s, label_id),
                    image_url = COALESCE(%s, image_url)
                WHERE id = %s
                """,
                (album_name, release_date, label_id, image_url, existing_id),
            )
            return existing_id

    existing_id = fetch_one_id(
        cursor,
        "SELECT id FROM albums WHERE name = %s AND release_date <=> %s LIMIT 1",
        (album_name, release_date),
    )
    if existing_id:
        cursor.execute(
            """
            UPDATE albums
            SET spotify_album_id = COALESCE(%s, spotify_album_id),
                label_id = COALESCE(%s, label_id),
                image_url = COALESCE(%s, image_url)
            WHERE id = %s
            """,
            (spotify_album_id, label_id, image_url, existing_id),
        )
        return existing_id

    cursor.execute(
        """
        INSERT INTO albums (
            spotify_album_id,
            name,
            release_date,
            label_id,
            image_url
        ) VALUES (%s, %s, %s, %s, %s)
        """,
        (spotify_album_id, album_name, release_date, label_id, image_url),
    )
    return int(cursor.lastrowid)


def ensure_track(
    cursor,
    spotify_track_id,
    track_uri,
    name,
    album_id,
    duration_ms,
    popularity,
    explicit,
    spotify_url,
    preview_url,
    cover_image_url,
):
    existing_id = None

    if spotify_track_id:
        existing_id = fetch_one_id(
            cursor,
            "SELECT id FROM tracks WHERE spotify_track_id = %s LIMIT 1",
            (spotify_track_id,),
        )

    if not existing_id and track_uri:
        existing_id = fetch_one_id(
            cursor,
            "SELECT id FROM tracks WHERE track_uri = %s LIMIT 1",
            (track_uri,),
        )

    if existing_id:
        cursor.execute(
            """
            UPDATE tracks
            SET spotify_track_id = COALESCE(%s, spotify_track_id),
                track_uri = COALESCE(%s, track_uri),
                name = COALESCE(%s, name),
                album_id = COALESCE(%s, album_id),
                duration_ms = COALESCE(%s, duration_ms),
                popularity = COALESCE(%s, popularity),
                explicit = %s,
                spotify_url = COALESCE(%s, spotify_url),
                preview_url = COALESCE(%s, preview_url),
                cover_image_url = COALESCE(%s, cover_image_url)
            WHERE id = %s
            """,
            (
                spotify_track_id,
                track_uri,
                name,
                album_id,
                duration_ms,
                popularity,
                explicit,
                spotify_url,
                preview_url,
                cover_image_url,
                existing_id,
            ),
        )
        return existing_id

    cursor.execute(
        """
        INSERT INTO tracks (
            spotify_track_id,
            track_uri,
            name,
            album_id,
            duration_ms,
            popularity,
            explicit,
            spotify_url,
            preview_url,
            cover_image_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            spotify_track_id,
            track_uri,
            name,
            album_id,
            duration_ms,
            popularity,
            explicit,
            spotify_url,
            preview_url,
            cover_image_url,
        ),
    )
    return int(cursor.lastrowid)


def upsert_audio_features(cursor, track_id, row):
    cursor.execute(
        """
        INSERT INTO audio_features (
            track_id,
            danceability,
            energy,
            `key`,
            loudness,
            mode,
            speechiness,
            acousticness,
            instrumentalness,
            liveness,
            valence,
            tempo,
            time_signature
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            danceability = VALUES(danceability),
            energy = VALUES(energy),
            `key` = VALUES(`key`),
            loudness = VALUES(loudness),
            mode = VALUES(mode),
            speechiness = VALUES(speechiness),
            acousticness = VALUES(acousticness),
            instrumentalness = VALUES(instrumentalness),
            liveness = VALUES(liveness),
            valence = VALUES(valence),
            tempo = VALUES(tempo),
            time_signature = VALUES(time_signature)
        """,
        (
            track_id,
            parse_float(row.get("Danceability")),
            parse_float(row.get("Energy")),
            parse_int(row.get("Key")),
            parse_float(row.get("Loudness")),
            parse_int(row.get("Mode")),
            parse_float(row.get("Speechiness")),
            parse_float(row.get("Acousticness")),
            parse_float(row.get("Instrumentalness")),
            parse_float(row.get("Liveness")),
            parse_float(row.get("Valence")),
            parse_float(row.get("Tempo")),
            parse_int(row.get("Time Signature")),
        ),
    )


def ensure_artist(cursor, spotify_artist_id, name, image_url):
    existing_id = None

    if spotify_artist_id:
        existing_id = fetch_one_id(
            cursor,
            "SELECT id FROM artists WHERE spotify_artist_id = %s LIMIT 1",
            (spotify_artist_id,),
        )

    if not existing_id:
        existing_id = fetch_one_id(
            cursor,
            "SELECT id FROM artists WHERE name = %s LIMIT 1",
            (name,),
        )

    if existing_id:
        cursor.execute(
            """
            UPDATE artists
            SET spotify_artist_id = COALESCE(%s, spotify_artist_id),
                name = COALESCE(%s, name),
                artist_name = COALESCE(%s, artist_name),
                image_url = COALESCE(%s, image_url)
            WHERE id = %s
            """,
            (spotify_artist_id, name, name, image_url, existing_id),
        )
        return existing_id

    cursor.execute(
        """
        INSERT INTO artists (
            spotify_artist_id,
            name,
            artist_name,
            image_url
        ) VALUES (%s, %s, %s, %s)
        """,
        (spotify_artist_id, name, name, image_url),
    )
    return int(cursor.lastrowid)


def ensure_genre(cursor, genre_name):
    existing_id = fetch_one_id(
        cursor,
        "SELECT id FROM genres WHERE name = %s LIMIT 1",
        (genre_name,),
    )
    if existing_id:
        return existing_id

    cursor.execute(
        "INSERT INTO genres (name) VALUES (%s)",
        (genre_name,),
    )
    return int(cursor.lastrowid)


def ensure_track_artist(cursor, track_id, artist_id):
    cursor.execute(
        """
        INSERT IGNORE INTO track_artists (track_id, artist_id)
        VALUES (%s, %s)
        """,
        (track_id, artist_id),
    )


def ensure_artist_genre(cursor, artist_id, genre_id):
    cursor.execute(
        """
        INSERT IGNORE INTO artist_genres (artist_id, genre_id)
        VALUES (%s, %s)
        """,
        (artist_id, genre_id),
    )


def ensure_playlist_track(cursor, playlist_id, track_id, added_at):
    cursor.execute(
        """
        INSERT INTO playlist_tracks (playlist_id, track_id, added_at)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE added_at = VALUES(added_at)
        """,
        (playlist_id, track_id, added_at),
    )


def build_enriched_payload(track_uri):
    spotify_track_id = extract_track_id(track_uri)
    if not spotify_track_id:
        return None

    track_data = get_spotify_track(spotify_track_id)
    album = track_data.get("album") or {}
    album_images = album.get("images") or []

    artists_payload = []
    for simplified_artist in track_data.get("artists", []):
        spotify_artist_id = simplified_artist.get("id")
        image_url = None

        if spotify_artist_id:
            artist_data = get_spotify_artist(spotify_artist_id)
            if artist_data:
                image_url = get_first_image_url(artist_data.get("images"))

        artists_payload.append(
            {
                "spotify_artist_id": spotify_artist_id,
                "name": simplified_artist.get("name"),
                "artist_name": simplified_artist.get("name"),
                "image_url": image_url,
            }
        )

    return {
        "spotify_track_id": track_data.get("id"),
        "track_uri": track_data.get("uri"),
        "track_name": track_data.get("name"),
        "spotify_url": (track_data.get("external_urls") or {}).get("spotify"),
        "preview_url": track_data.get("preview_url"),
        "cover_image_url": get_first_image_url(album_images),
        "duration_ms": track_data.get("duration_ms"),
        "explicit": track_data.get("explicit"),
        "popularity": track_data.get("popularity"),
        "album": {
            "spotify_album_id": album.get("id"),
            "name": album.get("name"),
            "release_date": album.get("release_date"),
            "image_url": get_first_image_url(album_images),
        },
        "artists": artists_payload,
    }


@app.post("/api/import/exportify")
async def import_exportify_csv(
    file: UploadFile = File(...),
    playlist_name: str = Form(...),
    enrich_with_spotify: bool = Form(True),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / file.filename

    try:
        file_content = await file.read()
        temp_path.write_bytes(file_content)

        processed_rows = 0
        imported_tracks = 0
        linked_artists = 0
        linked_genres = 0

        with pymysql.connect(**get_db_config()) as connection:
            with connection.cursor() as cursor:
                playlist_id = ensure_playlist(cursor, playlist_name)

                with temp_path.open("r", encoding="utf-8-sig", newline="") as file_handle:
                    reader = csv.DictReader(file_handle)

                    for row in reader:
                        processed_rows += 1

                        enrichment = None
                        if enrich_with_spotify:
                            try:
                                enrichment = build_enriched_payload(row.get("Track URI"))
                            except Exception:
                                enrichment = None

                        label_name = clean_text(row.get("Record Label"))
                        label_id = ensure_record_label(cursor, label_name)

                        enriched_album = (enrichment or {}).get("album", {})

                        album_id = ensure_album(
                            cursor=cursor,
                            spotify_album_id=enriched_album.get("spotify_album_id"),
                            album_name=clean_text(row.get("Album Name")) or enriched_album.get("name"),
                            release_date=parse_date(row.get("Release Date")) or enriched_album.get("release_date"),
                            label_id=label_id,
                            image_url=enriched_album.get("image_url"),
                        )

                        track_id = ensure_track(
                            cursor=cursor,
                            spotify_track_id=(enrichment or {}).get("spotify_track_id") or extract_track_id(row.get("Track URI")),
                            track_uri=clean_text(row.get("Track URI")) or (enrichment or {}).get("track_uri"),
                            name=clean_text(row.get("Track Name")) or (enrichment or {}).get("track_name"),
                            album_id=album_id,
                            duration_ms=parse_int(row.get("Duration (ms)")) or (enrichment or {}).get("duration_ms"),
                            popularity=parse_int(row.get("Popularity")) if row.get("Popularity") not in (None, "", "-") else (enrichment or {}).get("popularity"),
                            explicit=parse_bool(row.get("Explicit")),
                            spotify_url=(enrichment or {}).get("spotify_url"),
                            preview_url=(enrichment or {}).get("preview_url"),
                            cover_image_url=(enrichment or {}).get("cover_image_url"),
                        )
                        imported_tracks += 1

                        upsert_audio_features(cursor, track_id, row)

                        artist_names = split_artists(row.get("Artist Name(s)"))
                        enriched_artists = (enrichment or {}).get("artists", [])

                        for index, artist_name in enumerate(artist_names):
                            enriched_artist = enriched_artists[index] if index < len(enriched_artists) else {}

                            artist_id = ensure_artist(
                                cursor=cursor,
                                spotify_artist_id=enriched_artist.get("spotify_artist_id"),
                                name=artist_name,
                                image_url=enriched_artist.get("image_url"),
                            )
                            ensure_track_artist(cursor, track_id, artist_id)
                            linked_artists += 1

                            for genre_name in split_genres(row.get("Genres")):
                                genre_id = ensure_genre(cursor, genre_name)
                                ensure_artist_genre(cursor, artist_id, genre_id)
                                linked_genres += 1

                        ensure_playlist_track(
                            cursor=cursor,
                            playlist_id=playlist_id,
                            track_id=track_id,
                            added_at=parse_timestamp(row.get("Added At")),
                        )

                connection.commit()

        return {
            "status": "ok",
            "playlist_id": playlist_id,
            "processed_rows": processed_rows,
            "imported_tracks": imported_tracks,
            "linked_artists": linked_artists,
            "linked_genres": linked_genres,
        }

    except (OperationalError, InterfaceError):
        raise HTTPException(status_code=503, detail="Database is not reachable")
    except MySQLError as exc:
        raise HTTPException(status_code=500, detail=f"Database query failed: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

# =========================================================
# CSV IMPORT HELPERS END
# =========================================================