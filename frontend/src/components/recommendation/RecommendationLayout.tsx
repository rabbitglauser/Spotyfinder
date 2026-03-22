"use client";

import React, { useRef, useState } from "react";
import { Music4, Sparkles, Upload } from "lucide-react";

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
  playlistName: string;
  setPlaylistName: React.Dispatch<React.SetStateAction<string>>;
  selectedFile: File | null;
  enrichWithSpotify: boolean;
  setEnrichWithSpotify: React.Dispatch<React.SetStateAction<boolean>>;
  isUploading: boolean;
  uploadMessage: string | null;
  uploadError: string | null;
  onFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onUpload: () => Promise<void>;
  onFind: () => void;
}

function addGenreToFront(list: string[], value: string) {
  const trimmed = value.trim();

  if (!trimmed) return list;

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
    <div className="space-y-3">
      <div className="section-pill px-4 py-3 text-sm font-bold uppercase tracking-[0.18em] text-white/55">
        {title}
      </div>

      <div className="soft-panel rounded-[24px] p-3">
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
          className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-white/28"
        />

        <div className="mt-3 flex min-h-[36px] flex-wrap gap-2">
          {values.length === 0 ? (
            <span className="text-sm text-white/35">No genres added yet</span>
          ) : (
            values.map((genre) => (
              <button
                key={genre}
                type="button"
                onClick={() => onRemove(genre)}
                className="genre-pill group inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-semibold transition hover:border-red-400/40 hover:bg-red-500/10 hover:text-red-200"
              >
                <span>{genre}</span>
                <span className="text-xs opacity-0 transition group-hover:opacity-100">
                  ✕
                </span>
              </button>
            ))
          )}
        </div>
      </div>
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
    <div className="soft-panel rounded-[24px] p-4">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <div className="text-base font-black text-white">{label}</div>
          <div className="text-xs text-white/42">{description}</div>
        </div>

        <button
          type="button"
          onClick={onToggle}
          className="relative h-7 w-14 rounded-full transition"
          style={{
            background: slider.enabled
              ? "linear-gradient(90deg, var(--theme-accent), var(--theme-warm))"
              : "rgba(255,255,255,0.12)",
            boxShadow: slider.enabled
              ? "0 0 18px color-mix(in srgb, var(--theme-accent) 22%, transparent)"
              : "none",
          }}
        >
          <span
            className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${
              slider.enabled ? "left-8" : "left-1"
            }`}
          />
        </button>
      </div>

      <div className={slider.enabled ? "opacity-100" : "opacity-35"}>
        <div className="mb-2 text-sm font-semibold text-white/58">
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
          className="themed-slider"
        />
      </div>
    </div>
  );
}

export default function RecommendationLayout({
  filters,
  setFilters,
  playlistName,
  setPlaylistName,
  selectedFile,
  enrichWithSpotify,
  setEnrichWithSpotify,
  isUploading,
  uploadMessage,
  uploadError,
  onFileChange,
  onUpload,
  onFind,
}: RecommendationLayoutProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  return (
    <div
      className="page-shell page-shell--locked"
      style={
        {
          "--theme-accent": "#1ed760",
          "--theme-dominant": "#1db954",
          "--theme-warm": "#79f2a3",
          "--theme-deep": "#0d1110",
          "--theme-panel": "#111513",
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
          <div>
            <h1 className="page-title text-5xl sm:text-6xl lg:text-7xl">
              Find your uniqueness
            </h1>
            <p className="mt-3 max-w-2xl text-sm text-soft">
              Upload your Exportify CSV, tune your taste filters, and move into
              your refined recommendations.
            </p>
          </div>

          <div className="grid min-h-0 flex-1 gap-5 xl:grid-cols-[0.88fr_1.12fr]">
            <div className="glass-panel glass-panel--accent flex min-h-0 flex-col rounded-[32px] p-5 md:p-6">
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,text/csv"
                className="hidden"
                onChange={onFileChange}
              />

              <div className="flex h-full min-h-0 flex-col justify-between gap-6">
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="spotify-button-dark mx-auto flex h-24 w-24 items-center justify-center rounded-full"
                  >
                    <Upload className="h-10 w-10 text-white/80" />
                  </button>

                  <div className="mx-auto mt-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-white/55">
                    <Sparkles className="h-4 w-4" />
                    exportify flow
                  </div>

                  <h2 className="mt-5 text-4xl font-black tracking-tight text-white md:text-5xl">
                    Upload CSV
                  </h2>
                  <p className="mx-auto mt-3 max-w-lg text-sm text-soft">
                    Wähle deine Exportify-Datei aus und importiere sie direkt ins
                    Backend.
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="playlistName"
                      className="mb-2 block text-sm font-semibold text-white/70"
                    >
                      Playlist name
                    </label>
                    <input
                      id="playlistName"
                      type="text"
                      value={playlistName}
                      onChange={(event) => setPlaylistName(event.target.value)}
                      placeholder="z. B. Gym Mix 2026"
                      className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-white outline-none placeholder:text-white/28"
                    />
                  </div>

                  <div className="grid gap-4 md:grid-cols-[1fr_auto]">
                    <div className="soft-panel rounded-[24px] p-4">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <div className="text-sm font-black text-white">
                            Enrich with Spotify
                          </div>
                          <div className="text-xs text-white/42">
                            Zusätzliche Spotify-Daten mitverwenden
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() =>
                            setEnrichWithSpotify((current) => !current)
                          }
                          className="relative h-7 w-14 rounded-full transition"
                          style={{
                            background: enrichWithSpotify
                              ? "linear-gradient(90deg, var(--theme-accent), var(--theme-warm))"
                              : "rgba(255,255,255,0.12)",
                            boxShadow: enrichWithSpotify
                              ? "0 0 18px color-mix(in srgb, var(--theme-accent) 22%, transparent)"
                              : "none",
                          }}
                        >
                          <span
                            className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${
                              enrichWithSpotify ? "left-8" : "left-1"
                            }`}
                          />
                        </button>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="spotify-button-dark rounded-[24px] px-5 py-4 text-sm font-black"
                    >
                      Datei auswählen
                    </button>
                  </div>

                  {selectedFile ? (
                    <div className="soft-panel rounded-[22px] px-4 py-3 text-sm text-white/80">
                      <span className="font-black text-white">Datei:</span>{" "}
                      {selectedFile.name}
                    </div>
                  ) : (
                    <div className="rounded-[22px] border border-dashed border-white/12 px-4 py-3 text-sm text-white/38">
                      Noch keine CSV ausgewählt
                    </div>
                  )}

                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      type="button"
                      onClick={onUpload}
                      disabled={
                        !selectedFile || !playlistName.trim() || isUploading
                      }
                      className="spotify-button rounded-full px-7 py-3.5 text-base font-black disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {isUploading ? "Uploading..." : "Upload CSV"}
                    </button>

                    {uploadMessage && (
                      <div className="text-sm font-bold text-green-300">
                        {uploadMessage}
                      </div>
                    )}

                    {uploadError && (
                      <div className="text-sm font-bold text-red-300">
                        {uploadError}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="glass-panel flex min-h-0 flex-col overflow-hidden rounded-[32px] p-4 md:p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-white/55">
                  <Music4 className="h-4 w-4" />
                  taste filters
                </div>

                <div className="text-xs text-white/35">
                  Tune your recommendation vibe
                </div>
              </div>

              <div className="panel-scroll flex-1 space-y-4">
                <GenreInputField
                  title="Include genres"
                  placeholder="Type a genre and press Enter"
                  values={filters.includeGenres}
                  onAdd={(value) =>
                    setFilters((current) => ({
                      ...current,
                      includeGenres: addGenreToFront(
                        current.includeGenres,
                        value
                      ),
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
                      excludeGenres: addGenreToFront(
                        current.excludeGenres,
                        value
                      ),
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

              <div className="mt-4 flex justify-end border-t border-white/8 pt-4">
                <button
                  type="button"
                  onClick={onFind}
                  className="spotify-button rounded-full px-8 py-4 text-lg font-black"
                >
                  Find
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}