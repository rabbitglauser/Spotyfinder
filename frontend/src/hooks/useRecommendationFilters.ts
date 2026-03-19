"use client";

import { useState } from "react";
import { RecommendationFilters } from "@/components/recommendation/RecommendationLayout";

const initialFilters: RecommendationFilters = {
  includeGenres: ["Rap", "Drill", "Chill"],
  excludeGenres: ["Gangster Rap", "Aggressive"],
  popularity: {
    enabled: true,
    value: 72,
  },
  danceability: {
    enabled: true,
    value: 64,
  },
  energy: {
    enabled: true,
    value: 58,
  },
  mood: {
    enabled: true,
    value: 48,
  },
  acoustic: {
    enabled: true,
    value: 22,
  },
};

export default function useRecommendationFilters() {
  return useState<RecommendationFilters>(initialFilters);
}
