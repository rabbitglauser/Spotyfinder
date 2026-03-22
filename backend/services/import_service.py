from __future__ import annotations

import csv
import io
import traceback
from typing import Any

import pymysql
from fastapi import HTTPException, UploadFile
from pymysql.err import InterfaceError, MySQLError, OperationalError

from db import get_db_config
from services.spotify_service import enrich_track_uris, extract_track_id
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


def fetch_one_id(cursor, query: str, params: tuple[Any, ...]) -> int | None:
    cursor.execute(query, params)
    row = cursor.fetchone()
    if not row:
        return None
    return int(row["id"])


def ensure_playlist(
    cursor,
    playlist_name: str,
    playlist_cache: dict[str, int],
) -> int:
    cache_key = playlist_name.strip().lower()
    cached_id = playlist_cache.get(cache_key)
    if cached_id:
        return cached_id

    existing_id = fetch_one_id(
        cursor,
        "SELECT id FROM playlists WHERE name = %s LIMIT 1",
        (playlist_name,),
    )
    if existing_id:
        playlist_cache[cache_key] = existing_id
        return existing_id

    cursor.execute(
        "INSERT INTO playlists (spotify_playlist_id, name) VALUES (%s, %s)",
        (None, playlist_name),
    )
    playlist_id = int(cursor.lastrowid)
    playlist_cache[cache_key] = playlist_id
    return playlist_id


def ensure_record_label(
    cursor,
    label_name: str | None,
    record_label_cache: dict[str, int],
) -> int | None:
    if not label_name:
        return None

    cache_key = label_name.strip().lower()
    cached_id = record_label_cache.get(cache_key)
    if cached_id:
        return cached_id

    existing_id = fetch_one_id(
        cursor,
        "SELECT id FROM record_labels WHERE name = %s LIMIT 1",
        (label_name,),
    )
    if existing_id:
        record_label_cache[cache_key] = existing_id
        return existing_id

    cursor.execute(
        "INSERT INTO record_labels (name) VALUES (%s)",
        (label_name,),
    )
    label_id = int(cursor.lastrowid)
    record_label_cache[cache_key] = label_id
    return label_id


def ensure_album(
    cursor,
    spotify_album_id: str | None,
    album_name: str | None,
    release_date,
    label_id: int | None,
    image_url: str | None,
    album_cache_by_spotify_id: dict[str, int],
    album_cache_by_name_and_release: dict[tuple[str | None, Any], int],
) -> int | None:
    if not album_name and not spotify_album_id:
        return None

    if spotify_album_id:
        cached_id = album_cache_by_spotify_id.get(spotify_album_id)
        if cached_id:
            cursor.execute(
                """
                UPDATE albums
                SET name = COALESCE(%s, name),
                    release_date = COALESCE(%s, release_date),
                    label_id = COALESCE(%s, label_id),
                    image_url = COALESCE(%s, image_url)
                WHERE id = %s
                """,
                (album_name, release_date, label_id, image_url, cached_id),
            )
            return cached_id

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
            album_cache_by_spotify_id[spotify_album_id] = existing_id
            album_cache_by_name_and_release[(album_name, release_date)] = existing_id
            return existing_id

    key = (album_name, release_date)
    cached_id = album_cache_by_name_and_release.get(key)
    if cached_id:
        cursor.execute(
            """
            UPDATE albums
            SET spotify_album_id = COALESCE(%s, spotify_album_id),
                label_id = COALESCE(%s, label_id),
                image_url = COALESCE(%s, image_url)
            WHERE id = %s
            """,
            (spotify_album_id, label_id, image_url, cached_id),
        )
        if spotify_album_id:
            album_cache_by_spotify_id[spotify_album_id] = cached_id
        return cached_id

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
        if spotify_album_id:
            album_cache_by_spotify_id[spotify_album_id] = existing_id
        album_cache_by_name_and_release[key] = existing_id
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
    album_id = int(cursor.lastrowid)

    if spotify_album_id:
        album_cache_by_spotify_id[spotify_album_id] = album_id
    album_cache_by_name_and_release[key] = album_id

    return album_id


