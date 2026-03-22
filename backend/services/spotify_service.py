from __future__ import annotations

import os
import time
from base64 import b64encode
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class SpotifyService:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_BASE_URL = "https://api.spotify.com/v1"

    def __init__(self) -> None:
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET is missing in backend/.env"
            )

        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    def _basic_auth_header(self) -> str:
        raw = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        return f"Basic {b64encode(raw).decode('utf-8')}"

    def get_access_token(self) -> str:
        now = time.time()

        if self._access_token and now < self._token_expires_at:
            return self._access_token

        response = requests.post(
            self.TOKEN_URL,
            headers={
                "Authorization": self._basic_auth_header(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
            timeout=20,
        )
        response.raise_for_status()

        payload = response.json()
        self._access_token = payload["access_token"]

        expires_in = int(payload.get("expires_in", 3600))
        self._token_expires_at = now + max(expires_in - 60, 1)

        return self._access_token

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.get_access_token()}"}

    @staticmethod
    def extract_track_id(track_uri: str | None) -> str | None:
        if not track_uri:
            return None

        track_uri = track_uri.strip()

        if track_uri.startswith("spotify:track:"):
            return track_uri.split(":")[-1]

        if "open.spotify.com/track/" in track_uri:
            return track_uri.rstrip("/").split("/")[-1].split("?")[0]

        return track_uri

    @staticmethod
    def first_image_url(images: list[dict[str, Any]] | None) -> str | None:
        if not images:
            return None
        return images[0].get("url")

    def get_track(self, spotify_track_id: str, market: str | None = "CH") -> dict[str, Any]:
        params = {}
        if market:
            params["market"] = market

        response = requests.get(
            f"{self.API_BASE_URL}/tracks/{spotify_track_id}",
            headers=self._auth_headers(),
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def get_artist(self, spotify_artist_id: str) -> dict[str, Any]:
        response = requests.get(
            f"{self.API_BASE_URL}/artists/{spotify_artist_id}",
            headers=self._auth_headers(),
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def build_enrichment_from_track(self, track_data: dict[str, Any]) -> dict[str, Any]:
        album = track_data.get("album") or {}
        album_images = album.get("images") or []

        artist_payloads: list[dict[str, Any]] = []
        for simplified_artist in track_data.get("artists", []):
            spotify_artist_id = simplified_artist.get("id")
            image_url = None

            if spotify_artist_id:
                try:
                    full_artist = self.get_artist(spotify_artist_id)
                    image_url = self.first_image_url(full_artist.get("images"))
                except requests.RequestException:
                    image_url = None

            artist_payloads.append(
                {
                    "spotify_artist_id": spotify_artist_id,
                    "name": simplified_artist.get("name"),
                    "artist_name": simplified_artist.get("name"),
                    "spotify_url": (simplified_artist.get("external_urls") or {}).get("spotify"),
                    "image_url": image_url,
                }
            )

        return {
            "spotify_track_id": track_data.get("id"),
            "track_uri": track_data.get("uri"),
            "track_name": track_data.get("name"),
            "spotify_url": (track_data.get("external_urls") or {}).get("spotify"),
            "preview_url": track_data.get("preview_url"),
            "cover_image_url": self.first_image_url(album_images),
            "duration_ms": track_data.get("duration_ms"),
            "explicit": track_data.get("explicit"),
            "popularity": track_data.get("popularity"),
            "album": {
                "spotify_album_id": album.get("id"),
                "name": album.get("name"),
                "release_date": album.get("release_date"),
                "image_url": self.first_image_url(album_images),
                "spotify_url": (album.get("external_urls") or {}).get("spotify"),
            },
            "artists": artist_payloads,
        }

    def enrich_track_uri(self, track_uri: str | None) -> dict[str, Any] | None:
        spotify_track_id = self.extract_track_id(track_uri)
        if not spotify_track_id:
            return None

        track_data = self.get_track(spotify_track_id)
        return self.build_enrichment_from_track(track_data)

def get_spotify_access_token() -> str:
    service = SpotifyService()
    return service.get_access_token()


def extract_track_id(track_uri: str | None) -> str | None:
    return SpotifyService.extract_track_id(track_uri)


def get_spotify_track(spotify_track_id: str, market: str = "CH") -> dict[str, Any]:
    service = SpotifyService()
    return service.get_track(spotify_track_id, market)


def get_spotify_artist(spotify_artist_id: str) -> dict[str, Any]:
    service = SpotifyService()
    return service.get_artist(spotify_artist_id)


def build_enriched_payload(track_data: dict[str, Any]) -> dict[str, Any]:
    service = SpotifyService()
    return service.build_enrichment_from_track(track_data)


def enrich_track_uri(track_uri: str | None) -> dict[str, Any] | None:
    service = SpotifyService()
    return service.enrich_track_uri(track_uri)

def get_spotify_access_token() -> str:
    service = SpotifyService()
    return service.get_access_token()


def extract_track_id(track_uri: str | None) -> str | None:
    return SpotifyService.extract_track_id(track_uri)


def get_spotify_track(spotify_track_id: str, market: str = "CH") -> dict[str, Any]:
    service = SpotifyService()
    return service.get_track(spotify_track_id, market)


def get_spotify_artist(spotify_artist_id: str) -> dict[str, Any]:
    service = SpotifyService()
    return service.get_artist(spotify_artist_id)


def build_enriched_payload(track_data: dict[str, Any]) -> dict[str, Any]:
    service = SpotifyService()
    return service.build_enrichment_from_track(track_data)


def enrich_track_uri(track_uri: str | None) -> dict[str, Any] | None:
    service = SpotifyService()
    return service.enrich_track_uri(track_uri)
