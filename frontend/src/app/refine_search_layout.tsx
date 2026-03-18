"use client";

import React from "react";

export interface RefineSearchFilters {
  includeGenres: string[];
  excludeGenres: string[];
  popularity: number;
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
  followers: number;
  monthlyListeners: number;
  duration: string;
  palette: TrackPalette;
}

interface RefineSearchLayoutProps {
  filters: RefineSearchFilters;
  setFilters: React.Dispatch<React.SetStateAction<RefineSearchFilters>>;
  tracks: RefineSearchTrack[];
  activeTrack: RefineSearchTrack;
  setActiveTrack: React.Dispatch<React.SetStateAction<RefineSearchTrack>>;
}

function hexToRgba(hex: string, alpha: number) {
  const cleaned = hex.replace("#", "");
  const bigint = parseInt(cleaned, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function formatCompact(value: number) {
  return new Intl.NumberFormat("en", { notation: "compact" }).format(value);
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

export default function RefineSearchLayout({
  filters,
  setFilters,
  tracks,
  activeTrack,
  setActiveTrack,
}: RefineSearchLayoutProps) {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#030303] text-white">
      <BackgroundBlobs accent={activeTrack.palette.accent} />

      <div className="relative z-10 flex min-h-screen w-full flex-col px-6 py-8 md:px-10 lg:px-14">
        {/* HEADER START */}
        <div className="mb-8">
          <h1 className="text-5xl font-black tracking-tight text-[#19c819] sm:text-6xl md:text-7xl lg:text-8xl">
            Refine your Search
          </h1>
        </div>
        {/* HEADER END */}

        <div className="grid flex-1 gap-8 xl:grid-cols-[0.95fr_1.1fr]">
          <div className="flex h-full flex-col gap-6">
            {/* FILTERFIELD START */}
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
                  </div>
                </div>

                <div>
                  <div className="mb-2 text-sm font-bold text-white/55">
                    Popularity: {filters.popularity}/100
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={100}
                    step={1}
                    value={filters.popularity}
                    onChange={(event) =>
                      setFilters((current) => ({
                        ...current,
                        popularity: Number(event.target.value),
                      }))
                    }
                    className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10"
                    style={{ accentColor: activeTrack.palette.accent }}
                  />
                </div>
              </div>
            </div>
            {/* FILTERFIELD END */}

            {/* TRACKLIST START */}
            <div className="rounded-[32px] border border-white/10 bg-white/10 p-6 shadow-2xl backdrop-blur-xl">
              <div className="mb-4 text-3xl font-black text-white">
                Tracks Similar in your Playlist:
              </div>

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
                      <div
                        className="h-12 w-12 rounded-xl"
                        style={{
                          background: `linear-gradient(135deg, ${track.palette.primary}, ${track.palette.secondary})`,
                        }}
                      />
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
            {/* TRACKLIST END */}
          </div>

          {/* RESULTCARD START */}
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
                  <div
                    className="aspect-square rounded-[22px]"
                    style={{
                      background: `linear-gradient(135deg, ${activeTrack.palette.primary}, ${activeTrack.palette.secondary})`,
                    }}
                  />

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
                      {activeTrack.genres.map((genre) => (
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
                      ))}
                    </div>
                  </div>

                  <div className="overflow-hidden rounded-[24px] border border-white/10 bg-black/15">
                    <div
                      className="h-64 w-full"
                      style={{
                        background: `linear-gradient(180deg, ${hexToRgba(
                          activeTrack.palette.secondary,
                          0.45
                        )}, ${hexToRgba(activeTrack.palette.primary, 0.4)})`,
                      }}
                    />
                    <div className="space-y-4 p-4">
                      <div className="flex items-end justify-between gap-4 text-white">
                        <div>
                          <div className="text-4xl font-black">
                            {formatCompact(activeTrack.followers)}
                          </div>
                          <div className="text-xs text-white/55">
                            Followers
                          </div>
                        </div>
                        <div className="text-sm font-semibold text-white/75">
                          HEAR ME
                        </div>
                      </div>
                      <div>
                        <div className="text-4xl font-black text-white">
                          {formatCompact(activeTrack.monthlyListeners)}
                        </div>
                        <div className="text-xs text-white/55">
                          Monthly listeners
                        </div>
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
                </div>
              </div>
            </div>
          </div>
          {/* RESULTCARD END */}
        </div>
      </div>
    </div>
  );
}