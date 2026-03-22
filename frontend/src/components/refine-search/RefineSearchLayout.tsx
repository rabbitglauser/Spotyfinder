"use client";

import React from "react";

export interface RefineSearchFilters {
  includeGenres: string[];
  excludeGenres: string[];
  popularity: number;
  danceability: number | null;
  energy: number | null;
  mood: number | null;
  acoustic: number | null;
}

export interface TrackPalette {
  primary: string;
  secondary: string;
  accent: string;
  surface: string;
}

export interface RefineSearchTrack {
  id: number;
  title: string;
  artist: string;
  genres: string[];
  duration: string;
  palette: TrackPalette;
  previewUrl?: string | null;
  coverImageUrl?: string | null;
  popularity?: number;
  matchReasons?: string[];
}

interface RefineSearchLayoutProps {
  filters: RefineSearchFilters;
  setFilters: React.Dispatch<React.SetStateAction<RefineSearchFilters>>;
  tracks: RefineSearchTrack[];
  activeTrack: RefineSearchTrack;
  setActiveTrack: React.Dispatch<React.SetStateAction<RefineSearchTrack>>;
  isLoading: boolean;
  error: string | null;
}

function hexToRgba(hex: string, alpha: number) {
  const cleaned = hex.replace("#", "");
  const bigint = parseInt(cleaned, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function BackgroundBlobs({ accent }: { accent: string }) {
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
          className="absolute left-[-120px] top-[-80px] h-[420px] w-[420px] rounded-full bg-green-600/25 blur-3xl"
          style={{ animation: "slowFloatOne 18s ease-in-out infinite" }}
        />
        <div
          className="absolute left-[28%] top-[8%] h-[280px] w-[280px] rounded-full bg-green-500/15 blur-3xl"
          style={{ animation: "slowFloatTwo 22s ease-in-out infinite" }}
        />
        <div
          className="absolute bottom-[-120px] right-[-100px] h-[420px] w-[420px] rounded-full blur-3xl"
          style={{
            backgroundColor: hexToRgba(accent, 0.28),
            animation: "slowFloatOne 24s ease-in-out infinite",
          }}
        />
        <div
          className="absolute bottom-[10%] left-[35%] h-[260px] w-[260px] rounded-full bg-green-700/18 blur-3xl"
          style={{ animation: "slowFloatTwo 20s ease-in-out infinite" }}
        />
      </div>
    </>
  );
}

function FilterSlider({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div>
      <div className="mb-2 text-sm font-bold text-white/55">
        {label}: {value}/100
      </div>
      <input
        type="range"
        min={0}
        max={100}
        step={1}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10"
      />
    </div>
  );
}

function OptionalSlider({
  label,
  value,
  onToggle,
  onChange,
}: {
  label: string;
  value: number | null;
  onToggle: () => void;
  onChange: (value: number) => void;
}) {
  const enabled = value !== null;
  const sliderValue = value ?? 50;

  return (
    <div className="rounded-[22px] border border-white/10 bg-black/15 p-4">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <div className="text-base font-bold text-white">{label}</div>
          <div className="text-xs text-white/45">
            {enabled ? `Value: ${sliderValue}/100` : "Disabled"}
          </div>
        </div>

        <button
          type="button"
          onClick={onToggle}
          className={`relative h-7 w-14 rounded-full transition ${
            enabled ? "bg-green-500" : "bg-white/15"
          }`}
        >
          <span
            className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${
              enabled ? "left-8" : "left-1"
            }`}
          />
        </button>
      </div>

      <input
        type="range"
        min={0}
        max={100}
        step={1}
        value={sliderValue}
        disabled={!enabled}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
      />
    </div>
  );
}

export default function RefineSearchLayout({
  filters,
  setFilters,
  tracks,
  activeTrack,
  setActiveTrack,
  isLoading,
  error,
}: RefineSearchLayoutProps) {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#030303] text-white">
      <BackgroundBlobs accent={activeTrack.palette.accent} />

      <div className="relative z-10 flex min-h-screen w-full flex-col px-6 py-8 md:px-10 lg:px-14">
        <div className="mb-8">
          <h1 className="text-5xl font-black tracking-tight text-[#19c819] sm:text-6xl md:text-7xl lg:text-8xl">
            Refine your Search
          </h1>
        </div>

        <div className="grid flex-1 gap-8 xl:grid-cols-[0.95fr_1.1fr]">
          <div className="flex h-full flex-col gap-6">
            <div className="rounded-[32px] border border-white/10 bg-white/10 p-6 shadow-2xl backdrop-blur-xl">
              <div className="space-y-5">
                <div>
                  <div className="mb-3 rounded-full bg-white/10 px-4 py-2 text-lg font-bold text-white/45">
                    Include Genres ....
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {filters.includeGenres.map((genre) => (
                      <span
                        key={genre}
                        className="rounded-full border border-white/10 bg-white/10 px-3 py-1.5 text-sm font-semibold text-white/75"
                      >
                        {genre}
                      </span>
                    ))}
                    {filters.includeGenres.length === 0 && (
                      <span className="text-sm text-white/40">No include genres</span>
                    )}
                  </div>
                </div>

                <div>
                  <div className="mb-3 rounded-full bg-white/10 px-4 py-2 text-lg font-bold text-white/45">
                    Exclude Genres ....
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {filters.excludeGenres.map((genre) => (
                      <span
                        key={genre}
                        className="rounded-full border border-white/10 bg-white/10 px-3 py-1.5 text-sm font-semibold text-white/75"
                      >
                        {genre}
                      </span>
                    ))}
                    {filters.excludeGenres.length === 0 && (
                      <span className="text-sm text-white/40">No exclude genres</span>
                    )}
                  </div>
                </div>

                <FilterSlider
                  label="Popularity"
                  value={filters.popularity}
                  onChange={(value) =>
                    setFilters((current) => ({
                      ...current,
                      popularity: value,
                    }))
                  }
                />

                <OptionalSlider
                  label="Danceability"
                  value={filters.danceability}
                  onToggle={() =>
                    setFilters((current) => ({
                      ...current,
                      danceability:
                        current.danceability === null ? 50 : null,
                    }))
                  }
                  onChange={(value) =>
                    setFilters((current) => ({
                      ...current,
                      danceability: value,
                    }))
                  }
                />

                <OptionalSlider
                  label="Energy"
                  value={filters.energy}
                  onToggle={() =>
                    setFilters((current) => ({
                      ...current,
                      energy: current.energy === null ? 50 : null,
                    }))
                  }
                  onChange={(value) =>
                    setFilters((current) => ({
                      ...current,
                      energy: value,
                    }))
                  }
                />

                <OptionalSlider
                  label="Mood"
                  value={filters.mood}
                  onToggle={() =>
                    setFilters((current) => ({
                      ...current,
                      mood: current.mood === null ? 50 : null,
                    }))
                  }
                  onChange={(value) =>
                    setFilters((current) => ({
                      ...current,
                      mood: value,
                    }))
                  }
                />

                <OptionalSlider
                  label="Acoustic"
                  value={filters.acoustic}
                  onToggle={() =>
                    setFilters((current) => ({
                      ...current,
                      acoustic: current.acoustic === null ? 50 : null,
                    }))
                  }
                  onChange={(value) =>
                    setFilters((current) => ({
                      ...current,
                      acoustic: value,
                    }))
                  }
                />
              </div>
            </div>

            <div className="rounded-[32px] border border-white/10 bg-white/10 p-6 shadow-2xl backdrop-blur-xl">
              <div className="mb-4 text-3xl font-black text-white">
                Tracks Similar in your Playlist:
              </div>

              {isLoading && (
                <div className="mb-4 text-sm font-semibold text-white/60">
                  Loading recommendations...
                </div>
              )}

              {error && (
                <div className="mb-4 rounded-2xl border border-red-400/20 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-300">
                  {error}
                </div>
              )}

              {!isLoading && !error && tracks.length === 0 && (
                <div className="mb-4 rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white/70">
                  No recommendations found for the current filters.
                </div>
              )}

              <div className="grid gap-3 sm:grid-cols-2">
                {tracks.map((track) => {
                  const isActive = track.id === activeTrack.id;

                  return (
                    <button
                      key={track.id}
                      type="button"
                      onClick={() => setActiveTrack(track)}
                      className={`flex items-center gap-3 rounded-2xl border p-3 text-left transition ${
                        isActive
                          ? "border-white/20 bg-white/10"
                          : "border-white/10 bg-black/20 hover:bg-white/10"
                      }`}
                    >
                      {track.coverImageUrl ? (
                        <img
                          src={track.coverImageUrl}
                          alt={track.title}
                          className="h-12 w-12 rounded-xl object-cover"
                        />
                      ) : (
                        <div
                          className="h-12 w-12 rounded-xl"
                          style={{
                            background: `linear-gradient(135deg, ${track.palette.primary}, ${track.palette.secondary})`,
                          }}
                        />
                      )}

                      <div className="min-w-0">
                        <div className="truncate text-sm font-bold text-white">
                          {track.title}
                        </div>
                        <div className="truncate text-xs text-white/60">
                          {track.artist}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div
            className="h-full rounded-[32px] border p-5 shadow-2xl backdrop-blur-xl md:p-6"
            style={{
              background: `linear-gradient(135deg, ${hexToRgba(
                activeTrack.palette.primary,
                0.32
              )}, ${hexToRgba(activeTrack.palette.secondary, 0.18)})`,
              borderColor: hexToRgba(activeTrack.palette.accent, 0.3),
            }}
          >
            <div className="grid h-full gap-4 lg:grid-cols-[1fr_0.9fr]">
              <div className="space-y-4">
                <div className="grid gap-4 rounded-[28px] border border-white/10 bg-black/15 p-4 md:grid-cols-[8rem_1fr]">
                  {activeTrack.coverImageUrl ? (
                    <img
                      src={activeTrack.coverImageUrl}
                      alt={activeTrack.title}
                      className="aspect-square rounded-[22px] object-cover"
                    />
                  ) : (
                    <div
                      className="aspect-square rounded-[22px]"
                      style={{
                        background: `linear-gradient(135deg, ${activeTrack.palette.primary}, ${activeTrack.palette.secondary})`,
                      }}
                    />
                  )}

                  <div className="flex flex-col justify-between gap-4">
                    <div>
                      <div className="text-2xl font-black text-white">
                        {activeTrack.title}
                      </div>
                      <div className="text-sm text-white/70">
                        {activeTrack.artist}
                      </div>
                    </div>

                    <div className="flex items-center justify-center gap-5 text-2xl text-white">
                      <span>◀◀</span>
                      <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2">
                        II
                      </span>
                      <span>▶▶</span>
                    </div>

                    <div>
                      <div className="mb-2 h-2 rounded-full bg-white/15">
                        <div
                          className="h-2 rounded-full"
                          style={{
                            width: "58%",
                            backgroundColor: activeTrack.palette.accent,
                          }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-white/60">
                        <span>1:20</span>
                        <span>{activeTrack.duration}</span>
                      </div>
                    </div>

                    {activeTrack.previewUrl ? (
                      <a
                        href={activeTrack.previewUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs font-semibold text-white/70 underline"
                      >
                        Open preview
                      </a>
                    ) : (
                      <div className="text-xs text-white/40">
                        No preview available
                      </div>
                    )}
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-[0.8fr_1fr]">
                  <div className="rounded-[24px] border border-white/10 bg-black/15 p-4">
                    <div
                      className="mb-4 text-4xl font-black"
                      style={{ color: activeTrack.palette.accent }}
                    >
                      Genre:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {activeTrack.genres.length > 0 ? (
                        activeTrack.genres.map((genre) => (
                          <span
                            key={genre}
                            className="rounded-full border px-3 py-1.5 text-sm font-bold"
                            style={{
                              borderColor: hexToRgba(
                                activeTrack.palette.accent,
                                0.4
                              ),
                              color: activeTrack.palette.accent,
                              backgroundColor: hexToRgba(
                                activeTrack.palette.accent,
                                0.08
                              ),
                            }}
                          >
                            {genre}
                          </span>
                        ))
                      ) : (
                        <span className="text-sm text-white/40">
                          No genres available
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="overflow-hidden rounded-[24px] border border-white/10 bg-black/15">
                    <div
                      className="h-64 w-full"
                      style={{
                        background: activeTrack.coverImageUrl
                          ? `center / cover no-repeat url(${activeTrack.coverImageUrl})`
                          : `linear-gradient(180deg, ${hexToRgba(
                              activeTrack.palette.secondary,
                              0.45
                            )}, ${hexToRgba(activeTrack.palette.primary, 0.4)})`,
                      }}
                    />
                    <div className="space-y-4 p-4">
                      <div>
                        <div className="text-4xl font-black text-white">
                          {activeTrack.popularity ?? 0}/100
                        </div>
                        <div className="text-xs text-white/55">Popularity</div>
                      </div>
                      <div>
                        <div className="text-4xl font-black text-white">
                          {activeTrack.genres.length}
                        </div>
                        <div className="text-xs text-white/55">Matched genres</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-[28px] border border-white/10 bg-black/15 p-4">
                <div className="mb-3 text-sm font-bold text-white/80">
                  Why this matches
                </div>
                <div className="space-y-3 text-sm text-white/70">
                  {activeTrack.matchReasons && activeTrack.matchReasons.length > 0 ? (
                    activeTrack.matchReasons.map((reason, index) => (
                      <div
                        key={`${reason}-${index}`}
                        className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
                      >
                        {reason}
                      </div>
                    ))
                  ) : (
                    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                      No match explanation available.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}