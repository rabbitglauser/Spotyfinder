"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

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

function PreviewCard({ type }: { type: GettingStartedStepCard["type"] }) {
  if (type === "login") {
    return (
      <div className="h-full rounded-[28px] border border-white/10 bg-white/10 p-4">
        {/* LOGINPREVIEW START */}
        <div className="mb-4 text-xl font-extrabold text-white">
          https://exportify.net/
        </div>

        <div className="mx-auto flex max-w-[180px] flex-col gap-3 rounded-[24px] border border-white/10 bg-black/40 p-4 text-white/70">
          <div className="text-center text-2xl font-bold text-white">
            Welcome back
          </div>
          <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs">
            Email address or username
          </div>
          <div className="rounded-full bg-[#1ed760] px-4 py-2 text-center text-xs font-bold text-black">
            Continue
          </div>
          <div className="text-center text-xs text-white/40">or</div>
          <div className="rounded-full border border-white/15 px-3 py-2 text-center text-[11px]">
            Continue with Google
          </div>
          <div className="rounded-full border border-white/15 px-3 py-2 text-center text-[11px]">
            Continue with Facebook
          </div>
          <div className="rounded-full border border-white/15 px-3 py-2 text-center text-[11px]">
            Continue with Apple
          </div>
        </div>
        {/* LOGINPREVIEW END */}
      </div>
    );
  }

  if (type === "export") {
    return (
      <div className="h-full rounded-[28px] border border-white/10 bg-white/10 p-4">
        {/* EXPORTPREVIEW START */}
        <div className="rounded-[24px] border border-white/10 bg-black/35 p-4">
          <div className="mb-4 flex items-center justify-between text-sm text-white/60">
            <span>Tracks</span>
            <span className="rounded-lg border border-white/10 px-3 py-1 text-xs">
              Export All
            </span>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-3 text-white/70">
              <span>2385</span>
              <span className="rounded-lg bg-green-600 px-3 py-1 text-xs font-bold text-white">
                Export
              </span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-3 text-white/70">
              <span>402</span>
              <span className="rounded-lg bg-green-600 px-3 py-1 text-xs font-bold text-white">
                Export
              </span>
            </div>
          </div>
        </div>
        {/* EXPORTPREVIEW END */}
      </div>
    );
  }

  return (
    <div className="h-full rounded-[28px] border border-white/10 bg-white/10 p-4">
      {/* UPLOADPREVIEW START */}
      <div className="mx-auto mb-5 flex h-28 max-w-[190px] items-center justify-center rounded-[24px] border border-white/10 bg-black/40 text-center text-sm font-bold text-[#19c819]">
        Find your uniqueness
      </div>
      <div className="mx-auto max-w-[240px] text-center text-2xl font-extrabold leading-tight text-white">
        Upload your download into the search area and find tracks that fit you.
      </div>
      {/* UPLOADPREVIEW END */}
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
  if (type === "login") {
    return (
      <a
        href="https://exportify.net/"
        target="_blank"
        rel="noreferrer"
        className="inline-flex justify-center rounded-full bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 text-lg font-bold text-white shadow-lg shadow-green-700/30 transition hover:scale-[1.02]"
      >
        {label}
      </a>
    );
  }

  if (type === "export") {
    return (
      <a
        href="https://exportify.net/"
        target="_blank"
        rel="noreferrer"
        className="inline-flex justify-center rounded-full bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 text-lg font-bold text-white shadow-lg shadow-green-700/30 transition hover:scale-[1.02]"
      >
        {label}
      </a>
    );
  }

  return (
    <Link
      href="/find-your-uniqueness"
      className="inline-flex justify-center rounded-full bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 text-lg font-bold text-white shadow-lg shadow-green-700/30 transition hover:scale-[1.02]"
    >
      {label}
    </Link>
  );
}

export default function GettingStartedLayout({
  stepCards,
  infoBlock,
}: GettingStartedLayoutProps) {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#030303] text-white">
      <BackgroundBlobs />

      <div className="relative z-10 flex min-h-screen w-full flex-col px-6 py-8 md:px-10 lg:px-14">
        {/* HEADER START */}
        <div className="mb-8">
          <h1 className="text-5xl font-black tracking-tight text-[#19c819] sm:text-6xl md:text-7xl lg:text-8xl">
            Getting Started
          </h1>
        </div>
        {/* HEADER END */}

        {/* STEPCARDS START */}
        <div className="grid flex-1 gap-6 lg:grid-cols-3 items-stretch">
          {stepCards.map((card) => (
            <div key={card.id} className="flex h-full flex-col gap-4">
              <ActionButton type={card.type} label={card.buttonLabel} />

              <div className="flex h-full min-h-[540px] flex-col rounded-[32px] border border-white/10 bg-white/10 p-4 shadow-2xl backdrop-blur-xl">
                <div className="h-[340px] shrink-0">
                  <PreviewCard type={card.type} />
                </div>

                <div className="flex flex-1 items-center justify-center px-4">
                  <p className="max-w-[280px] text-center text-2xl font-extrabold leading-tight text-white">
                    {card.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
        {/* STEPCARDS END */}

        {/* INFOBLOCK START */}
        <div className="mt-8 rounded-[32px] bg-gradient-to-r from-green-700/90 to-green-800/40 p-6 backdrop-blur-xl">
          <div className="text-xl font-black text-white">{infoBlock.title}</div>
          <p className="mt-2 max-w-3xl text-sm text-white/75">
            {infoBlock.description}
          </p>
        </div>
        {/* INFOBLOCK END */}

        {/* CONTINUEBUTTON START */}
        <div className="mt-4 flex justify-end">
          <Link
            href="/find-your-uniqueness"
            className="inline-flex items-center gap-2 rounded-full px-4 py-3 text-xl font-bold text-white transition hover:translate-x-1"
          >
            Continue <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
        {/* CONTINUEBUTTON END */}
      </div>
    </div>
  );
}