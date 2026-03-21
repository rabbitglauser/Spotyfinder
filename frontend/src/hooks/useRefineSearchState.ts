"use client";

import { useState } from "react";

type RefineSearchFilters = {
  includeGenres: string[];
  excludeGenres: string[];
  popularity: number;
};

type TrackPalette = {
  primary: string;
  secondary: string;
  accent: string;
  surface: string;
};

type RefineSearchTrack = {
  id: number;
  title: string;
  artist: string;
  genres: string[];
  followers: number;
  monthlyListeners: number;
  duration: string;
  palette: TrackPalette;
};

const mockTracks: RefineSearchTrack[] = [
  {
    id: 1,
    title: "Afterglow",
    artist: "The Midnight Youth",
    genres: ["synthpop", "indie pop", "dreamwave"],
    followers: 248000,
    monthlyListeners: 1300000,
    duration: "3:42",
    palette: {
      primary: "#2A9D8F",
      secondary: "#1D3557",
      accent: "#52E3C2",
      surface: "#101820",
    },
  },
  {
    id: 2,
    title: "Velvet Noise",
    artist: "Neon Harbor",
    genres: ["alt pop", "electropop", "night drive"],
    followers: 512000,
    monthlyListeners: 2800000,
    duration: "4:01",
    palette: {
      primary: "#7B2CBF",
      secondary: "#240046",
      accent: "#C77DFF",
      surface: "#140A1F",
    },
  },
  {
    id: 3,
    title: "Static Hearts",
    artist: "Glass Avenue",
    genres: ["indie rock", "modern rock", "alt"],
    followers: 384000,
    monthlyListeners: 1900000,
    duration: "3:27",
    palette: {
      primary: "#E76F51",
      secondary: "#5F0F40",
      accent: "#FF9F6E",
      surface: "#1A1013",
    },
  },
  {
    id: 4,
    title: "Blue Motion",
    artist: "Arctic Echo",
    genres: ["ambient pop", "chillwave", "electronic"],
    followers: 146000,
    monthlyListeners: 860000,
    duration: "4:18",
    palette: {
      primary: "#3A86FF",
      secondary: "#1B263B",
      accent: "#7CC6FE",
      surface: "#0F1722",
    },
  },
];

export default function useRefineSearchState() {
  const [filters, setFilters] = useState<RefineSearchFilters>({
    includeGenres: [],
    excludeGenres: [],
    popularity: 50,
  });

  const [tracks] = useState<RefineSearchTrack[]>(mockTracks);
  const [activeTrack, setActiveTrack] = useState<RefineSearchTrack>(
    mockTracks[0]
  );

  return {
    filters,
    setFilters,
    tracks,
    activeTrack,
    setActiveTrack,
  };
}