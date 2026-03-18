"use client";

import React, { useState } from "react";
import Link from "next/link";

export interface ToggleSliderValue {
  enabled: boolean;
  value: number;
}

export interface RecommendationFilters {
  includeGenres: string[];
  excludeGenres: string[];
  popularity: ToggleSliderValue;
  danceability: ToggleSliderValue;
  energy: ToggleSliderValue;
  mood: ToggleSliderValue;
  acoustic: ToggleSliderValue;
}

interface RecommendationLayoutProps {
  filters: RecommendationFilters;
  setFilters: React.Dispatch<React.SetStateAction<RecommendationFilters>>;
}

function BackgroundBlobs() {
  return (
    <>
      <style>
        {`
          @keyframes slowFloatOne {
            0% { transform: translate3d(0px, 0px, 0px) scale(1); }
            50% { transform: translate3d(25px, 18px, 0px) scale(1.06); }
            100% { transform: translate3d(0px, 0px, 0px) scale(1); }
          }

          @keyframes slowFloatTwo {
            0% { transform: translate3d(0px, 0px, 0px) scale(1); }
            50% { transform: translate3d(-30px, 24px, 0px) scale(0.95); }
            100% { transform: translate3d(0px, 0px, 0px) scale(1); }
          }
        `}
      </style>

      <div className="pointer-events-none absolute inset-0 overflow-hidden bg-black">
        <div
          className="absolute left-[-120px] top-[-80px] h-[420px] w-[420px] rounded-full bg-green-600/30 blur-3xl"
          style={{ animation: "slowFloatOne 18s ease-in-out infinite" }}
        />
        <div
          className="absolute left-[28%] top-[8%] h-[280px] w-[280px] rounded-full bg-green-500/20 blur-3xl"
          style={{ animation: "slowFloatTwo 22s ease-in-out infinite" }}
        />
        <div
          className="absolute bottom-[-120px] right-[-100px] h-[420px] w-[420px] rounded-full bg-green-500/35 blur-3xl"
          style={{ animation: "slowFloatOne 24s ease-in-out infinite" }}
        />
        <div
          className="absolute bottom-[10%] left-[35%] h-[260px] w-[260px] rounded-full bg-green-700/20 blur-3xl"
          style={{ animation: "slowFloatTwo 20s ease-in-out infinite" }}
        />
      </div>
    </>
  );
}

function addGenreToFront(list: string[], value: string) {
  const trimmed = value.trim();

  if (!trimmed) {
    return list;
  }

  const withoutDuplicate = list.filter(
    (item) => item.toLowerCase() !== trimmed.toLowerCase()
  );

  return [trimmed, ...withoutDuplicate];
}

function GenreInputField({
  title,
  placeholder,
  values,
  onAdd,
  onRemove,
}: {
  title: string;
  placeholder: string;
  values: string[];
  onAdd: (value: string) => void;
  onRemove: (value: string) => void;
}) {
  const [inputValue, setInputValue] = useState("");

  const submitValue = () => {
    const trimmed = inputValue.trim();

    if (!trimmed) return;

    onAdd(trimmed);
    setInputValue("");
  };

  return (
    <div>
      {/* GENREFIELD START */}
      <div className="mb-3 rounded-full bg-white/10 px-4 py-3 text-lg font-bold text-white/55">
        {title}
      </div>

      <div className="rounded-[24px] border border-white/10 bg-black/20 p-3">
        <input
          type="text"
          value={inputValue}
          placeholder={placeholder}
          onChange={(event) => setInputValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === ",") {
              event.preventDefault();
              submitValue();
            }
          }}
          className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none placeholder:text-white/30"
        />

        <div className="mt-3 flex flex-wrap gap-2">
          {values.map((genre) => (
            <button
              key={genre}
              type="button"
              onClick={() => onRemove(genre)}
              className="group inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/8 px-3 py-1.5 text-sm font-semibold text-white transition hover:border-red-400/40 hover:bg-red-500/10"
            >
              <span>{genre}</span>
              <span className="text-xs text-red-300 opacity-0 transition group-hover:opacity-100">
                ✕
              </span>
            </button>
          ))}
        </div>
      </div>
      {/* GENREFIELD END */}
    </div>
  );
}

