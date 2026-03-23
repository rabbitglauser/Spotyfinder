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
        self._artist_cache: dict[str, dict[str, Any]] = {}

    def _basic_auth_header(self) -> str:
        raw = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        return f"Basic {b64encode(raw).decode('utf-8')}"

    def _sleep_for_rate_limit(
        self,
        response: requests.Response | None,
        attempt: int,
    ) -> None:
        retry_after_header = response.headers.get("Retry-After") if response else None

        try:
            retry_after_seconds = (
                float(retry_after_header) if retry_after_header else None
            )
        except (TypeError, ValueError):
            retry_after_seconds = None

        if retry_after_seconds is None:
            retry_after_seconds = min(1.5 * (attempt + 1), 5)

        time.sleep(max(retry_after_seconds, 0.8))

    def get_access_token(self) -> str:
        now = time.time()

        if self._access_token and now < self._token_expires_at:
            return self._access_token

        last_response: requests.Response | None = None

        for attempt in range(3):
            response = requests.post(
                self.TOKEN_URL,
                headers={
                    "Authorization": self._basic_auth_header(),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "client_credentials"},
                timeout=20,
            )

            last_response = response

            if response.status_code == 429:
                self._sleep_for_rate_limit(response, attempt)
                continue

            response.raise_for_status()

            payload = response.json()
            self._access_token = payload["access_token"]

            expires_in = int(payload.get("expires_in", 3600))
            self._token_expires_at = now + max(expires_in - 60, 1)

            return self._access_token

        if last_response is not None:
            last_response.raise_for_status()

        raise RuntimeError("Failed to retrieve Spotify access token")

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.get_access_token()}"}

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int = 20,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        last_response: requests.Response | None = None

        for attempt in range(max_retries):
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                data=data,
                timeout=timeout,
            )

            last_response = response

            if response.status_code == 429:
                self._sleep_for_rate_limit(response, attempt)
                continue

            response.raise_for_status()

            if not response.content:
                return {}

            return response.json()

        if last_response is not None:
            last_response.raise_for_status()

        raise RuntimeError(f"Spotify request failed after {max_retries} retries")

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

    def get_track(
        self,
        spotify_track_id: str,
        market: str | None = "CH",
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if market:
            params["market"] = market

        return self._request_json(
            "GET",
            f"{self.API_BASE_URL}/tracks/{spotify_track_id}",
            headers=self._auth_headers(),
            params=params,
            timeout=20,
            max_retries=3,
        )

    def _get_tracks_bulk_chunk(
        self,
        chunk: list[str],
        market: str | None = "CH",
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {"ids": ",".join(chunk)}
        if market:
            params["market"] = market

        payload = self._request_json(
            "GET",
            f"{self.API_BASE_URL}/tracks",
            headers=self._auth_headers(),
            params=params,
            timeout=20,
            max_retries=3,
        )

        tracks = payload.get("tracks") or []
        return [track for track in tracks if track]

    def _get_tracks_individually(
        self,
        chunk: list[str],
        market: str | None = "CH",
    ) -> list[dict[str, Any]]:
        collected_tracks: list[dict[str, Any]] = []

        for track_id in chunk:
            try:
                track_data = self.get_track(track_id, market=market)
                if track_data:
                    collected_tracks.append(track_data)
            except requests.HTTPError as exc:
                response = exc.response
                status_code = response.status_code if response is not None else None

                if status_code in {400, 403, 404}:
                    print(
                        f"SPOTIFY SINGLE TRACK SKIPPED: {track_id} "
                        f"(status={status_code})"
                    )
                    continue

                raise
            except requests.RequestException as exc:
                print(f"SPOTIFY SINGLE TRACK FAILED: {track_id} ({exc})")
                continue

            time.sleep(0.05)

        return collected_tracks

    def get_tracks(
        self,
        spotify_track_ids: list[str],
        market: str | None = "CH",
    ) -> list[dict[str, Any]]:
        unique_ids: list[str] = []
        seen: set[str] = set()

        for value in spotify_track_ids:
            track_id = self.extract_track_id(value)
            if not track_id or track_id in seen:
                continue
            seen.add(track_id)
            unique_ids.append(track_id)

        if not unique_ids:
            return []

        all_tracks: list[dict[str, Any]] = []

        for start_index in range(0, len(unique_ids), 50):
            chunk = unique_ids[start_index : start_index + 50]

            try:
                chunk_tracks = self._get_tracks_bulk_chunk(chunk, market=market)
                print(
                    f"SPOTIFY BULK CHUNK OK: fetched {len(chunk_tracks)} "
                    f"tracks for chunk size {len(chunk)}"
                )
                all_tracks.extend(chunk_tracks)

            except requests.HTTPError as exc:
                response = exc.response
                status_code = response.status_code if response is not None else None

                if status_code == 403:
                    print(
                        f"SPOTIFY BULK CHUNK FORBIDDEN, falling back to single "
                        f"track requests for chunk size {len(chunk)}"
                    )
                    fallback_tracks = self._get_tracks_individually(
                        chunk,
                        market=market,
                    )
                    print(
                        f"SPOTIFY SINGLE TRACK FALLBACK OK: fetched "
                        f"{len(fallback_tracks)} tracks"
                    )
                    all_tracks.extend(fallback_tracks)
                    continue

                raise

        return all_tracks

    def get_artist(self, spotify_artist_id: str) -> dict[str, Any]:
        if spotify_artist_id in self._artist_cache:
            return self._artist_cache[spotify_artist_id]

        artist_data = self._request_json(
            "GET",
            f"{self.API_BASE_URL}/artists/{spotify_artist_id}",
            headers=self._auth_headers(),
            timeout=20,
            max_retries=3,
        )
        self._artist_cache[spotify_artist_id] = artist_data
        return artist_data

    def build_enrichment_from_track(
        self,
        track_data: dict[str, Any],
        include_artist_details: bool = False,
    ) -> dict[str, Any]:
        album = track_data.get("album") or {}
        album_images = album.get("images") or []

        artist_payloads: list[dict[str, Any]] = []
        for simplified_artist in track_data.get("artists", []):
            spotify_artist_id = simplified_artist.get("id")
            image_url = None

            if include_artist_details and spotify_artist_id:
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
                    "spotify_url": (
                        simplified_artist.get("external_urls") or {}
                    ).get("spotify"),
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

    def enrich_track_uri(
        self,
        track_uri: str | None,
        include_artist_details: bool = False,
    ) -> dict[str, Any] | None:
        spotify_track_id = self.extract_track_id(track_uri)
        if not spotify_track_id:
            return None

        track_data = self.get_track(spotify_track_id, market="CH")
        return self.build_enrichment_from_track(
            track_data,
            include_artist_details=include_artist_details,
        )

    def enrich_track_uris(
        self,
        track_uris: list[str | None],
        include_artist_details: bool = False,
        market: str = "CH",
    ) -> dict[str, dict[str, Any]]:
        track_ids: list[str] = []
        seen: set[str] = set()

        for track_uri in track_uris:
            track_id = self.extract_track_id(track_uri)
            if not track_id or track_id in seen:
                continue
            seen.add(track_id)
            track_ids.append(track_id)

        if not track_ids:
            return {}

        track_payloads = self.get_tracks(track_ids, market=market)
        enrichment_by_track_id: dict[str, dict[str, Any]] = {}

        for track_data in track_payloads:
            enrichment = self.build_enrichment_from_track(
                track_data,
                include_artist_details=include_artist_details,
            )
            spotify_track_id = enrichment.get("spotify_track_id")
            if spotify_track_id:
                enrichment_by_track_id[spotify_track_id] = enrichment

        return enrichment_by_track_id


def extract_track_id(track_uri: str | None) -> str | None:
    return SpotifyService.extract_track_id(track_uri)


def get_spotify_access_token() -> str:
    service = SpotifyService()
    return service.get_access_token()


def get_spotify_track(spotify_track_id: str, market: str = "CH") -> dict[str, Any]:
    service = SpotifyService()
    return service.get_track(spotify_track_id, market)


def get_spotify_tracks(
    spotify_track_ids: list[str],
    market: str = "CH",
) -> list[dict[str, Any]]:
    service = SpotifyService()
    return service.get_tracks(spotify_track_ids, market)


def get_spotify_artist(spotify_artist_id: str) -> dict[str, Any]:
    service = SpotifyService()
    return service.get_artist(spotify_artist_id)


def build_enriched_payload(
    track_data: dict[str, Any],
    include_artist_details: bool = False,
) -> dict[str, Any]:
    service = SpotifyService()
    return service.build_enrichment_from_track(
        track_data,
        include_artist_details=include_artist_details,
    )


def enrich_track_uri(
    track_uri: str | None,
    include_artist_details: bool = False,
) -> dict[str, Any] | None:
    service = SpotifyService()
    return service.enrich_track_uri(
        track_uri,
        include_artist_details=include_artist_details,
    )


def enrich_track_uris(
    track_uris: list[str | None],
    include_artist_details: bool = False,
    market: str = "CH",
) -> dict[str, dict[str, Any]]:
    service = SpotifyService()
    return service.enrich_track_uris(
        track_uris,
        include_artist_details=include_artist_details,
        market=market,
    )