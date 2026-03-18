"use client";

import React, { useState } from "react";
import RecommendationLayout, {
  RecommendationFilters,
} from "./recommendation_layout";

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

export default function Recommendation() {
  const [filters, setFilters] =
    useState<RecommendationFilters>(initialFilters);

  return (
    <RecommendationLayout
      filters={filters}
      setFilters={setFilters}
    />
  );
}