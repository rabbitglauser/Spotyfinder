from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import mysql.connector
from dotenv import load_dotenv

from spotify_service import SpotifyService

load_dotenv()


@dataclass
class ImportSummary:
    playlist_id: int
    processed_rows: int
    imported_tracks: int
    linked_artists: int
    linked_genres: int


class CsvImportService:
    def __init__(self, spotify_service: SpotifyService | None = None) -> None:
        self.spotify_service = spotify_service

    def _get_connection(self):
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "spotyfinderdb"),
            autocommit=False,
        )

    @staticmethod
    def _clean_text(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text or text == "-":
            return None
        return text

    @staticmethod
    def _parse_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        return text in {"true", "1", "yes", "y"}

    @staticmethod
    def _parse_date(value: Any) -> str | None:
        text = CsvImportService._clean_text(value)
        if not text:
            return None
        return text

    @staticmethod
    def _parse_timestamp(value: Any) -> str | None:
        text = CsvImportService._clean_text(value)
        if not text:
            return None
        return text.replace("Z", "+00:00")

    @staticmethod
    def _parse_float(value: Any) -> float | None:
        if value in (None, "", "-"):
            return None
        return float(value)

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        if value in (None, "", "-"):
            return None
        return int(float(value))

    @staticmethod
    def _split_artists(value: Any) -> list[str]:
        text = CsvImportService._clean_text(value)
        if not text:
            return []
        return [part.strip() for part in text.split(";") if part.strip()]

    @staticmethod
    def _split_genres(value: Any) -> list[str]:
        text = CsvImportService._clean_text(value)
        if not text:
            return []
        return [part.strip() for part in text.split(",") if part.strip()]

    def _fetch_one_id(self, cursor, query: str, params: tuple[Any, ...]) -> int | None:
        cursor.execute(query, params)
        row = cursor.fetchone()
        if not row:
            return None
        return int(row["id"])

    def _ensure_playlist(self, cursor, playlist_name: str) -> int:
        existing_id = self._fetch_one_id(
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

    def _ensure_record_label(self, cursor, label_name: str | None) -> int | None:
        if not label_name:
            return None

        existing_id = self._fetch_one_id(
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

    def _ensure_album(
        self,
        cursor,
        spotify_album_id: str | None,
        album_name: str | None,
        release_date: str | None,
        label_id: int | None,
        image_url: str | None,
    ) -> int | None:
        if not album_name and not spotify_album_id:
            return None

        if spotify_album_id:
            existing_id = self._fetch_one_id(
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

        existing_id = self._fetch_one_id(
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

    def _ensure_track(
        self,
        cursor,
        spotify_track_id: str | None,
        track_uri: str | None,
        name: str | None,
        album_id: int | None,
        duration_ms: int | None,
        popularity: int | None,
        explicit: bool,
        spotify_url: str | None,
        preview_url: str | None,
        cover_image_url: str | None,
    ) -> int:
        existing_id = None

        if spotify_track_id:
            existing_id = self._fetch_one_id(
                cursor,
                "SELECT id FROM tracks WHERE spotify_track_id = %s LIMIT 1",
                (spotify_track_id,),
            )

        if not existing_id and track_uri:
            existing_id = self._fetch_one_id(
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

    def _upsert_audio_features(
        self,
        cursor,
        track_id: int,
        row: dict[str, Any],
    ) -> None:
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
                self._parse_float(row.get("Danceability")),
                self._parse_float(row.get("Energy")),
                self._parse_int(row.get("Key")),
                self._parse_float(row.get("Loudness")),
                self._parse_int(row.get("Mode")),
                self._parse_float(row.get("Speechiness")),
                self._parse_float(row.get("Acousticness")),
                self._parse_float(row.get("Instrumentalness")),
                self._parse_float(row.get("Liveness")),
                self._parse_float(row.get("Valence")),
                self._parse_float(row.get("Tempo")),
                self._parse_int(row.get("Time Signature")),
            ),
        )

    def _ensure_artist(
        self,
        cursor,
        spotify_artist_id: str | None,
        name: str,
        image_url: str | None,
    ) -> int:
        existing_id = None

        if spotify_artist_id:
            existing_id = self._fetch_one_id(
                cursor,
                "SELECT id FROM artists WHERE spotify_artist_id = %s LIMIT 1",
                (spotify_artist_id,),
            )

        if not existing_id:
            existing_id = self._fetch_one_id(
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

    def _ensure_genre(self, cursor, genre_name: str) -> int:
        existing_id = self._fetch_one_id(
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

    def _ensure_track_artist(self, cursor, track_id: int, artist_id: int) -> None:
        cursor.execute(
            """
            INSERT IGNORE INTO track_artists (track_id, artist_id)
            VALUES (%s, %s)
            """,
            (track_id, artist_id),
        )

    def _ensure_artist_genre(self, cursor, artist_id: int, genre_id: int) -> None:
        cursor.execute(
            """
            INSERT IGNORE INTO artist_genres (artist_id, genre_id)
            VALUES (%s, %s)
            """,
            (artist_id, genre_id),
        )

    def _ensure_playlist_track(
        self,
        cursor,
        playlist_id: int,
        track_id: int,
        added_at: str | None,
    ) -> None:
        cursor.execute(
            """
            INSERT INTO playlist_tracks (playlist_id, track_id, added_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE added_at = VALUES(added_at)
            """,
            (playlist_id, track_id, added_at),
        )

    def _build_artist_enrichment_map(
        self,
        enrichment: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        if not enrichment:
            return []
        return enrichment.get("artists", [])

    def import_exportify_csv(
        self,
        csv_path: str | Path,
        playlist_name: str,
        enrich_with_spotify: bool = True,
    ) -> ImportSummary:
        csv_path = Path(csv_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        connection = self._get_connection()
        cursor = connection.cursor(dictionary=True)

        processed_rows = 0
        imported_tracks = 0
        linked_artists = 0
        linked_genres = 0

        try:
            playlist_id = self._ensure_playlist(cursor, playlist_name)

            with csv_path.open("r", encoding="utf-8-sig", newline="") as file_handle:
                reader = csv.DictReader(file_handle)

                for raw_row in reader:
                    processed_rows += 1

                    enrichment = None
                    if enrich_with_spotify and self.spotify_service:
                        try:
                            enrichment = self.spotify_service.enrich_track_uri(raw_row.get("Track URI"))
                        except Exception:
                            enrichment = None

                    label_name = self._clean_text(raw_row.get("Record Label"))
                    label_id = self._ensure_record_label(cursor, label_name)

                    enriched_album = (enrichment or {}).get("album", {})
                    album_id = self._ensure_album(
                        cursor=cursor,
                        spotify_album_id=enriched_album.get("spotify_album_id"),
                        album_name=self._clean_text(raw_row.get("Album Name")) or enriched_album.get("name"),
                        release_date=self._parse_date(raw_row.get("Release Date")) or enriched_album.get("release_date"),
                        label_id=label_id,
                        image_url=enriched_album.get("image_url"),
                    )

                    track_id = self._ensure_track(
                        cursor=cursor,
                        spotify_track_id=(
                            (enrichment or {}).get("spotify_track_id")
                            or SpotifyService.extract_track_id(raw_row.get("Track URI"))
                        ),
                        track_uri=self._clean_text(raw_row.get("Track URI")) or (enrichment or {}).get("track_uri"),
                        name=self._clean_text(raw_row.get("Track Name")) or (enrichment or {}).get("track_name"),
                        album_id=album_id,
                        duration_ms=self._parse_int(raw_row.get("Duration (ms)"))
                        or (enrichment or {}).get("duration_ms"),
                        popularity=self._parse_int(raw_row.get("Popularity"))
                        if raw_row.get("Popularity") not in (None, "", "-")
                        else (enrichment or {}).get("popularity"),
                        explicit=self._parse_bool(raw_row.get("Explicit")),
                        spotify_url=(enrichment or {}).get("spotify_url"),
                        preview_url=(enrichment or {}).get("preview_url"),
                        cover_image_url=(enrichment or {}).get("cover_image_url"),
                    )
                    imported_tracks += 1

                    self._upsert_audio_features(cursor, track_id, raw_row)

                    artist_names = self._split_artists(raw_row.get("Artist Name(s)"))
                    artist_enrichment = self._build_artist_enrichment_map(enrichment)

                    for index, artist_name in enumerate(artist_names):
                        enriched_artist = artist_enrichment[index] if index < len(artist_enrichment) else {}

                        artist_id = self._ensure_artist(
                            cursor=cursor,
                            spotify_artist_id=enriched_artist.get("spotify_artist_id"),
                            name=artist_name,
                            image_url=enriched_artist.get("image_url"),
                        )
                        self._ensure_track_artist(cursor, track_id, artist_id)
                        linked_artists += 1

                        for genre_name in self._split_genres(raw_row.get("Genres")):
                            genre_id = self._ensure_genre(cursor, genre_name)
                            self._ensure_artist_genre(cursor, artist_id, genre_id)
                            linked_genres += 1

                    self._ensure_playlist_track(
                        cursor=cursor,
                        playlist_id=playlist_id,
                        track_id=track_id,
                        added_at=self._parse_timestamp(raw_row.get("Added At")),
                    )

            connection.commit()

            return ImportSummary(
                playlist_id=playlist_id,
                processed_rows=processed_rows,
                imported_tracks=imported_tracks,
                linked_artists=linked_artists,
                linked_genres=linked_genres,
            )

        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()