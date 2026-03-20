from fastapi import APIRouter

from services.spotify_service import get_spotify_access_token, get_spotify_track

router = APIRouter()


@router.get("/api/spotify/token-test")
def spotify_token_test():
    token = get_spotify_access_token()
    return {"status": "ok", "token_preview": token[:12] + "..."}


@router.get("/api/spotify/tracks/{spotify_track_id}")
def spotify_track_by_id(spotify_track_id: str):
    return get_spotify_track(spotify_track_id)