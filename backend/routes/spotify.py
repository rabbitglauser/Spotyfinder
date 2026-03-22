import requests
from fastapi import APIRouter, HTTPException

from services.spotify_service import SpotifyService

router = APIRouter()


@router.get("/api/spotify/token-test")
def spotify_token_test():
    try:
        service = SpotifyService()
        token = service.get_access_token()
        return {"status": "ok", "token_preview": token[:12] + "..."}
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Spotify token request failed")


@router.get("/api/spotify/tracks/{spotify_track_id}")
def spotify_track_by_id(spotify_track_id: str):
    try:
        service = SpotifyService()
        return service.get_track(spotify_track_id)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Spotify track request failed")