def ensure_track(
    cursor,
    spotify_track_id: str | None,
    track_uri: str | None,
    name: str | None,
    album_id: int | None,
    duration_ms: int | None,
    popularity: int | None,
    explicit: bool | None,
    spotify_url: str | None,
    preview_url: str | None,
    cover_image_url: str | None,
    track_cache_by_spotify_id: dict[str, int],
    track_cache_by_uri: dict[str, int],
) -> int:
    existing_id: int | None = None

    if spotify_track_id:
        existing_id = track_cache_by_spotify_id.get(spotify_track_id)
        if not existing_id:
            existing_id = fetch_one_id(
                cursor,
                "SELECT id FROM tracks WHERE spotify_track_id = %s LIMIT 1",
                (spotify_track_id,),
            )

    if not existing_id and track_uri:
        existing_id = track_cache_by_uri.get(track_uri)
        if not existing_id:
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
                explicit = COALESCE(%s, explicit),
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
        if spotify_track_id:
            track_cache_by_spotify_id[spotify_track_id] = existing_id
        if track_uri:
            track_cache_by_uri[track_uri] = existing_id
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
    track_id = int(cursor.lastrowid)

    if spotify_track_id:
        track_cache_by_spotify_id[spotify_track_id] = track_id
    if track_uri:
        track_cache_by_uri[track_uri] = track_id

    return track_id


def upsert_audio_features(cursor, track_id: int, row: dict[str, Any]) -> None:
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


def ensure_artist(
    cursor,
    spotify_artist_id: str | None,
    name: str | None,
    image_url: str | None,
    artist_cache_by_spotify_id: dict[str, int],
    artist_cache_by_name: dict[str, int],
) -> int | None:
    if not spotify_artist_id and not name:
        return None

    existing_id: int | None = None

    if spotify_artist_id:
        existing_id = artist_cache_by_spotify_id.get(spotify_artist_id)
        if not existing_id:
            existing_id = fetch_one_id(
                cursor,
                "SELECT id FROM artists WHERE spotify_artist_id = %s LIMIT 1",
                (spotify_artist_id,),
            )

    if not existing_id and name:
        cache_key = name.strip().lower()
        existing_id = artist_cache_by_name.get(cache_key)
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
        if spotify_artist_id:
            artist_cache_by_spotify_id[spotify_artist_id] = existing_id
        if name:
            artist_cache_by_name[name.strip().lower()] = existing_id
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
    artist_id = int(cursor.lastrowid)

    if spotify_artist_id:
        artist_cache_by_spotify_id[spotify_artist_id] = artist_id
    if name:
        artist_cache_by_name[name.strip().lower()] = artist_id

    return artist_id


def ensure_genre(
    cursor,
    genre_name: str,
    genre_cache: dict[str, int],
) -> int:
    cache_key = genre_name.strip().lower()
    cached_id = genre_cache.get(cache_key)
    if cached_id:
        return cached_id

    existing_id = fetch_one_id(
        cursor,
        "SELECT id FROM genres WHERE name = %s LIMIT 1",
        (genre_name,),
    )
    if existing_id:
        genre_cache[cache_key] = existing_id
        return existing_id

    cursor.execute(
        "INSERT INTO genres (name) VALUES (%s)",
        (genre_name,),
    )
    genre_id = int(cursor.lastrowid)
    genre_cache[cache_key] = genre_id
    return genre_id


def ensure_track_artist(cursor, track_id: int, artist_id: int) -> None:
    cursor.execute(
        """
        INSERT IGNORE INTO track_artists (track_id, artist_id)
        VALUES (%s, %s)
        """,
        (track_id, artist_id),
    )


def ensure_artist_genre(cursor, artist_id: int, genre_id: int) -> None:
    cursor.execute(
        """
        INSERT IGNORE INTO artist_genres (artist_id, genre_id)
        VALUES (%s, %s)
        """,
        (artist_id, genre_id),
    )


def ensure_playlist_track(
    cursor,
    playlist_id: int,
    track_id: int,
    added_at,
) -> None:
    cursor.execute(
        """
        INSERT INTO playlist_tracks (playlist_id, track_id, added_at)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE added_at = VALUES(added_at)
        """,
        (playlist_id, track_id, added_at),
    )


