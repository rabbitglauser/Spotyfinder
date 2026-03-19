"use client";

import React from "react";
import useRecommendationFilters from "@/hooks/useRecommendationFilters";
import RecommendationLayout from "./RecommendationLayout";

export default function Recommendation() {
  const [filters, setFilters] = useRecommendationFilters();

  return (
    <RecommendationLayout
      filters={filters}
      setFilters={setFilters}
    />
  );
}
