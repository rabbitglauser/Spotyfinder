import base64
import os
import time

import requests
from fastapi import HTTPException

_spotify_token_cache = {
    "access_token": None,
    "expires_at": 0,
}


def get_spotify_client_id():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="SPOTIFY_CLIENT_ID is missing in backend/.env",
        )
    return client_id


def get_spotify_client_secret():
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_secret:
        raise HTTPException(
            status_code=500,
            detail="SPOTIFY_CLIENT_SECRET is missing in backend/.env",
        )
    return client_secret


def get_spotify_access_token():
    now = time.time()

    if (
        _spotify_token_cache["access_token"]
        and now < _spotify_token_cache["expires_at"]
    ):
        return _spotify_token_cache["access_token"]

    client_id = get_spotify_client_id()
    client_secret = get_spotify_client_secret()

    raw = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = "Basic " + base64.b64encode(raw).decode("utf-8")

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=20,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Spotify token request failed: {response.text}",
        )

    payload = response.json()
    access_token = payload["access_token"]
    expires_in = int(payload.get("expires_in", 3600))

    _spotify_token_cache["access_token"] = access_token
    _spotify_token_cache["expires_at"] = now + max(expires_in - 60, 1)

    return access_token


def extract_track_id(track_uri: str | None):
    if not track_uri:
        return None

    track_uri = track_uri.strip()

    if track_uri.startswith("spotify:track:"):
        return track_uri.split(":")[-1]

    if "open.spotify.com/track/" in track_uri:
        return track_uri.rstrip("/").split("/")[-1].split("?")[0]

    return track_uri


def get_spotify_track(spotify_track_id: str, market: str = "CH"):
    token = get_spotify_access_token()

    response = requests.get(
        f"https://api.spotify.com/v1/tracks/{spotify_track_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"market": market},
        timeout=20,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Spotify track request failed: {response.text}",
        )

    return response.json()


def get_spotify_artist(spotify_artist_id: str):
    token = get_spotify_access_token()

    response = requests.get(
        f"https://api.spotify.com/v1/artists/{spotify_artist_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )

    if response.status_code != 200:
        return None

    return response.json()


def get_first_image_url(images):
    if not images:
        return None
    return images[0].get("url")


def build_enriched_payload(track_uri):
    spotify_track_id = extract_track_id(track_uri)
    if not spotify_track_id:
        return None

    track_data = get_spotify_track(spotify_track_id)
    album = track_data.get("album") or {}
    album_images = album.get("images") or []

    artists_payload = []
    for simplified_artist in track_data.get("artists", []):
        spotify_artist_id = simplified_artist.get("id")
        image_url = None

        if spotify_artist_id:
            artist_data = get_spotify_artist(spotify_artist_id)
            if artist_data:
                image_url = get_first_image_url(artist_data.get("images"))

        artists_payload.append(
            {
                "spotify_artist_id": spotify_artist_id,
                "name": simplified_artist.get("name"),
                "artist_name": simplified_artist.get("name"),
                "image_url": image_url,
            }
        )

    return {
        "spotify_track_id": track_data.get("id"),
        "track_uri": track_data.get("uri"),
        "track_name": track_data.get("name"),
        "spotify_url": (track_data.get("external_urls") or {}).get("spotify"),
        "preview_url": track_data.get("preview_url"),
        "cover_image_url": get_first_image_url(album_images),
        "duration_ms": track_data.get("duration_ms"),
        "explicit": track_data.get("explicit"),
        "popularity": track_data.get("popularity"),
        "album": {
            "spotify_album_id": album.get("id"),
            "name": album.get("name"),
            "release_date": album.get("release_date"),
            "image_url": get_first_image_url(album_images),
        },
        "artists": artists_payload,
    }