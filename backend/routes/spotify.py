from __future__ import annotations

from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Query

from services.spotify_service import get_spotify_access_token, get_spotify_track

router = APIRouter(prefix="/api/spotify", tags=["spotify"])


@router.get("/token-test")
def spotify_token_test() -> dict[str, str]:
    try:
        token = get_spotify_access_token()
        return {
            "status": "ok",
            "token_preview": f"{token[:12]}...",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Spotify token test failed: {exc}",
        )


@router.get("/tracks/{spotify_track_id}")
def spotify_track_by_id(
    spotify_track_id: str,
    market: str = Query(default="CH", min_length=2, max_length=2),
) -> dict[str, Any]:
    try:
        track = get_spotify_track(spotify_track_id, market)

        album = track.get("album") or {}
        artists = track.get("artists") or []

        return {
            "spotify_track_id": track.get("id"),
            "name": track.get("name"),
            "uri": track.get("uri"),
            "preview_url": track.get("preview_url"),
            "duration_ms": track.get("duration_ms"),
            "popularity": track.get("popularity"),
            "explicit": track.get("explicit"),
            "spotify_url": (track.get("external_urls") or {}).get("spotify"),
            "cover_image_url": (
                (album.get("images") or [{}])[0].get("url")
                if album.get("images")
                else None
            ),
            "album": {
                "id": album.get("id"),
                "name": album.get("name"),
                "release_date": album.get("release_date"),
            },
            "artists": [
                {
                    "id": artist.get("id"),
                    "name": artist.get("name"),
                    "spotify_url": (artist.get("external_urls") or {}).get("spotify"),
                }
                for artist in artists
            ],
            "raw": track,
        }

    except requests.HTTPError as exc:
        response = exc.response

        if response is not None:
            try:
                spotify_error = response.json()
            except ValueError:
                spotify_error = {"raw": response.text}

            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "message": "Spotify track request failed",
                    "spotify_status": response.status_code,
                    "spotify_error": spotify_error,
                    "spotify_track_id": spotify_track_id,
                    "market": market,
                },
            )

        raise HTTPException(
            status_code=502,
            detail=f"Spotify track request failed: {exc}",
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Spotify request error: {exc}",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Spotify error: {exc}",
        )