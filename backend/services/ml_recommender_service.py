from __future__ import annotations

from typing import Any

import numpy as np
import pymysql
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler

from db import get_db_config

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

EXPLAIN_FEATURES = [
    ("danceability", "Danceability"),
    ("energy", "Energy"),
    ("valence", "Mood"),
    ("acousticness", "Acousticness"),
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


def split_grouped_values(value: str | None) -> list[str]:
    if not value:
        return []

    seen: set[str] = set()
    items: list[str] = []

    for part in value.split("||"):
        cleaned = part.strip()
        normalized = cleaned.lower()

        if cleaned and normalized not in seen:
            seen.add(normalized)
            items.append(cleaned)

    return items


def normalize_terms(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values if value and value.strip()]


def genre_matches(
    track_genres: list[str],
    include_genres: list[str],
    exclude_genres: list[str],
) -> bool:
    normalized_track_genres = [genre.lower() for genre in track_genres]

    if include_genres:
        has_include_match = any(
            include_term in track_genre or track_genge_in_include(track_genre, include_term)
            for include_term in include_genres
            for track_genre in normalized_track_genres
        )
        if not has_include_match:
            return False

    if exclude_genres:
        has_exclude_match = any(
            exclude_term in track_genre or track_genge_in_include(track_genre, exclude_term)
            for exclude_term in exclude_genres
            for track_genre in normalized_track_genres
        )
        if has_exclude_match:
            return False

    return True


def track_genge_in_include(track_genre: str, term: str) -> bool:
    return track_genre in term


def append_reason(reasons: list[str], text: str) -> None:
    if text not in reasons:
        reasons.append(text)


def safe_float(value: Any) -> float:
    if value is None:
        return np.nan

    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def fill_nan_with_median(matrix: np.ndarray) -> np.ndarray:
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


def build_match_reasons(
    row: dict[str, Any],
    playlist_profile: dict[str, float],
    overlap: list[str],
) -> list[str]:
    reasons: list[str] = []

    for feature_name, label in EXPLAIN_FEATURES:
        actual = row.get(feature_name)
        target = playlist_profile.get(feature_name)

        if actual is None or target is None:
            continue

        diff = abs(float(actual) - float(target))

        if diff <= 0.08:
            append_reason(reasons, f"{label} is very close to your playlist.")
        elif diff <= 0.16:
            append_reason(reasons, f"{label} is close to your playlist.")

        if len(reasons) >= 3:
            break

    if overlap:
        append_reason(reasons, f"Shares genres like {', '.join(overlap[:2])}.")
    elif row.get("preview_url"):
        append_reason(reasons, "Preview available.")
    elif row.get("cover_image_url"):
        append_reason(reasons, "Album cover available.")

    if not reasons:
        append_reason(reasons, "Similar overall profile to your playlist.")

    return reasons[:4]


def fetch_corpus(cursor) -> list[dict[str, Any]]:
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


def recommend_from_playlist(
    playlist_name: str,
    limit: int,
    filters: dict[str, Any],
) -> dict[str, Any]:
    limit = max(1, min(limit, 20))
    include_genres = normalize_terms(filters.get("includeGenres", []))
    exclude_genres = normalize_terms(filters.get("excludeGenres", []))
    popularity_threshold = max(0, min(int(filters.get("popularity", 0) or 0), 100))

    with pymysql.connect(**get_db_config()) as connection:
        with connection.cursor() as cursor:
            rows = fetch_corpus(cursor)
            playlist_track_ids = fetch_playlist_track_ids(cursor, playlist_name)

    if not playlist_track_ids:
        raise ValueError(f"Playlist '{playlist_name}' was not found or has no tracks.")

    prepared_rows: list[dict[str, Any]] = []

    for row in rows:
        artist_names = split_grouped_values(row.get("artist_names"))
        genre_names = split_grouped_values(row.get("genre_names"))

        prepared_rows.append(
            {
                **row,
                "artist_names_list": artist_names,
                "genre_names_list": genre_names,
            }
        )

    playlist_rows = [row for row in prepared_rows if int(row["id"]) in playlist_track_ids]

    if not playlist_rows:
        raise ValueError(f"No playlist tracks found for '{playlist_name}'.")

    numeric_matrix = np.array(
        [
            [safe_float(row.get(feature_name)) for feature_name in NUMERIC_FEATURES]
            for row in prepared_rows
        ],
        dtype=float,
    )
    numeric_matrix = fill_nan_with_median(numeric_matrix)

    scaler = StandardScaler()
    numeric_scaled = scaler.fit_transform(numeric_matrix)

    all_genres = [normalize_terms(row["genre_names_list"]) for row in prepared_rows]
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(all_genres).astype(float)

    if genre_matrix.size > 0:
        genre_matrix *= 1.4
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

    playlist_profile = {
        feature_name: float(
            np.nanmean(
                [
                    safe_float(row.get(feature_name))
                    for row in playlist_rows
                ]
            )
        )
        for feature_name in EXPLAIN_FEATURES_MAP()
    }

    playlist_genre_set = {
        genre
        for row in playlist_rows
        for genre in normalize_terms(row["genre_names_list"])
    }

    candidate_indices: list[int] = []

    for index, row in enumerate(prepared_rows):
        if int(row["id"]) in playlist_track_ids:
            continue

        if int(row.get("popularity") or 0) < popularity_threshold:
            continue

        if not genre_matches(row["genre_names_list"], include_genres, exclude_genres):
            continue

        candidate_indices.append(index)

    if not candidate_indices:
        return {
            "count": 0,
            "items": [],
            "playlist_name": playlist_name,
        }

    candidate_matrix = feature_matrix[candidate_indices]

    neighbor_count = min(len(candidate_indices), max(limit * 30, 150))
    model = NearestNeighbors(metric="cosine")
    model.fit(candidate_matrix)

    distances, local_neighbor_indices = model.kneighbors(
        playlist_vector.reshape(1, -1),
        n_neighbors=neighbor_count,
    )

    ranked_candidates: list[dict[str, Any]] = []

    for distance, local_index in zip(
        distances[0].tolist(),
        local_neighbor_indices[0].tolist(),
    ):
        global_index = candidate_indices[local_index]
        row = prepared_rows[global_index]

        normalized_genres = normalize_terms(row["genre_names_list"])
        overlap = sorted(set(normalized_genres) & playlist_genre_set)

        has_preview = bool(row.get("preview_url"))
        has_cover = bool(row.get("cover_image_url"))

        adjusted_distance = float(distance)
        if has_preview:
            adjusted_distance -= 0.05
        if has_cover:
            adjusted_distance -= 0.02
        adjusted_distance -= min(len(overlap), 3) * 0.01

        ranked_candidates.append(
            {
                "id": int(row["id"]),
                "spotifyTrackId": row.get("spotify_track_id"),
                "title": row.get("track_name") or "Unknown track",
                "artist": ", ".join(row["artist_names_list"]) or "Unknown artist",
                "genres": row["genre_names_list"],
                "duration": format_duration(row.get("duration_ms")),
                "palette": build_palette(len(ranked_candidates)),
                "previewUrl": row.get("preview_url"),
                "coverImageUrl": row.get("cover_image_url"),
                "popularity": int(row.get("popularity") or 0),
                "matchReasons": build_match_reasons(row, playlist_profile, overlap),
                "_distance": adjusted_distance,
                "_has_preview": has_preview,
                "_has_cover": has_cover,
            }
        )

    ranked_candidates.sort(
        key=lambda item: (
            0 if item["_has_preview"] else 1,
            0 if item["_has_cover"] else 1,
            item["_distance"],
            -(item.get("popularity") or 0),
            item["title"].lower(),
        )
    )

    items = []
    for index, item in enumerate(ranked_candidates[:limit]):
        cleaned = {
            key: value
            for key, value in item.items()
            if not key.startswith("_")
        }
        cleaned["palette"] = build_palette(index)
        items.append(cleaned)

    return {
        "count": len(items),
        "items": items,
        "playlist_name": playlist_name,
    }


def EXPLAIN_FEATURES_MAP() -> list[str]:
    return [name for name, _ in EXPLAIN_FEATURES]