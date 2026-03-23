"use client";

import React from "react";
import {
  Pause,
  SkipBack,
  SkipForward,
  Sparkles,
  TrendingUp,
} from "lucide-react";

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
  const raw = (hex || "#1ed760").replace("#", "").trim();
  const normalized =
    raw.length === 3
      ? raw
          .split("")
          .map((char) => char + char)
          .join("")
      : raw.padEnd(6, "0").slice(0, 6);

  const bigint = parseInt(normalized, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
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
    <div className="soft-panel rounded-[24px] p-4">
      <div className="mb-3 flex items-center justify-between gap-4">
        <div>
          <div className="text-base font-black text-white">{label}</div>
          <div className="text-xs text-white/42">Value: {value}/100</div>
        </div>
      </div>

      <input
        type="range"
        min={0}
        max={100}
        step={1}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="themed-slider"
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
    <div className="soft-panel rounded-[24px] p-4">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <div className="text-base font-black text-white">{label}</div>
          <div className="text-xs text-white/42">
            {enabled ? `Value: ${sliderValue}/100` : "Disabled"}
          </div>
        </div>

        <button
          type="button"
          onClick={onToggle}
          className="relative h-7 w-14 rounded-full transition"
          style={{
            background: enabled
              ? "linear-gradient(90deg, var(--theme-accent), var(--theme-warm))"
              : "rgba(255,255,255,0.12)",
            boxShadow: enabled
              ? "0 0 18px color-mix(in srgb, var(--theme-accent) 22%, transparent)"
              : "none",
          }}
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
        className="themed-slider"
      />
    </div>
  );
}