def build_spotify_enrichment_map(
    rows: list[dict[str, Any]],
    enrich_with_spotify: bool,
) -> dict[str, dict[str, Any]]:
    if not enrich_with_spotify:
        return {}

    track_uris = [clean_text(row.get("Track URI")) for row in rows]
    valid_track_uris = [track_uri for track_uri in track_uris if track_uri]

    if not valid_track_uris:
        return {}

    try:
        enrichment_map = enrich_track_uris(
            valid_track_uris,
            include_artist_details=False,
            market="CH",
        )
        print(
            f"SPOTIFY BULK ENRICHMENT OK: {len(enrichment_map)} track payloads fetched"
        )
        return enrichment_map
    except Exception as exc:
        print("SPOTIFY BULK ENRICHMENT FAILED:", repr(exc))
        traceback.print_exc()
        return {}


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
        reader = csv.DictReader(csv_buffer)
        rows = list(reader)

        processed_rows = 0
        imported_tracks = 0
        linked_artists = 0
        linked_genres = 0

        spotify_enrichment_by_track_id = build_spotify_enrichment_map(
            rows,
            enrich_with_spotify=enrich_with_spotify,
        )

        playlist_cache: dict[str, int] = {}
        record_label_cache: dict[str, int] = {}
        album_cache_by_spotify_id: dict[str, int] = {}
        album_cache_by_name_and_release: dict[tuple[str | None, Any], int] = {}
        track_cache_by_spotify_id: dict[str, int] = {}
        track_cache_by_uri: dict[str, int] = {}
        artist_cache_by_spotify_id: dict[str, int] = {}
        artist_cache_by_name: dict[str, int] = {}
        genre_cache: dict[str, int] = {}

        with pymysql.connect(**get_db_config()) as connection:
            with connection.cursor() as cursor:
                playlist_id = ensure_playlist(cursor, playlist_name, playlist_cache)

                for row in rows:
                    processed_rows += 1

                    if processed_rows <= 10 or processed_rows % 25 == 0:
                        print(
                            "IMPORTING ROW:",
                            processed_rows,
                            row.get("Track Name"),
                            row.get("Track URI"),
                        )

                    if processed_rows % 100 == 0:
                        connection.ping(reconnect=True)

                    track_uri = clean_text(row.get("Track URI"))
                    csv_track_name = clean_text(row.get("Track Name"))
                    csv_album_name = clean_text(row.get("Album Name"))
                    csv_label_name = clean_text(row.get("Record Label"))
                    csv_track_id = extract_track_id(track_uri)

                    enrichment = (
                        spotify_enrichment_by_track_id.get(csv_track_id, {})
                        if csv_track_id
                        else {}
                    )

                    enriched_album = enrichment.get("album", {})

                    label_id = ensure_record_label(
                        cursor=cursor,
                        label_name=csv_label_name,
                        record_label_cache=record_label_cache,
                    )

                    album_id = ensure_album(
                        cursor=cursor,
                        spotify_album_id=enriched_album.get("spotify_album_id"),
                        album_name=csv_album_name or enriched_album.get("name"),
                        release_date=parse_date(row.get("Release Date"))
                        or parse_date(enriched_album.get("release_date")),
                        label_id=label_id,
                        image_url=enriched_album.get("image_url"),
                        album_cache_by_spotify_id=album_cache_by_spotify_id,
                        album_cache_by_name_and_release=album_cache_by_name_and_release,
                    )

                    popularity_value = (
                        parse_int(row.get("Popularity"))
                        if row.get("Popularity") not in (None, "", "-")
                        else enrichment.get("popularity")
                    )

                    track_id = ensure_track(
                        cursor=cursor,
                        spotify_track_id=enrichment.get("spotify_track_id")
                        or csv_track_id,
                        track_uri=track_uri or enrichment.get("track_uri"),
                        name=csv_track_name or enrichment.get("track_name"),
                        album_id=album_id,
                        duration_ms=parse_int(row.get("Duration (ms)"))
                        or enrichment.get("duration_ms"),
                        popularity=popularity_value,
                        explicit=parse_bool(row.get("Explicit"))
                        if row.get("Explicit") not in (None, "")
                        else enrichment.get("explicit"),
                        spotify_url=enrichment.get("spotify_url"),
                        preview_url=enrichment.get("preview_url"),
                        cover_image_url=enrichment.get("cover_image_url"),
                        track_cache_by_spotify_id=track_cache_by_spotify_id,
                        track_cache_by_uri=track_cache_by_uri,
                    )
                    imported_tracks += 1

                    upsert_audio_features(cursor, track_id, row)

                    artist_names = split_artists(row.get("Artist Name(s)"))
                    enriched_artists = enrichment.get("artists", [])

                    genre_values = split_genres(row.get("Genres"))

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
                            artist_cache_by_spotify_id=artist_cache_by_spotify_id,
                            artist_cache_by_name=artist_cache_by_name,
                        )

                        if artist_id is None:
                            continue

                        ensure_track_artist(cursor, track_id, artist_id)
                        linked_artists += 1

                        for genre_name in genre_values:
                            genre_id = ensure_genre(cursor, genre_name, genre_cache)
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
            "spotify_enriched_tracks": len(spotify_enrichment_by_track_id),
        }

    except (OperationalError, InterfaceError) as exc:
        print("DB CONNECTION ERROR:", repr(exc))
        traceback.print_exc()
        raise HTTPException(
            status_code=503,
            detail=f"Database connection problem: {exc}",
        )
    except MySQLError as exc:
        print("MYSQL ERROR:", repr(exc))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"MySQL error: {exc}")
    except Exception as exc:
        print("GENERAL ERROR:", repr(exc))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")