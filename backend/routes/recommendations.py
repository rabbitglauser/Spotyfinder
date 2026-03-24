from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import pymysql
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pymysql.err import InterfaceError, MySQLError, OperationalError
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler

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

NUMERIC_FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "speechiness",
    "instrumentalness",
    "liveness",
    "tempo",
    "popularity",
]

NUMERIC_WEIGHTS = {
    "danceability": 1.8,
    "energy": 1.7,
    "valence": 1.4,
    "acousticness": 1.4,
    "speechiness": 0.45,
    "instrumentalness": 0.35,
    "liveness": 0.45,
    "tempo": 0.35,
    "popularity": 0.65,
}

SLIDER_TO_FEATURE = {
    "danceability": "danceability",
    "energy": "energy",
    "mood": "valence",
    "acoustic": "acousticness",
}

GENRE_MATRIX_WEIGHT = 2.4
SHARED_GENRE_BONUS_PER_MATCH = 0.045
TOP_GENRE_BONUS_PER_MATCH = 0.06
ZERO_GENRE_OVERLAP_PENALTY = 0.14
MAX_SHARED_GENRE_BONUS_MATCHES = 4
MAX_TOP_GENRE_BONUS_MATCHES = 3


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

    seen: set[str] = set()
    result: list[str] = []

    for part in value.split("||"):
        cleaned = part.strip()
        lowered = cleaned.lower()

        if cleaned and lowered not in seen:
            seen.add(lowered)
            result.append(cleaned)

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