function GenrePills({
  genres,
  accent,
}: {
  genres: string[];
  accent: string;
}) {
  if (!genres || genres.length === 0) {
    return (
      <div className="text-sm font-medium text-white/40">
        No genres returned for this track.
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {genres.map((genre) => (
        <span
          key={genre}
          className="rounded-full border px-3 py-1.5 text-sm font-bold"
          style={{
            borderColor: hexToRgba(accent, 0.35),
            color: accent,
            backgroundColor: hexToRgba(accent, 0.08),
          }}
        >
          {genre}
        </span>
      ))}
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
  const themePrimary = activeTrack.palette.primary || "#1ed760";
  const themeSecondary =
    activeTrack.palette.secondary || activeTrack.palette.primary || "#79f2a3";
  const themeAccent = activeTrack.palette.primary || "#1ed760";

  return (
    <div
      className="page-shell page-shell--locked"
      style={
        {
          "--theme-accent": themeAccent,
          "--theme-dominant": themePrimary,
          "--theme-warm": themeSecondary,
          "--theme-deep": "#0b0d0f",
          "--theme-panel": "#101314",
          "--theme-soft": "rgba(255,255,255,0.82)",
        } as React.CSSProperties
      }
    >
      <div className="ambient-bg">
        <div className="ambient-orb ambient-orb--one" />
        <div className="ambient-orb ambient-orb--two" />
        <div className="ambient-orb ambient-orb--three" />
        <div className="ambient-orb ambient-orb--four" />
        <div className="ambient-orb ambient-orb--five" />
      </div>

      <div className="page-content">
        <div className="page-frame">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h1 className="page-title text-5xl sm:text-6xl lg:text-7xl">
                Refine your Search
              </h1>
              <p className="mt-3 max-w-2xl text-sm text-soft">
                Fine-tune your playlist DNA and let the active track set the
                color mood of the recommendation space.
              </p>
            </div>

            <div className="hidden rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-white/45 xl:inline-flex">
              {tracks.length} suggestions
            </div>
          </div>

          <div className="grid min-h-0 flex-1 gap-5 xl:grid-cols-[0.84fr_1.16fr]">
            <div className="grid min-h-0 gap-5 xl:grid-rows-[minmax(0,1fr)_minmax(280px,0.72fr)]">
              <div className="glass-panel flex min-h-0 flex-col rounded-[32px] p-4 md:p-5">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div className="section-pill px-4 py-3 text-sm font-bold uppercase tracking-[0.18em] text-white/55">
                    Playlist DNA
                  </div>
                  <div className="text-xs text-white/35">
                    Based on your uploaded data
                  </div>
                </div>

                <div className="panel-scroll space-y-4">
                  <div className="space-y-3">
                    <div className="section-pill px-4 py-3 text-sm font-bold uppercase tracking-[0.18em] text-white/55">
                      Include genres
                    </div>
                    <div className="soft-panel min-h-[72px] rounded-[24px] p-4">
                      <GenrePills
                        genres={filters.includeGenres}
                        accent={themeAccent}
                      />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="section-pill px-4 py-3 text-sm font-bold uppercase tracking-[0.18em] text-white/55">
                      Exclude genres
                    </div>
                    <div className="soft-panel min-h-[72px] rounded-[24px] p-4">
                      <GenrePills
                        genres={filters.excludeGenres}
                        accent={themeAccent}
                      />
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

              <div className="glass-panel flex min-h-0 flex-col rounded-[32px] p-4 md:p-5">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div className="text-2xl font-black text-white">
                    Similar tracks you might like
                  </div>
                  <div className="text-xs text-white/35">
                    Click a card to focus it
                  </div>
                </div>

                {isLoading && (
                  <div className="mb-4 rounded-[20px] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-semibold text-white/60">
                    Loading recommendations...
                  </div>
                )}

                {error && (
                  <div className="mb-4 rounded-[20px] border border-red-400/20 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-300">
                    {error}
                  </div>
                )}

                {!isLoading && !error && tracks.length === 0 && (
                  <div className="mb-4 rounded-[20px] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white/70">
                    No recommendations found for the current filters.
                  </div>
                )}

                <div className="panel-scroll grid gap-3 sm:grid-cols-2">
                  {tracks.map((track) => {
                    const isActive = track.id === activeTrack.id;
                    const cardPrimary = track.palette.primary || themePrimary;
                    const cardSecondary =
                      track.palette.secondary || track.palette.primary || themeSecondary;
                    const cardAccent = track.palette.primary || themeAccent;

                    return (
                      <button
                        key={track.id}
                        type="button"
                        onClick={() => setActiveTrack(track)}
                        className="group flex items-center gap-3 rounded-[22px] border p-3 text-left transition duration-200 hover:-translate-y-[1px]"
                        style={{
                          borderColor: isActive
                            ? hexToRgba(cardAccent, 0.42)
                            : "rgba(255,255,255,0.08)",
                          background: `linear-gradient(135deg, ${hexToRgba(
                            cardPrimary,
                            isActive ? 0.24 : 0.14
                          )}, ${hexToRgba(
                            cardSecondary,
                            isActive ? 0.14 : 0.06
                          )})`,
                          boxShadow: isActive
                            ? `0 0 32px ${hexToRgba(cardAccent, 0.16)}`
                            : "none",
                        }}
                      >
                        {track.coverImageUrl ? (
                          <img
                            src={track.coverImageUrl}
                            alt={track.title}
                            className="h-14 w-14 rounded-2xl object-cover shadow-[0_8px_18px_rgba(0,0,0,0.35)]"
                          />
                        ) : (
                          <div
                            className="h-14 w-14 rounded-2xl"
                            style={{
                              background: `linear-gradient(135deg, ${cardPrimary}, ${cardSecondary})`,
                            }}
                          />
                        )}

                        <div className="min-w-0 flex-1">
                          <div className="truncate text-sm font-black text-white">
                            {track.title}
                          </div>
                          <div className="truncate text-xs text-white/60">
                            {track.artist}
                          </div>

                          <div className="mt-2 flex items-center gap-2 text-[11px] text-white/45">
                            {typeof track.popularity === "number" && (
                              <span
                                className="rounded-full border px-2 py-1"
                                style={{
                                  borderColor: hexToRgba(cardAccent, 0.28),
                                  backgroundColor: hexToRgba(cardAccent, 0.08),
                                }}
                              >
                                {track.popularity}/100
                              </span>
                            )}
                            <span>{track.genres.length} genres</span>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="glass-panel glass-panel--accent min-h-0 overflow-hidden rounded-[32px] p-4 md:p-5">
              <div
                className="relative h-full min-h-0 overflow-hidden rounded-[28px] border p-4 md:p-5"
                style={{
                  borderColor: hexToRgba(themeAccent, 0.28),
                  background: `linear-gradient(135deg, ${hexToRgba(
                    themePrimary,
                    0.24
                  )}, ${hexToRgba(themeSecondary, 0.12)})`,
                }}
              >
                <div
                  className="pointer-events-none absolute -right-16 top-6 h-56 w-56 rounded-full blur-3xl"
                  style={{
                    background: hexToRgba(themePrimary, 0.24),
                  }}
                />
                <div
                  className="pointer-events-none absolute -bottom-20 left-1/3 h-52 w-52 rounded-full blur-3xl"
                  style={{
                    background: hexToRgba(themeSecondary, 0.2),
                  }}
                />

              <div className="relative grid h-full min-h-0 gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
                <div className="grid min-h-0 content-start gap-4">
                  <div className="glass-subpanel rounded-[28px] p-4 md:p-5">
                    <div className="flex flex-col gap-4 md:flex-row">
                      <div
                        className="cover-glow h-36 w-36 shrink-0 overflow-hidden rounded-[24px] border"
                        style={{
                          borderColor: hexToRgba(themeAccent, 0.24),
                        }}
                      >
                        {activeTrack.coverImageUrl ? (
                          <img
                            src={activeTrack.coverImageUrl}
                            alt={activeTrack.title}
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <div
                            className="h-full w-full"
                            style={{
                              background: `linear-gradient(135deg, ${themePrimary}, ${themeSecondary})`,
                            }}
                          />
                        )}
                      </div>

                      <div className="flex min-w-0 flex-1 flex-col justify-between gap-4">
                        <div>
                          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-[11px] font-bold uppercase tracking-[0.18em] text-white/58">
                            <Sparkles className="h-3.5 w-3.5" />
                            now focused
                          </div>

                          <div className="mt-4 text-3xl font-black leading-tight text-white">
                            {activeTrack.title}
                          </div>
                          <div className="mt-1 text-sm text-white/68">
                            {activeTrack.artist}
                          </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-3">
                          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-2 text-white/85">
                            <SkipBack className="h-4 w-4" />
                            <div className="rounded-full border border-white/10 bg-white/[0.08] p-2">
                              <Pause className="h-4 w-4" />
                            </div>
                            <SkipForward className="h-4 w-4" />
                          </div>

                          {activeTrack.previewUrl ? (
                            <a
                              href={activeTrack.previewUrl}
                              target="_blank"
                              rel="noreferrer"
                              className="spotify-button rounded-full px-4 py-2 text-xs font-black"
                            >
                              Open preview
                            </a>
                          ) : (
                            <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-semibold text-white/42">
                              No preview
                            </div>
                          )}
                        </div>

                        <div>
                          <div className="mb-2 h-2 rounded-full bg-white/12">
                            <div
                              className="h-2 rounded-full"
                              style={{
                                width: "58%",
                                backgroundColor: themeAccent,
                                boxShadow: `0 0 16px ${hexToRgba(themeAccent, 0.32)}`,
                              }}
                            />
                          </div>

                          <div className="flex justify-between text-xs text-white/55">
                            <span>1:20</span>
                            <span>{activeTrack.duration}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_260px]">
                    <div className="glass-subpanel rounded-[24px] p-4">
                      <div
                        className="mb-4 text-3xl font-black"
                        style={{ color: themeAccent }}
                      >
                        Genre
                      </div>

                      <GenrePills genres={activeTrack.genres} accent={themeAccent} />
                    </div>

                    <div className="glass-subpanel self-start rounded-[24px] p-4">
                      <div className="overflow-hidden rounded-[20px] border border-white/10">
                        <div className="aspect-square w-full overflow-hidden">
                          {activeTrack.coverImageUrl ? (
                            <img
                              src={activeTrack.coverImageUrl}
                              alt={activeTrack.title}
                              className="h-full w-full object-cover"
                            />
                          ) : (
                            <div
                              className="h-full w-full"
                              style={{
                                background: `linear-gradient(135deg, ${themePrimary}, ${themeSecondary})`,
                              }}
                            />
                          )}
                        </div>
                      </div>

                      <div className="mt-4 grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-4xl font-black text-white">
                            {activeTrack.popularity ?? 0}
                            <span className="text-xl text-white/55">/100</span>
                          </div>
                          <div className="mt-1 text-xs text-white/55">Popularity</div>
                        </div>

                        <div>
                          <div className="text-4xl font-black text-white">
                            {activeTrack.genres.length}
                          </div>
                          <div className="mt-1 text-xs text-white/55">Matched genres</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

  <div className="glass-subpanel flex min-h-0 flex-col rounded-[28px] p-4 md:p-5">
    <div className="mb-4 flex items-center gap-2 text-sm font-black text-white/80">
      <TrendingUp className="h-4 w-4" />
      Why this matches
    </div>

    <div className="panel-scroll space-y-3 text-sm text-white/72">
      {activeTrack.matchReasons && activeTrack.matchReasons.length > 0 ? (
        activeTrack.matchReasons.map((reason, index) => (
          <div
            key={`${reason}-${index}`}
            className="rounded-[20px] border border-white/10 bg-white/[0.05] px-4 py-3"
            style={{
              boxShadow: `inset 0 0 0 1px ${hexToRgba(themeAccent, 0.06)}`,
            }}
          >
            {reason}
          </div>
        ))
      ) : (
        <div className="rounded-[20px] border border-white/10 bg-white/[0.05] px-4 py-3">
          No match explanation available.
        </div>
      )}
    </div>
  </div>
</div>
                  <div className="glass-subpanel flex min-h-0 flex-col rounded-[28px] p-4 md:p-5">
                    <div className="mb-4 flex items-center gap-2 text-sm font-black text-white/80">
                      <TrendingUp className="h-4 w-4" />
                      Why this matches
                    </div>

                    <div className="panel-scroll space-y-3 text-sm text-white/72">
                      {activeTrack.matchReasons &&
                      activeTrack.matchReasons.length > 0 ? (
                        activeTrack.matchReasons.map((reason, index) => (
                          <div
                            key={`${reason}-${index}`}
                            className="rounded-[20px] border border-white/10 bg-white/[0.05] px-4 py-3"
                            style={{
                              boxShadow: `inset 0 0 0 1px ${hexToRgba(
                                themeAccent,
                                0.06
                              )}`,
                            }}
                          >
                            {reason}
                          </div>
                        ))
                      ) : (
                        <div className="rounded-[20px] border border-white/10 bg-white/[0.05] px-4 py-3">
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
      </div>
  );
}