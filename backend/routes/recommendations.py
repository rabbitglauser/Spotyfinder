from __future__ import annotations

from typing import Any

import pymysql
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pymysql.err import InterfaceError, MySQLError, OperationalError

from db import get_db_config

# Falls deine Datei wirklich "Spotify_service.py" heisst, nimm stattdessen:
# from services.Spotify_service import SpotifyService
from services.spotify_service import SpotifyService

router = APIRouter()


class RecommendationFilterPayload(BaseModel):
    includeGenres: list[str] = Field(default_factory=list)
    excludeGenres: list[str] = Field(default_factory=list)
    popularity: int = 0


class RecommendationRequest(BaseModel):
    playlist_name: str
    limit: int = 8
    filters: RecommendationFilterPayload = Field(
        default_factory=RecommendationFilterPayload
    )


PALETTES = [
    {
        "primary": "#2A9D8F",
        "secondary": "#1D3557",
        "accent": "#52E3C2",
        "surface": "#101820",
    },
    {
        "primary": "#7B2CBF",
        "secondary": "#240046",
        "accent": "#C77DFF",
        "surface": "#140A1F",
    },
    {
        "primary": "#E76F51",
        "secondary": "#5F0F40",
        "accent": "#FF9F6E",
        "surface": "#1A1013",
    },
    {
        "primary": "#3A86FF",
        "secondary": "#1B263B",
        "accent": "#7CC6FE",
        "surface": "#0F1722",
    },
]


def build_palette(index: int) -> dict[str, str]:
    return PALETTES[index % len(PALETTES)]


def format_duration(duration_ms: Any) -> str:
    if not isinstance(duration_ms, int) or duration_ms <= 0:
        return "0:00"

    total_seconds = duration_ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def normalize_terms(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values if value.strip()]


def genre_matches(
    track_genres: list[str],
    include_genres: list[str],
    exclude_genres: list[str],
) -> bool:
    normalized_track_genres = [genre.lower() for genre in track_genres]

    if include_genres:
        has_include_match = any(
            include_term in track_genre or track_genre in include_term
            for include_term in include_genres
            for track_genre in normalized_track_genres
        )
        if not has_include_match:
            return False

    if exclude_genres:
        has_exclude_match = any(
            exclude_term in track_genre or track_genre in exclude_term
            for exclude_term in exclude_genres
            for track_genre in normalized_track_genres
        )
        if has_exclude_match:
            return False

    return True


@router.post("/api/recommendations")
def get_recommendations(payload: RecommendationRequest):
    limit = max(1, min(payload.limit, 20))
    popularity_threshold = max(0, min(payload.filters.popularity, 100))
    include_genres = normalize_terms(payload.filters.includeGenres)
    exclude_genres = normalize_terms(payload.filters.excludeGenres)

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
                        t.popularity
                    FROM tracks AS t
                    WHERE COALESCE(t.popularity, 0) >= %s
                    ORDER BY COALESCE(t.popularity, 0) DESC, t.id DESC
                    LIMIT %s
                    """,
                    (popularity_threshold, max(limit * 5, 20)),
                )
                rows = cursor.fetchall()

        spotify: SpotifyService | None = None
        try:
            spotify = SpotifyService()
        except ValueError:
            spotify = None

        recommendations: list[dict[str, Any]] = []

        for index, row in enumerate(rows):
            spotify_track_id = row.get("spotify_track_id")
            track_uri = row.get("track_uri")
            track_name = row.get("name") or "Unknown track"
            duration_ms = row.get("duration_ms")
            popularity = row.get("popularity") or 0

            artist_name = "Unknown Artist"
            genres: list[str] = []
            followers = 0
            preview_url = None
            cover_image_url = None

            if spotify:
                resolved_track_id = spotify_track_id or SpotifyService.extract_track_id(
                    track_uri
                )

                if resolved_track_id:
                    try:
                        track_data = spotify.get_track(resolved_track_id)

                        artists = track_data.get("artists") or []
                        artist_names = [
                            artist.get("name")
                            for artist in artists
                            if artist.get("name")
                        ]
                        if artist_names:
                            artist_name = ", ".join(artist_names)

                        album = track_data.get("album") or {}
                        album_images = album.get("images") or []
                        cover_image_url = SpotifyService.first_image_url(album_images)
                        preview_url = track_data.get("preview_url")

                        first_artist = artists[0] if artists else None
                        first_artist_id = (
                            first_artist.get("id")
                            if isinstance(first_artist, dict)
                            else None
                        )

                        if first_artist_id:
                            try:
                                artist_data = spotify.get_artist(first_artist_id)
                                genres = artist_data.get("genres") or []
                                followers = (
                                    (artist_data.get("followers") or {}).get("total")
                                    or 0
                                )
                            except requests.RequestException:
                                pass

                    except requests.RequestException:
                        pass

            if not genre_matches(genres, include_genres, exclude_genres):
                continue

            recommendations.append(
                {
                    "id": row.get("id"),
                    "title": track_name,
                    "artist": artist_name,
                    "genres": genres,
                    "followers": followers,
                    "monthlyListeners": 0,
                    "duration": format_duration(duration_ms),
                    "palette": build_palette(index),
                    "previewUrl": preview_url,
                    "coverImageUrl": cover_image_url,
                    "popularity": popularity,
                }
            )

            if len(recommendations) >= limit:
                break

        return {
            "count": len(recommendations),
            "items": recommendations,
            "playlist_name": payload.playlist_name,
        }

    except (OperationalError, InterfaceError):
        raise HTTPException(status_code=503, detail="Database is not reachable")
    except MySQLError:
        raise HTTPException(status_code=500, detail="Database query failed")
    
    print("REC TRACK:", track_name, "ARTIST:", artist_name, "GENRES:", genres, "POPULARITY:", popularity)