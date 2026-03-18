"use client";

import React from "react";
import GettingStartedLayout, {
  GettingStartedInfoBlock,
  GettingStartedStepCard,
} from "./getting_started_layout";

const stepCards: GettingStartedStepCard[] = [
  {
    id: 1,
    buttonLabel: "Log Into Exportify",
    title: "Log In",
    description:
      "Log into Exportify with your Spotify account so you can export one or more playlists.",
    type: "login",
  },
  {
    id: 2,
    buttonLabel: "Export your Playlist",
    title: "Export",
    description:
      "Export one or more playlists and keep the data ready for upload into your recommendation flow.",
    type: "export",
  },
  {
    id: 3,
    buttonLabel: "Upload your Download",
    title: "Upload",
    description:
      "Upload your exported file and move into the search flow with your own playlist data.",
    type: "upload",
  },
];

const infoBlock: GettingStartedInfoBlock = {
  title: "Base frontend flow",
  description:
    "This is only dummy content for now. Later this can show auth state, selected playlist count, upload progress, or helpful onboarding text from your backend.",
};

export default function GettingStarted() {
  return <GettingStartedLayout stepCards={stepCards} infoBlock={infoBlock} />;
}