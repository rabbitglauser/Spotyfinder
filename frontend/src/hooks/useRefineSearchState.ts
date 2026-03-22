"use client";

import { useEffect, useState } from "react";
import {
  RefineSearchFilters,
  RefineSearchTrack,
} from "@/components/refine-search/RefineSearchLayout";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type StoredRefineSearchPayload = {
  playlistName: string;
  enrichWithSpotify: boolean;
  filters?: {
    includeGenres?: string[];
    excludeGenres?: string[];
    popularity?: number;
    danceability?: number | null;
    energy?: number | null;
    mood?: number | null;
    acoustic?: number | null;
  };
};

type RecommendationApiResponse = {
  count?: number;
  items?: RefineSearchTrack[];
  playlist_name?: string;
  detail?: string;
};

const emptyTrack: RefineSearchTrack = {
  id: 0,
  title: "No track selected",
  artist: "Spotyfinder",
  genres: [],
  duration: "0:00",
  palette: {
    primary: "#1f2937",
    secondary: "#111827",
    accent: "#19c819",
    surface: "#030303",
  },
  previewUrl: null,
  coverImageUrl: null,
  popularity: 0,
  matchReasons: ["No recommendation selected yet."],
};

export default function useRefineSearchState() {
  const [playlistName, setPlaylistName] = useState("");
  const [filters, setFilters] = useState<RefineSearchFilters>({
    includeGenres: [],
    excludeGenres: [],
    popularity: 0,
    danceability: null,
    energy: null,
    mood: null,
    acoustic: null,
  });

  const [tracks, setTracks] = useState<RefineSearchTrack[]>([]);
  const [activeTrack, setActiveTrack] = useState<RefineSearchTrack>(emptyTrack);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("spotyfinder-refine-search");
    if (!raw) return;

    try {
      const parsed: StoredRefineSearchPayload = JSON.parse(raw);

      setPlaylistName(parsed.playlistName ?? "");

      setFilters({
        includeGenres: parsed.filters?.includeGenres ?? [],
        excludeGenres: parsed.filters?.excludeGenres ?? [],
        popularity: parsed.filters?.popularity ?? 0,
        danceability:
          typeof parsed.filters?.danceability === "number"
            ? parsed.filters.danceability
            : null,
        energy:
          typeof parsed.filters?.energy === "number"
            ? parsed.filters.energy
            : null,
        mood:
          typeof parsed.filters?.mood === "number"
            ? parsed.filters.mood
            : null,
        acoustic:
          typeof parsed.filters?.acoustic === "number"
            ? parsed.filters.acoustic
            : null,
      });
    } catch (loadError) {
      console.error("Failed to read refine search payload:", loadError);
      setError("Failed to load refine search settings.");
    }
  }, []);

  useEffect(() => {
    if (!playlistName) return;

    let isCancelled = false;

    const timeoutId = window.setTimeout(async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/api/recommendations`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            playlist_name: playlistName,
            limit: 8,
            filters: {
              includeGenres: filters.includeGenres,
              excludeGenres: filters.excludeGenres,
              popularity: filters.popularity,
              danceability: filters.danceability,
              energy: filters.energy,
              mood: filters.mood,
              acoustic: filters.acoustic,
            },
          }),
        });

        const data: RecommendationApiResponse = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Failed to load recommendations.");
        }

        const nextTracks = Array.isArray(data.items) ? data.items : [];

        if (isCancelled) return;

        setTracks(nextTracks);
        setActiveTrack((current) => {
          const stillExists = nextTracks.find((track) => track.id === current.id);
          return stillExists ?? nextTracks[0] ?? emptyTrack;
        });
      } catch (requestError) {
        if (isCancelled) return;

        const message =
          requestError instanceof Error
            ? requestError.message
            : "Failed to load recommendations.";

        setError(message);
        setTracks([]);
        setActiveTrack(emptyTrack);
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }, 400);

    return () => {
      isCancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [playlistName, filters]);

  return {
    filters,
    setFilters,
    tracks,
    activeTrack,
    setActiveTrack,
    isLoading,
    error,
  };
}