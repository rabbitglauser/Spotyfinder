"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Download, ExternalLink, Upload } from "lucide-react";

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
      <div className="soft-panel h-full rounded-[28px] p-4 md:p-5">
        <div className="mb-4 text-base font-extrabold text-white underline decoration-white/25 underline-offset-4">
          https://exportify.net/
        </div>

        <div className="mx-auto flex h-[230px] max-w-[190px] flex-col gap-3 rounded-[26px] border border-white/10 bg-black/40 p-4 shadow-[0_16px_40px_rgba(0,0,0,0.35)]">
          <div className="mt-2 text-center text-2xl font-black leading-tight text-white">
            Welcome back
          </div>

          <div className="rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-[11px] text-white/50">
            Email address or username
          </div>

          <div className="spotify-button rounded-full px-4 py-2 text-center text-[11px] font-black">
            Continue
          </div>

          <div className="text-center text-[11px] text-white/35">or</div>

          <div className="rounded-full border border-white/12 px-3 py-2 text-center text-[10px] text-white/75">
            Continue with Google
          </div>
          <div className="rounded-full border border-white/12 px-3 py-2 text-center text-[10px] text-white/75">
            Continue with Facebook
          </div>
          <div className="rounded-full border border-white/12 px-3 py-2 text-center text-[10px] text-white/75">
            Continue with Apple
          </div>
        </div>
      </div>
    );
  }

  if (type === "export") {
    return (
      <div className="soft-panel h-full rounded-[28px] p-4 md:p-5">
        <div className="rounded-[24px] border border-white/10 bg-black/35 p-4">
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

        <div className="mt-5 flex items-center gap-2 text-xs font-semibold text-white/45">
          <Download className="h-4 w-4" />
          Export one or more playlists from Exportify
        </div>
      </div>
    );
  }

  return (
    <div className="soft-panel h-full rounded-[28px] p-4 md:p-5">
      <div className="mx-auto flex h-full max-w-[290px] flex-col justify-between gap-4">
        <div className="rounded-[24px] border border-white/10 bg-black/35 p-4">
          <div className="mb-3 text-center text-[10px] font-black uppercase tracking-[0.22em] text-[var(--theme-accent)]">
            Find your uniqueness
          </div>

          <div className="space-y-3">
            <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-3 text-xs text-white/35">
              Upload your CSV...
            </div>
            <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-3 text-xs text-white/35">
              Add your filters...
            </div>
            <div className="spotify-button mx-auto w-fit rounded-full px-4 py-2 text-[11px] font-black">
              Find
            </div>
          </div>
        </div>

        <div className="text-center text-xl font-black leading-tight text-white">
          Upload your download and jump straight into recommendations.
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
  infoBlock,
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
        <div className="page-frame">
          <div>
            <h1 className="page-title text-5xl sm:text-6xl lg:text-7xl">
              Getting Started
            </h1>
            <p className="mt-3 max-w-2xl text-sm text-soft">
              Export your Spotify playlist with Exportify, upload the CSV, then
              move into your recommendation flow.
            </p>
          </div>

          <div className="grid min-h-0 flex-1 gap-5 xl:grid-cols-3">
            {stepCards.map((card) => (
              <div key={card.id} className="flex min-h-0 flex-col gap-4">
                <ActionButton type={card.type} label={card.buttonLabel} />

                <div className="glass-panel flex min-h-0 flex-1 flex-col rounded-[32px] p-4 md:p-5">
                  <div className="h-[260px] shrink-0 md:h-[290px]">
                    <PreviewCard type={card.type} />
                  </div>

                  <div className="flex flex-1 items-center justify-center px-3 py-4">
                    <p className="max-w-[290px] text-center text-xl font-black leading-tight text-white md:text-2xl">
                      {card.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid gap-4 xl:grid-cols-[1fr_auto]">
            <div className="glass-panel rounded-[28px] p-5">
              <div className="text-lg font-black text-white">
                {infoBlock.title}
              </div>
              <p className="mt-2 max-w-3xl text-sm text-soft">
                {infoBlock.description}
              </p>
            </div>

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
  );
}