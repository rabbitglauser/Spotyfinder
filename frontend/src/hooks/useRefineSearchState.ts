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
  followers: 0,
  monthlyListeners: 0,
  duration: "0:00",
  palette: {
    primary: "#1f2937",
    secondary: "#111827",
    accent: "#19c819",
    surface: "#030303",
  },
};

export default function useRefineSearchState() {
  const [playlistName, setPlaylistName] = useState("");
  const [filters, setFilters] = useState<RefineSearchFilters>({
    includeGenres: [],
    excludeGenres: [],
    popularity: 50,
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
        popularity: parsed.filters?.popularity ?? 50,
      });
    } catch (loadError) {
      console.error("Failed to read refine search payload:", loadError);
      setError("Failed to load refine search settings.");
    }
  }, []);

  useEffect(() => {
    if (!playlistName) return;

    let isCancelled = false;

    const loadRecommendations = async () => {
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
    };

    loadRecommendations();

    return () => {
      isCancelled = true;
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