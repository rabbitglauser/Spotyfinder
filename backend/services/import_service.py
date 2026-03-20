import csv
import io
import traceback

import pymysql
from fastapi import HTTPException, UploadFile
from pymysql.err import InterfaceError, MySQLError, OperationalError

from db import get_db_config
from services.spotify_service import build_enriched_payload, extract_track_id
from utils.csv_helpers import (
    clean_text,
    parse_bool,
    parse_date,
    parse_float,
    parse_int,
    parse_timestamp,
    split_artists,
    split_genres,
)


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


def safe_build_enrichment(track_uri):
    try:
        return build_enriched_payload(track_uri)
    except Exception:
        return None


async def import_exportify_file(
    file: UploadFile,
    playlist_name: str,
    enrich_with_spotify: bool = True,
):
    filename = file.filename or ""

    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    try:
        raw_content = await file.read()
        csv_text = raw_content.decode("utf-8-sig")
        csv_buffer = io.StringIO(csv_text)

        processed_rows = 0
        imported_tracks = 0
        linked_artists = 0
        linked_genres = 0

        with pymysql.connect(**get_db_config()) as connection:
            with connection.cursor() as cursor:
                connection.ping(reconnect=True)
                playlist_id = ensure_playlist(cursor, playlist_name)
                reader = csv.DictReader(csv_buffer)

                for row in reader:
                    processed_rows += 1
                    print(
                        "IMPORTING ROW:",
                        processed_rows,
                        row.get("Track Name"),
                        row.get("Track URI"),
                    )

                    enrichment = None
                    if enrich_with_spotify:
                        enrichment = safe_build_enrichment(row.get("Track URI"))

                    connection.ping(reconnect=True)

                    enriched_album = (enrichment or {}).get("album", {})
                    label_name = clean_text(row.get("Record Label"))
                    label_id = ensure_record_label(cursor, label_name)

                    album_id = ensure_album(
                        cursor=cursor,
                        spotify_album_id=enriched_album.get("spotify_album_id"),
                        album_name=clean_text(row.get("Album Name")) or enriched_album.get("name"),
                        release_date=parse_date(row.get("Release Date")) or parse_date(enriched_album.get("release_date")),
                        label_id=label_id,
                        image_url=enriched_album.get("image_url"),
                    )

                    track_id = ensure_track(
                        cursor=cursor,
                        spotify_track_id=(enrichment or {}).get("spotify_track_id")
                        or extract_track_id(row.get("Track URI")),
                        track_uri=clean_text(row.get("Track URI")) or (enrichment or {}).get("track_uri"),
                        name=clean_text(row.get("Track Name")) or (enrichment or {}).get("track_name"),
                        album_id=album_id,
                        duration_ms=parse_int(row.get("Duration (ms)")) or (enrichment or {}).get("duration_ms"),
                        popularity=parse_int(row.get("Popularity"))
                        if row.get("Popularity") not in (None, "", "-")
                        else (enrichment or {}).get("popularity"),
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
                        enriched_artist = (
                            enriched_artists[index]
                            if index < len(enriched_artists)
                            else {}
                        )

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

                print("ABOUT TO COMMIT")
                connection.ping(reconnect=True)
                connection.commit()
                print("COMMIT OK")

        return {
            "status": "ok",
            "playlist_id": playlist_id,
            "processed_rows": processed_rows,
            "imported_tracks": imported_tracks,
            "linked_artists": linked_artists,
            "linked_genres": linked_genres,
        }

    except (OperationalError, InterfaceError) as exc:
        print("DB CONNECTION ERROR:", repr(exc))
        traceback.print_exc()
        raise HTTPException(status_code=503, detail=f"Database connection problem: {exc}")
    except MySQLError as exc:
        print("MYSQL ERROR:", repr(exc))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"MySQL error: {exc}")
    except Exception as exc:
        print("GENERAL ERROR:", repr(exc))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")

    except (OperationalError, InterfaceError) as exc:
            raise HTTPException(status_code=503, detail=f"Database connection problem: {exc}")
    except MySQLError as exc:
            raise HTTPException(status_code=500, detail=f"MySQL error: {exc}")
    except Exception as exc:
            raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")