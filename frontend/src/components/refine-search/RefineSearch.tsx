"use client";

import React, { useEffect } from "react";
import useRefineSearchState from "@/hooks/useRefineSearchState";
import RefineSearchLayout from "./RefineSearchLayout";

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

export default function RefineSearch() {
  const { filters, setFilters, tracks, activeTrack, setActiveTrack } =
    useRefineSearchState();

  useEffect(() => {
    const raw = localStorage.getItem("spotyfinder-refine-search");
    if (!raw) return;

    try {
      const parsed: StoredRefineSearchPayload = JSON.parse(raw);

      setFilters((current) => ({
        ...current,
        includeGenres: parsed.filters?.includeGenres ?? [],
        excludeGenres: parsed.filters?.excludeGenres ?? [],
        popularity: parsed.filters?.popularity ?? current.popularity,
      }));
    } catch (error) {
      console.error("Failed to load refine search state:", error);
    }
  }, [setFilters]);

  return (
    <RefineSearchLayout
      filters={filters}
      setFilters={setFilters}
      tracks={tracks}
      activeTrack={activeTrack}
      setActiveTrack={setActiveTrack}
    />
  );
}