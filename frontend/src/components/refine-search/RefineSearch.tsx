"use client";
import React from "react";
import useRefineSearchState from "@/hooks/useRefineSearchState";
import RefineSearchLayout from "./RefineSearchLayout";

export default function RefineSearch() {
  const { filters, setFilters, tracks, activeTrack, setActiveTrack } =
    useRefineSearchState();

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
