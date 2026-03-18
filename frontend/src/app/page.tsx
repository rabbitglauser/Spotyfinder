type Track = {
  id: number;
  track_uri: string;
  duration_ms: number;
  popularity: number;
  explicit: boolean;
  album_name: string | null;
};

async function getTracks(): Promise<Track[]> {
  try {
    const res = await fetch("http://backend:8000/api/items", {
      cache: "no-store",
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.items ?? [];
  } catch {
    return [];
  }
}

export default async function Home() {
  const tracks = await getTracks();

  return (
    <main className="min-h-screen bg-black text-white p-8">
      <h1 className="text-3xl font-bold mb-6 text-green-400">Spotyfinder — Tracks</h1>

      {tracks.length === 0 ? (
        <p className="text-zinc-400">No tracks found or backend unavailable.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-zinc-800 text-zinc-300 text-left">
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">Track URI</th>
                <th className="px-4 py-2">Album</th>
                <th className="px-4 py-2">Duration (ms)</th>
                <th className="px-4 py-2">Popularity</th>
                <th className="px-4 py-2">Explicit</th>
              </tr>
            </thead>
            <tbody>
              {tracks.map((track) => (
                <tr
                  key={track.id}
                  className="border-t border-zinc-700 hover:bg-zinc-900 transition-colors"
                >
                  <td className="px-4 py-2 text-zinc-400">{track.id}</td>
                  <td className="px-4 py-2 font-mono text-xs text-green-300">{track.track_uri}</td>
                  <td className="px-4 py-2">{track.album_name ?? "—"}</td>
                  <td className="px-4 py-2">{track.duration_ms.toLocaleString()}</td>
                  <td className="px-4 py-2">{track.popularity}</td>
                  <td className="px-4 py-2">{track.explicit ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
