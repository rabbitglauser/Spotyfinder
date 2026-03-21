"use client";

import React, { useState } from "react";
import useRecommendationFilters from "@/hooks/useRecommendationFilters";
import RecommendationLayout from "./RecommendationLayout";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ApiDetailItem = {
  msg?: string;
  loc?: Array<string | number>;
  type?: string;
};

type ApiMessageResponse = {
  message?: string;
  detail?: string | ApiDetailItem[];
};

function isApiDetailItem(value: unknown): value is ApiDetailItem {
  return typeof value === "object" && value !== null;
}

function isApiMessageResponse(value: unknown): value is ApiMessageResponse {
  return typeof value === "object" && value !== null;
}

function getErrorMessage(data: unknown, fallback: string): string {
  if (!data) return fallback;

  if (typeof data === "string") return data;

  if (!isApiMessageResponse(data)) return fallback;

  if (typeof data.message === "string") return data.message;
  if (typeof data.detail === "string") return data.detail;

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) =>
        isApiDetailItem(item) && typeof item.msg === "string"
          ? item.msg
          : JSON.stringify(item)
      )
      .join(" | ");
  }

  return fallback;
}

export default function Recommendation() {
  const [filters, setFilters] = useRecommendationFilters();

  const [playlistName, setPlaylistName] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [enrichWithSpotify, setEnrichWithSpotify] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setUploadMessage(null);
    setUploadError(null);
  };

  const handleUpload = async () => {
    const trimmedPlaylistName = playlistName.trim();

    if (!trimmedPlaylistName) {
      setUploadError("Please enter a playlist name.");
      setUploadMessage(null);
      return;
    }

    if (!selectedFile) {
      setUploadError("Please choose a CSV file first.");
      setUploadMessage(null);
      return;
    }

    try {
      setIsUploading(true);
      setUploadError(null);
      setUploadMessage(null);

      const formData = new FormData();
      formData.append("file", selectedFile, selectedFile.name);
      formData.append("playlist_name", trimmedPlaylistName);
      formData.append(
        "enrich_with_spotify",
        enrichWithSpotify ? "true" : "false"
      );

      const response = await fetch(
        `${API_BASE_URL}/api/import/exportify?playlist_name=${encodeURIComponent(
          trimmedPlaylistName
        )}`,
        {
          method: "POST",
          body: formData,
        }
      );

      let data: unknown = null;
      const contentType = response.headers.get("content-type") ?? "";

      if (contentType.includes("application/json")) {
        data = await response.json().catch(() => null);
      } else {
        const text = await response.text().catch(() => "");
        data = text ? { message: text } : null;
      }

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data, "Upload failed. Please try again.")
        );
      }

      let successMessage = "Upload completed successfully.";

      if (isApiMessageResponse(data)) {
        if (typeof data.message === "string") {
          successMessage = data.message;
        } else if (typeof data.detail === "string") {
          successMessage = data.detail;
        }
      }

      setUploadMessage(successMessage);
      setUploadError(null);
    } catch (error: unknown) {
      const message =
        error instanceof Error ? error.message : "Upload failed.";
      setUploadError(message);
      setUploadMessage(null);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <RecommendationLayout
      filters={filters}
      setFilters={setFilters}
      playlistName={playlistName}
      setPlaylistName={setPlaylistName}
      selectedFile={selectedFile}
      enrichWithSpotify={enrichWithSpotify}
      setEnrichWithSpotify={setEnrichWithSpotify}
      isUploading={isUploading}
      uploadMessage={uploadMessage}
      uploadError={uploadError}
      onFileChange={handleFileChange}
      onUpload={handleUpload}
    />
  );
}