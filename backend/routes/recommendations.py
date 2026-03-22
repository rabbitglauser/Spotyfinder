from __future__ import annotations

from typing import Any

import pymysql
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pymysql.err import InterfaceError, MySQLError, OperationalError

from db import get_db_config

router = APIRouter()


class RecommendationFilterPayload(BaseModel):
    includeGenres: list[str] = Field(default_factory=list)
    excludeGenres: list[str] = Field(default_factory=list)
    popularity: int = 0
    danceability: int | None = None
    energy: int | None = None
    mood: int | None = None
    acoustic: int | None = None


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
    return [value.strip().lower() for value in values if value and value.strip()]


def split_grouped_values(value: str | None) -> list[str]:
    if not value:
        return []

    parts = [item.strip() for item in value.split("||")]
    seen: set[str] = set()
    result: list[str] = []

    for part in parts:
        normalized = part.lower()
        if part and normalized not in seen:
            seen.add(normalized)
            result.append(part)

    return result


def normalize_slider(value: int | None) -> float | None:
    if value is None:
        return None
    clamped = max(0, min(value, 100))
    return clamped / 100.0


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


def append_reason(reasons: list[str], text: str) -> None:
    if text not in reasons:
        reasons.append(text)


def score_feature(
    reasons: list[str],
    label: str,
    actual: Any,
    target: float | None,
    weight: float,
) -> float:
    if target is None:
        return 0.0

    if actual is None:
        return 0.35 * weight

    diff = abs(float(actual) - float(target))

    if diff <= 0.08:
        append_reason(reasons, f"{label} is very close to your target.")
    elif diff <= 0.16:
        append_reason(reasons, f"{label} is close to your target.")

    return diff * weight


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
                        AVG(af.danceability) AS avg_danceability,
                        AVG(af.energy) AS avg_energy,
                        AVG(af.valence) AS avg_mood,
                        AVG(af.acousticness) AS avg_acoustic,
                        GROUP_CONCAT(DISTINCT g.name ORDER BY g.name SEPARATOR '||') AS playlist_genres
                    FROM playlists p
                    JOIN playlist_tracks pt ON pt.playlist_id = p.id
                    JOIN tracks t ON t.id = pt.track_id
                    LEFT JOIN audio_features af ON af.track_id = t.id
                    LEFT JOIN track_artists ta ON ta.track_id = t.id
                    LEFT JOIN artists a ON a.id = ta.artist_id
                    LEFT JOIN artist_genres ag ON ag.artist_id = a.id
                    LEFT JOIN genres g ON g.id = ag.genre_id
                    WHERE p.name = %s
                    """,
                    (payload.playlist_name,),
                )
                playlist_profile = cursor.fetchone() or {}

                cursor.execute(
                    """
                    SELECT
                        t.id,
                        t.spotify_track_id,
                        t.name AS track_name,
                        t.duration_ms,
                        COALESCE(t.popularity, 0) AS popularity,
                        t.preview_url,
                        t.cover_image_url,
                        af.danceability,
                        af.energy,
                        af.valence,
                        af.acousticness,
                        GROUP_CONCAT(DISTINCT a.name ORDER BY a.name SEPARATOR '||') AS artist_names,
                        GROUP_CONCAT(DISTINCT g.name ORDER BY g.name SEPARATOR '||') AS genre_names
                    FROM tracks t
                    LEFT JOIN audio_features af ON af.track_id = t.id
                    LEFT JOIN track_artists ta ON ta.track_id = t.id
                    LEFT JOIN artists a ON a.id = ta.artist_id
                    LEFT JOIN artist_genres ag ON ag.artist_id = a.id
                    LEFT JOIN genres g ON g.id = ag.genre_id
                    WHERE COALESCE(t.popularity, 0) >= %s
                      AND t.id NOT IN (
                        SELECT pt.track_id
                        FROM playlist_tracks pt
                        JOIN playlists p ON p.id = pt.playlist_id
                        WHERE p.name = %s
                      )
                    GROUP BY
                        t.id,
                        t.spotify_track_id,
                        t.name,
                        t.duration_ms,
                        t.popularity,
                        t.preview_url,
                        t.cover_image_url,
                        af.danceability,
                        af.energy,
                        af.valence,
                        af.acousticness
                    ORDER BY
                        CASE WHEN t.preview_url IS NOT NULL AND t.preview_url <> '' THEN 0 ELSE 1 END,
                        CASE WHEN t.cover_image_url IS NOT NULL AND t.cover_image_url <> '' THEN 0 ELSE 1 END,
                        COALESCE(t.popularity, 0) DESC,
                        t.id DESC
                    LIMIT %s
                    """,
                    (popularity_threshold, payload.playlist_name, max(limit * 80, 400)),
                )
                rows = cursor.fetchall()

        playlist_genres = normalize_terms(
            split_grouped_values(playlist_profile.get("playlist_genres"))
        )
        playlist_genre_set = set(playlist_genres)

        target_danceability = (
            normalize_slider(payload.filters.danceability)
            if payload.filters.danceability is not None
            else playlist_profile.get("avg_danceability")
        )
        target_energy = (
            normalize_slider(payload.filters.energy)
            if payload.filters.energy is not None
            else playlist_profile.get("avg_energy")
        )
        target_mood = (
            normalize_slider(payload.filters.mood)
            if payload.filters.mood is not None
            else playlist_profile.get("avg_mood")
        )
        target_acoustic = (
            normalize_slider(payload.filters.acoustic)
            if payload.filters.acoustic is not None
            else playlist_profile.get("avg_acoustic")
        )

        scored_candidates: list[dict[str, Any]] = []

        for row in rows:
            track_name = row.get("track_name") or "Unknown track"
            duration_ms = row.get("duration_ms")
            popularity = row.get("popularity") or 0
            preview_url = row.get("preview_url")
            cover_image_url = row.get("cover_image_url")

            has_preview = bool(preview_url)
            has_cover = bool(cover_image_url)

            artist_names = split_grouped_values(row.get("artist_names"))
            genre_names = split_grouped_values(row.get("genre_names"))
            normalized_genres = normalize_terms(genre_names)

            if not genre_matches(genre_names, include_genres, exclude_genres):
                continue

            artist_name = ", ".join(artist_names) if artist_names else "Unknown Artist"

            reasons: list[str] = []
            score = 0.0

            score += score_feature(
                reasons,
                "Danceability",
                row.get("danceability"),
                target_danceability,
                1.6,
            )
            score += score_feature(
                reasons,
                "Energy",
                row.get("energy"),
                target_energy,
                1.5,
            )
            score += score_feature(
                reasons,
                "Mood",
                row.get("valence"),
                target_mood,
                1.2,
            )
            score += score_feature(
                reasons,
                "Acousticness",
                row.get("acousticness"),
                target_acoustic,
                1.3,
            )

            if include_genres:
                append_reason(reasons, "Matches your included genres.")

            overlap = sorted(set(normalized_genres) & playlist_genre_set)
            if overlap:
                append_reason(
                    reasons,
                    f"Shares playlist genres like {', '.join(overlap[:2])}.",
                )
                score -= min(len(overlap), 3) * 0.15

            if has_preview:
                append_reason(reasons, "Preview available.")
                score -= 0.45

            if has_cover:
                append_reason(reasons, "Album cover available.")
                score -= 0.15

            if popularity_threshold > 0:
                append_reason(
                    reasons,
                    f"Meets your popularity threshold ({popularity_threshold}+).",
                )

            if not reasons:
                append_reason(reasons, "Similar overall profile to your playlist.")

            scored_candidates.append(
                {
                    "id": row.get("id"),
                    "spotifyTrackId": row.get("spotify_track_id"),
                    "title": track_name,
                    "artist": artist_name,
                    "genres": genre_names,
                    "duration": format_duration(duration_ms),
                    "palette": build_palette(len(scored_candidates)),
                    "previewUrl": preview_url,
                    "coverImageUrl": cover_image_url,
                    "popularity": popularity,
                    "matchReasons": reasons[:4],
                    "_score": score,
                    "_has_preview": has_preview,
                    "_has_cover": has_cover,
                }
            )

        scored_candidates.sort(
            key=lambda item: (
                0 if item["_has_preview"] else 1,
                0 if item["_has_cover"] else 1,
                item["_score"],
                -(item.get("popularity") or 0),
                item["title"].lower(),
            )
        )

        recommendations = []
        for index, item in enumerate(scored_candidates[:limit]):
            cleaned = {
                key: value
                for key, value in item.items()
                if key not in {"_score", "_has_preview", "_has_cover"}
            }
            cleaned["palette"] = build_palette(index)
            recommendations.append(cleaned)

        return {
            "count": len(recommendations),
            "items": recommendations,
            "playlist_name": payload.playlist_name,
        }

    except (OperationalError, InterfaceError):
        raise HTTPException(status_code=503, detail="Database is not reachable")
    except MySQLError as exc:
        raise HTTPException(status_code=500, detail=f"Database query failed: {exc}")