function ToggleSlider({
  label,
  description,
  slider,
  onToggle,
  onChange,
}: {
  label: string;
  description: string;
  slider: ToggleSliderValue;
  onToggle: () => void;
  onChange: (value: number) => void;
}) {
  return (
    <div className="rounded-[22px] border border-white/10 bg-black/15 p-4">
      {/* SLIDERBLOCK START */}
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <div className="text-base font-bold text-white">{label}</div>
          <div className="text-xs text-white/45">{description}</div>
        </div>

        <button
          type="button"
          onClick={onToggle}
          className={`relative h-7 w-14 rounded-full transition ${
            slider.enabled ? "bg-green-500" : "bg-white/15"
          }`}
        >
          <span
            className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${
              slider.enabled ? "left-8" : "left-1"
            }`}
          />
        </button>
      </div>

      <div className={`${slider.enabled ? "opacity-100" : "opacity-35"}`}>
        <div className="mb-2 text-sm font-semibold text-white/60">
          Value: {slider.value}
        </div>

        <input
          type="range"
          min={0}
          max={100}
          step={1}
          value={slider.value}
          disabled={!slider.enabled}
          onChange={(event) => onChange(Number(event.target.value))}
          className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-[#19c819] disabled:cursor-not-allowed"
        />
      </div>
      {/* SLIDERBLOCK END */}
    </div>
  );
}

export default function RecommendationLayout({
  filters,
  setFilters,
}: RecommendationLayoutProps) {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#030303] text-white">
      <BackgroundBlobs />

      <div className="relative z-10 flex min-h-screen w-full flex-col px-6 py-8 md:px-10 lg:px-14">
        {/* HEADER START */}
        <div className="mb-8">
          <h1 className="text-5xl font-black tracking-tight text-[#19c819] sm:text-6xl md:text-7xl lg:text-8xl">
            Find your uniqueness
          </h1>
        </div>
        {/* HEADER END */}

        <div className="grid flex-1 gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          {/* UPLOADFIELD START */}
          <div className="flex min-h-[560px] items-center justify-center rounded-[32px] border-4 border-dashed border-white/20 bg-white/10 p-8 backdrop-blur-xl">
            <div className="space-y-6 text-center text-white/35">
              <div className="mx-auto flex h-28 w-28 items-center justify-center rounded-full border border-white/10 bg-white/5 text-6xl font-thin">
                ↑
              </div>

              <div>
                <p className="text-5xl font-black md:text-6xl">Upload...</p>
                <p className="mt-3 text-base text-white/45">
                  Later this can accept your exported playlist file.
                </p>
              </div>
            </div>
          </div>
          {/* UPLOADFIELD END */}

          {/* FILTERFIELD START */}
          <div className="flex h-full min-h-[560px] flex-col rounded-[32px] border border-white/10 bg-white/10 p-6 shadow-2xl backdrop-blur-xl md:p-8">
            <div className="space-y-5">
              <GenreInputField
                title="Include genres"
                placeholder="Type a genre and press Enter"
                values={filters.includeGenres}
                onAdd={(value) =>
                  setFilters((current) => ({
                    ...current,
                    includeGenres: addGenreToFront(current.includeGenres, value),
                  }))
                }
                onRemove={(value) =>
                  setFilters((current) => ({
                    ...current,
                    includeGenres: current.includeGenres.filter(
                      (item) => item !== value
                    ),
                  }))
                }
              />

              <GenreInputField
                title="Exclude genres"
                placeholder="Type a genre and press Enter"
                values={filters.excludeGenres}
                onAdd={(value) =>
                  setFilters((current) => ({
                    ...current,
                    excludeGenres: addGenreToFront(current.excludeGenres, value),
                  }))
                }
                onRemove={(value) =>
                  setFilters((current) => ({
                    ...current,
                    excludeGenres: current.excludeGenres.filter(
                      (item) => item !== value
                    ),
                  }))
                }
              />

              <ToggleSlider
                label="Popularity"
                description="How mainstream or well-known the artist/song should be"
                slider={filters.popularity}
                onToggle={() =>
                  setFilters((current) => ({
                    ...current,
                    popularity: {
                      ...current.popularity,
                      enabled: !current.popularity.enabled,
                    },
                  }))
                }
                onChange={(value) =>
                  setFilters((current) => ({
                    ...current,
                    popularity: {
                      ...current.popularity,
                      value,
                    },
                  }))
                }
              />

              <ToggleSlider
                label="Dance feel"
                description="How moveable or dance-friendly the song should feel"
                slider={filters.danceability}
                onToggle={() =>
                  setFilters((current) => ({
                    ...current,
                    danceability: {
                      ...current.danceability,
                      enabled: !current.danceability.enabled,
                    },
                  }))
                }
                onChange={(value) =>
                  setFilters((current) => ({
                    ...current,
                    danceability: {
                      ...current.danceability,
                      value,
                    },
                  }))
                }
              />

              <ToggleSlider
                label="Energy level"
                description="How intense, loud, or active the track should feel"
                slider={filters.energy}
                onToggle={() =>
                  setFilters((current) => ({
                    ...current,
                    energy: {
                      ...current.energy,
                      enabled: !current.energy.enabled,
                    },
                  }))
                }
                onChange={(value) =>
                  setFilters((current) => ({
                    ...current,
                    energy: {
                      ...current.energy,
                      value,
                    },
                  }))
                }
              />

              <ToggleSlider
                label="Mood"
                description="Lower is darker/sadder, higher is brighter/happier"
                slider={filters.mood}
                onToggle={() =>
                  setFilters((current) => ({
                    ...current,
                    mood: {
                      ...current.mood,
                      enabled: !current.mood.enabled,
                    },
                  }))
                }
                onChange={(value) =>
                  setFilters((current) => ({
                    ...current,
                    mood: {
                      ...current.mood,
                      value,
                    },
                  }))
                }
              />

              <ToggleSlider
                label="Acoustic feel"
                description="How organic, unplugged, or less synthetic it should sound"
                slider={filters.acoustic}
                onToggle={() =>
                  setFilters((current) => ({
                    ...current,
                    acoustic: {
                      ...current.acoustic,
                      enabled: !current.acoustic.enabled,
                    },
                  }))
                }
                onChange={(value) =>
                  setFilters((current) => ({
                    ...current,
                    acoustic: {
                      ...current.acoustic,
                      value,
                    },
                  }))
                }
              />
            </div>

            <div className="mt-auto flex justify-end pt-6">
              <Link
                href="/refine-search"
                className="rounded-full bg-gradient-to-r from-green-600 to-green-700 px-8 py-4 text-2xl font-black text-black shadow-lg shadow-green-700/30 transition hover:scale-[1.02]"
              >
                Find
              </Link>
            </div>
          </div>
          {/* FILTERFIELD END */}
        </div>
      </div>
    </div>
  );
}