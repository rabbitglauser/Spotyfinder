"use client";

import { useState } from "react";
import {
  RefineSearchFilters,
  RefineSearchTrack,
} from "@/components/refine-search/RefineSearchLayout";

const initialFilters: RefineSearchFilters = {
  includeGenres: ["Rap", "Drill", "Chill"],
  excludeGenres: ["Gangster Rap", "Aggressive"],
  popularity: 72,
};

const tracks: RefineSearchTrack[] = [
  {
    id: 1,
    title: "Fever",
    artist: "Buckshot, fakemink",
    genres: ["Rap", "Chill"],
    followers: 109549,
    monthlyListeners: 2323023,
    duration: "3:06",
    palette: {
      primary: "#8B2E74",
      secondary: "#D17A62",
      accent: "#D94CE1",
      surface: "#271224",
    },
  },
  {
    id: 2,
    title: "Under Your Spell",
    artist: "Snow Strippers",
    genres: ["Alt Pop", "Chill"],
    followers: 48611,
    monthlyListeners: 1370000,
    duration: "2:58",
    palette: {
      primary: "#2E4778",
      secondary: "#8EA7D8",
      accent: "#5FC5FF",
      surface: "#131D31",
    },
  },
  {
    id: 3,
    title: "Money Trees",
    artist: "Kendrick Lamar, Jay Rock",
    genres: ["Rap", "West Coast"],
    followers: 14411000,
    monthlyListeners: 55500000,
    duration: "6:26",
    palette: {
      primary: "#687540",
      secondary: "#D2B27A",
      accent: "#B1D454",
      surface: "#202414",
    },
  },
  {
    id: 4,
    title: "Track 10",
    artist: "Charli xcx",
    genres: ["Hyperpop", "Alt Pop"],
    followers: 3660000,
    monthlyListeners: 22100000,
    duration: "3:54",
    palette: {
      primary: "#B24372",
      secondary: "#FFB1D0",
      accent: "#FF66A3",
      surface: "#2A1520",
    },
  },
];

export default function useRefineSearchState() {
  const [filters, setFilters] = useState<RefineSearchFilters>(initialFilters);
  const [activeTrack, setActiveTrack] = useState<RefineSearchTrack>(tracks[0]);

  return { filters, setFilters, tracks, activeTrack, setActiveTrack };
}