def safe_float(value: Any) -> float:
    if value is None:
        return float("nan")

    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def fill_nan_with_column_median(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return matrix

    result = matrix.copy()

    for column_index in range(result.shape[1]):
        column = result[:, column_index]

        if np.all(np.isnan(column)):
            fill_value = 0.0
        else:
            fill_value = float(np.nanmedian(column))

        column[np.isnan(column)] = fill_value
        result[:, column_index] = column

    return result


def compute_playlist_profile_raw(
    playlist_rows: list[dict[str, Any]],
) -> dict[str, float | None]:
    profile: dict[str, float | None] = {}

    for feature_name in ["danceability", "energy", "valence", "acousticness"]:
        values = []

        for row in playlist_rows:
            parsed = safe_float(row.get(feature_name))
            if not np.isnan(parsed):
                values.append(parsed)

        profile[feature_name] = float(np.mean(values)) if values else None

    return profile


def compute_playlist_genre_stats(
    playlist_rows: list[dict[str, Any]],
) -> tuple[set[str], Counter[str], set[str]]:
    genre_counter: Counter[str] = Counter()

    for row in playlist_rows:
        for genre in normalize_terms(row["genre_names_list"]):
            genre_counter[genre] += 1

    playlist_genre_set = set(genre_counter.keys())
    top_playlist_genres = {genre for genre, _ in genre_counter.most_common(3)}

    return playlist_genre_set, genre_counter, top_playlist_genres


def build_match_reasons(
    row: dict[str, Any],
    playlist_profile_raw: dict[str, float | None],
    overlap: list[str],
    top_genre_matches: list[str],
    include_genres: list[str],
    has_preview: bool,
    has_cover: bool,
) -> list[str]:
    reasons: list[str] = []

    feature_labels = [
        ("danceability", "Danceability"),
        ("energy", "Energy"),
        ("valence", "Mood"),
        ("acousticness", "Acousticness"),
    ]

    for feature_name, label in feature_labels:
        actual = row.get(feature_name)
        target = playlist_profile_raw.get(feature_name)

        if actual is None or target is None:
            continue

        try:
            diff = abs(float(actual) - float(target))
        except (TypeError, ValueError):
            continue

        if diff <= 0.08:
            append_reason(reasons, f"{label} is very close to your playlist.")
        elif diff <= 0.16:
            append_reason(reasons, f"{label} is close to your playlist.")

        if len(reasons) >= 3:
            break

    if include_genres:
        append_reason(reasons, "Matches your included genres.")

    if overlap:
        append_reason(reasons, f"Shares genres like {', '.join(overlap[:2])}.")

    if top_genre_matches:
        append_reason(
            reasons,
            f"Matches top playlist genres like {', '.join(top_genre_matches[:2])}.",
        )

    if has_preview:
        append_reason(reasons, "Preview available.")

    if has_cover:
        append_reason(reasons, "Album cover available.")

    if not reasons:
        append_reason(reasons, "Similar overall profile to your playlist.")

    return reasons[:4]


def fetch_all_tracks(cursor) -> list[dict[str, Any]]:
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
            af.speechiness,
            af.instrumentalness,
            af.liveness,
            af.tempo,
            GROUP_CONCAT(DISTINCT a.name ORDER BY a.name SEPARATOR '||') AS artist_names,
            GROUP_CONCAT(DISTINCT g.name ORDER BY g.name SEPARATOR '||') AS genre_names
        FROM tracks t
        LEFT JOIN audio_features af ON af.track_id = t.id
        LEFT JOIN track_artists ta ON ta.track_id = t.id
        LEFT JOIN artists a ON a.id = ta.artist_id
        LEFT JOIN artist_genres ag ON ag.artist_id = a.id
        LEFT JOIN genres g ON g.id = ag.genre_id
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
            af.acousticness,
            af.speechiness,
            af.instrumentalness,
            af.liveness,
            af.tempo
        """
    )
    return list(cursor.fetchall())


def fetch_playlist_track_ids(cursor, playlist_name: str) -> set[int]:
    cursor.execute(
        """
        SELECT DISTINCT t.id
        FROM playlists p
        JOIN playlist_tracks pt ON pt.playlist_id = p.id
        JOIN tracks t ON t.id = pt.track_id
        WHERE p.name = %s
        """,
        (playlist_name,),
    )
    return {int(row["id"]) for row in cursor.fetchall()}


def override_playlist_vector_and_profile(
    playlist_vector: np.ndarray,
    playlist_profile_raw: dict[str, float | None],
    scaler: StandardScaler,
    filters: RecommendationFilterPayload,
) -> tuple[np.ndarray, dict[str, float | None]]:
    adjusted_vector = playlist_vector.copy()
    adjusted_profile = playlist_profile_raw.copy()

    for slider_name, feature_name in SLIDER_TO_FEATURE.items():
        slider_value = getattr(filters, slider_name)
        normalized_value = normalize_slider(slider_value)

        if normalized_value is None:
            continue

        feature_index = NUMERIC_FEATURES.index(feature_name)
        scaled_value = (
            (normalized_value - float(scaler.mean_[feature_index]))
            / float(scaler.scale_[feature_index])
        ) * NUMERIC_WEIGHTS[feature_name]

        adjusted_vector[feature_index] = scaled_value
        adjusted_profile[feature_name] = normalized_value

    return adjusted_vector, adjusted_profile


@router.post("/api/recommendations")
def get_recommendations(payload: RecommendationRequest):
    limit = max(1, min(payload.limit, 20))
    popularity_threshold = max(0, min(payload.filters.popularity, 100))
    include_genres = normalize_terms(payload.filters.includeGenres)
    exclude_genres = normalize_terms(payload.filters.excludeGenres)

    try:
        with pymysql.connect(**get_db_config()) as connection:
            with connection.cursor() as cursor:
                all_rows = fetch_all_tracks(cursor)
                playlist_track_ids = fetch_playlist_track_ids(
                    cursor,
                    payload.playlist_name,
                )

        if not playlist_track_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Playlist '{payload.playlist_name}' was not found or has no tracks.",
            )

        prepared_rows: list[dict[str, Any]] = []
        for row in all_rows:
            prepared_rows.append(
                {
                    **row,
                    "artist_names_list": split_grouped_values(row.get("artist_names")),
                    "genre_names_list": split_grouped_values(row.get("genre_names")),
                }
            )

        playlist_rows = [
            row for row in prepared_rows if int(row["id"]) in playlist_track_ids
        ]

        if not playlist_rows:
            raise HTTPException(
                status_code=404,
                detail=f"No imported tracks were found for playlist '{payload.playlist_name}'.",
            )

        numeric_matrix = np.array(
            [
                [safe_float(row.get(feature_name)) for feature_name in NUMERIC_FEATURES]
                for row in prepared_rows
            ],
            dtype=float,
        )

        numeric_matrix = fill_nan_with_column_median(numeric_matrix)

        scaler = StandardScaler()
        numeric_scaled = scaler.fit_transform(numeric_matrix)

        for feature_index, feature_name in enumerate(NUMERIC_FEATURES):
            numeric_scaled[:, feature_index] *= NUMERIC_WEIGHTS[feature_name]

        all_genres = [
            normalize_terms(row["genre_names_list"])
            for row in prepared_rows
        ]

        mlb = MultiLabelBinarizer()
        genre_matrix = mlb.fit_transform(all_genres).astype(float)

        if genre_matrix.size > 0:
            genre_matrix *= GENRE_MATRIX_WEIGHT
            feature_matrix = np.hstack([numeric_scaled, genre_matrix])
        else:
            feature_matrix = numeric_scaled

        row_index_by_track_id = {
            int(row["id"]): index for index, row in enumerate(prepared_rows)
        }

        playlist_indices = [
            row_index_by_track_id[int(row["id"])]
            for row in playlist_rows
            if int(row["id"]) in row_index_by_track_id
        ]

        playlist_vector = feature_matrix[playlist_indices].mean(axis=0)
        playlist_profile_raw = compute_playlist_profile_raw(playlist_rows)
        playlist_genre_set, playlist_genre_counter, top_playlist_genre_set = (
            compute_playlist_genre_stats(playlist_rows)
        )

        playlist_vector, playlist_profile_raw = override_playlist_vector_and_profile(
            playlist_vector,
            playlist_profile_raw,
            scaler,
            payload.filters,
        )

        candidate_indices: list[int] = []

        for index, row in enumerate(prepared_rows):
            if int(row["id"]) in playlist_track_ids:
                continue

            if int(row.get("popularity") or 0) < popularity_threshold:
                continue

            if not genre_matches(
                row["genre_names_list"],
                include_genres,
                exclude_genres,
            ):
                continue

            candidate_indices.append(index)

        if not candidate_indices:
            return {
                "count": 0,
                "items": [],
                "playlist_name": payload.playlist_name,
            }

        candidate_matrix = feature_matrix[candidate_indices]

        neighbor_count = min(
            len(candidate_indices),
            max(limit * 40, 200),
        )

        model = NearestNeighbors(metric="cosine")
        model.fit(candidate_matrix)

        distances, local_indices = model.kneighbors(
            playlist_vector.reshape(1, -1),
            n_neighbors=neighbor_count,
        )

        scored_candidates: list[dict[str, Any]] = []

        for distance, local_index in zip(
            distances[0].tolist(),
            local_indices[0].tolist(),
        ):
            global_index = candidate_indices[local_index]
            row = prepared_rows[global_index]

            track_name = row.get("track_name") or "Unknown track"
            duration_ms = row.get("duration_ms")
            popularity = int(row.get("popularity") or 0)
            preview_url = row.get("preview_url")
            cover_image_url = row.get("cover_image_url")

            has_preview = bool(preview_url)
            has_cover = bool(cover_image_url)

            genre_names = row["genre_names_list"]
            normalized_genres = normalize_terms(genre_names)

            overlap = sorted(set(normalized_genres) & playlist_genre_set)
            top_genre_matches = sorted(set(normalized_genres) & top_playlist_genre_set)

            adjusted_distance = float(distance)

            if has_preview:
                adjusted_distance -= 0.05

            if has_cover:
                adjusted_distance -= 0.02

            shared_genre_count = len(overlap)
            top_genre_count = len(top_genre_matches)

            adjusted_distance -= (
                min(shared_genre_count, MAX_SHARED_GENRE_BONUS_MATCHES)
                * SHARED_GENRE_BONUS_PER_MATCH
            )

            adjusted_distance -= (
                min(top_genre_count, MAX_TOP_GENRE_BONUS_MATCHES)
                * TOP_GENRE_BONUS_PER_MATCH
            )

            if playlist_genre_counter and shared_genre_count == 0:
                adjusted_distance += ZERO_GENRE_OVERLAP_PENALTY

            artist_name = (
                ", ".join(row["artist_names_list"])
                if row["artist_names_list"]
                else "Unknown Artist"
            )

            match_reasons = build_match_reasons(
                row=row,
                playlist_profile_raw=playlist_profile_raw,
                overlap=overlap,
                top_genre_matches=top_genre_matches,
                include_genres=include_genres,
                has_preview=has_preview,
                has_cover=has_cover,
            )

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
                    "matchReasons": match_reasons,
                    "_distance": adjusted_distance,
                    "_has_preview": has_preview,
                    "_has_cover": has_cover,
                    "_shared_genres": shared_genre_count,
                    "_top_genres": top_genre_count,
                }
            )

        scored_candidates.sort(
            key=lambda item: (
                0 if item["_has_preview"] else 1,
                0 if item["_has_cover"] else 1,
                -item["_top_genres"],
                -item["_shared_genres"],
                item["_distance"],
                -(item.get("popularity") or 0),
                item["title"].lower(),
            )
        )

        recommendations = []
        for index, item in enumerate(scored_candidates[:limit]):
            cleaned = {
                key: value
                for key, value in item.items()
                if key
                not in {
                    "_distance",
                    "_has_preview",
                    "_has_cover",
                    "_shared_genres",
                    "_top_genres",
                }
            }
            cleaned["palette"] = build_palette(index)
            recommendations.append(cleaned)

        return {
            "count": len(recommendations),
            "items": recommendations,
            "playlist_name": payload.playlist_name,
        }

    except HTTPException:
        raise
    except (OperationalError, InterfaceError):
        raise HTTPException(status_code=503, detail="Database is not reachable")
    except MySQLError as exc:
        raise HTTPException(status_code=500, detail=f"Database query failed: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {exc}")