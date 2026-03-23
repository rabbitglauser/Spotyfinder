"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, ExternalLink, Upload } from "lucide-react";

export interface GettingStartedStepCard {
  id: number;
  buttonLabel: string;
  title: string;
  description: string;
  type: "login" | "export" | "upload";
}

export interface GettingStartedInfoBlock {
  title: string;
  description: string;
}

interface GettingStartedLayoutProps {
  stepCards: GettingStartedStepCard[];
  infoBlock: GettingStartedInfoBlock;
}

function PreviewCard({ type }: { type: GettingStartedStepCard["type"] }) {
  if (type === "login") {
    return (
      <div className="mock-ui soft-panel flex h-full items-center justify-center overflow-hidden rounded-[26px] p-4">
        <div className="w-full max-w-[290px]">
          <div className="mb-3 text-sm font-extrabold text-white underline decoration-white/25 underline-offset-4">
            https://exportify.net/
          </div>

          <div className="mx-auto flex w-[180px] flex-col gap-2 rounded-[22px] border border-white/10 bg-black/40 p-3 shadow-[0_16px_40px_rgba(0,0,0,0.35)]">
            <div className="text-center text-[1.65rem] font-black leading-none text-white">
              Welcome back
            </div>

            <div className="rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-[9px] leading-tight text-white/50">
              Email address or username
            </div>

            <div className="spotify-button rounded-full px-4 py-2 text-center text-[9px] font-black">
              Continue
            </div>

            <div className="text-center text-[8px] text-white/35">or</div>

            <div className="rounded-full border border-white/12 px-3 py-2 text-center text-[8px] text-white/75">
              Continue with Google
            </div>
            <div className="rounded-full border border-white/12 px-3 py-2 text-center text-[8px] text-white/75">
              Continue with Facebook
            </div>
            <div className="rounded-full border border-white/12 px-3 py-2 text-center text-[8px] text-white/75">
              Continue with Apple
            </div>

            <div className="pt-1 text-center text-[7px] text-white/35">
              Don&apos;t have an account?
            </div>
            <div className="text-center text-[7px] font-semibold text-white/55">
              Register
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (type === "export") {
    return (
      <div className="mock-ui soft-panel flex h-full items-center justify-center overflow-hidden rounded-[26px] p-4">
        <div className="w-full max-w-[300px] rounded-[22px] border border-white/10 bg-black/35 p-4">
          <div className="mb-4 flex items-center justify-between text-xs text-white/55">
            <span>Tracks</span>
            <span className="rounded-lg border border-white/10 px-3 py-1 text-[10px] text-white/70">
              Export All
            </span>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.04] px-3 py-3">
              <span className="text-sm text-white/70">2385</span>
              <span className="spotify-button rounded-lg px-3 py-1 text-[10px] font-black">
                Export
              </span>
            </div>

            <div className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.04] px-3 py-3">
              <span className="text-sm text-white/70">402</span>
              <span className="spotify-button rounded-lg px-3 py-1 text-[10px] font-black">
                Export
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mock-ui soft-panel flex h-full items-center justify-center overflow-hidden rounded-[26px] p-4">
      <div className="w-full max-w-[220px] rounded-[22px] border border-white/10 bg-black/35 p-4">
        <div className="mb-3 text-center text-[10px] font-black uppercase tracking-[0.22em] text-[var(--theme-accent)]">
          Find your uniqueness
        </div>

        <div className="space-y-3">
          <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-3 text-[9px] text-white/35">
            Drop your CSV...
          </div>
          <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-3 text-[9px] text-white/35">
            Add your filters...
          </div>
          <div className="spotify-button mx-auto w-fit rounded-full px-4 py-2 text-[10px] font-black">
            Find
          </div>
        </div>
      </div>
    </div>
  );
}

function ActionButton({
  type,
  label,
}: {
  type: GettingStartedStepCard["type"];
  label: string;
}) {
  if (type === "login" || type === "export") {
    return (
      <a
        href="https://exportify.net/"
        target="_blank"
        rel="noreferrer"
        className="spotify-button inline-flex w-full items-center justify-center gap-2 rounded-full px-6 py-4 text-base font-black transition"
      >
        {label}
        <ExternalLink className="h-4 w-4" />
      </a>
    );
  }

  return (
    <Link
      href="/find-your-uniqueness"
      className="spotify-button inline-flex w-full items-center justify-center gap-2 rounded-full px-6 py-4 text-base font-black transition"
    >
      {label}
      <Upload className="h-4 w-4" />
    </Link>
  );
}

export default function GettingStartedLayout({
  stepCards,
}: GettingStartedLayoutProps) {
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
        <div className="mx-auto flex h-full w-full max-w-[1240px] min-h-0 flex-col">
          <div className="shrink-0">
            <h1 className="page-title text-5xl sm:text-6xl lg:text-7xl">
              Getting Started
            </h1>
            <p className="mt-3 max-w-2xl text-sm text-soft">
              Export your Spotify playlist with Exportify, upload the CSV, then
              move into your recommendation flow.
            </p>
          </div>

          <div className="mt-8 flex flex-1 flex-col justify-between gap-8">
            <div className="flex flex-wrap items-start justify-center gap-8 xl:flex-nowrap">
              {stepCards.map((card) => (
                <div
                  key={card.id}
                  className="flex w-full max-w-[360px] flex-col gap-4"
                >
                  <ActionButton type={card.type} label={card.buttonLabel} />

                  <div className="glass-panel h-[670px] rounded-[32px] p-5">
                    <div className="flex h-full flex-col">
                      <div className="h-[430px] shrink-0">
                        <PreviewCard type={card.type} />
                      </div>

                      <div className="flex flex-1 items-center justify-center px-4">
                        <p className="max-w-[250px] text-center text-[1.1rem] font-black leading-tight text-white sm:text-[1.25rem]">
                          {card.description}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="grid shrink-0 items-end gap-4 xl:grid-cols-[1fr_auto]">
              <div className="glass-panel h-[110px] rounded-[28px] bg-[linear-gradient(135deg,rgba(30,215,96,0.28),rgba(20,90,16,0.62))] p-0" />

              <div className="flex items-center justify-end">
                <Link
                  href="/find-your-uniqueness"
                  className="spotify-button inline-flex items-center gap-2 rounded-full px-6 py-4 text-base font-black"
                >
                  Continue
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}