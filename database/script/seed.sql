USE spotyfinderdb;

INSERT INTO playlists (id, spotify_playlist_id, name) VALUES
    (1, 'pl-those-eyes-demo', 'Those Eyes Demo Playlist');

INSERT INTO record_labels (id, name) VALUES
    (1, '199x'),
    (2, 'Columbia'),
    (3, 'BMG Rights Management (US) LLC'),
    (4, 'Cube Entertainment');

INSERT INTO artists (id, spotify_artist_id, name, artist_name, image_url) VALUES
    (1, 'artist-new-west', 'New West', 'New West', NULL),
    (2, 'artist-the-neighbourhood', 'The Neighbourhood', 'The Neighbourhood', NULL),
    (3, 'artist-you-me-at-six', 'You Me At Six', 'You Me At Six', NULL),
    (4, 'artist-gidle', 'i-dle', 'i-dle', NULL);

INSERT INTO albums (id, spotify_album_id, name, release_date, label_id, image_url) VALUES
    (1, 'album-those-eyes', 'Those Eyes', '2019-05-10', 1, NULL),
    (2, 'album-wiped-out', 'Wiped Out!', '2015-10-30', 2, NULL),
    (3, 'album-night-people', 'Night People', '2017-01-06', 3, NULL),
    (4, 'album-i-feel', 'I feel', '2023-05-15', 4, NULL);

INSERT INTO tracks (
    id,
    spotify_track_id,
    track_uri,
    name,
    album_id,
    duration_ms,
    popularity,
    explicit,
    spotify_url,
    preview_url,
    cover_image_url
) VALUES
    (1, '2GThBgzZoZfz0lx1JjBwfe', 'spotify:track:2GThBgzZoZfz0lx1JjBwfe', 'Those Eyes', 1, 220750, 1, FALSE, NULL, NULL, NULL),
    (2, '5Ma3BlNVDtn3JiwMEafSaq', 'spotify:track:5Ma3BlNVDtn3JiwMEafSaq', 'Daddy Issues', 2, 262323, 59, FALSE, NULL, NULL, NULL),
    (3, '6J0xeqjdpsUH0W1YBCmD1L', 'spotify:track:6J0xeqjdpsUH0W1YBCmD1L', 'Night People', 3, 271306, 0, FALSE, NULL, NULL, NULL),
    (4, '38MKW2tQHtyO8djIOKlEFF', 'spotify:track:38MKW2tQHtyO8djIOKlEFF', 'Queencard', 4, 162786, 2, FALSE, NULL, NULL, NULL);

INSERT INTO audio_features (
    track_id,
    danceability,
    energy,
    `key`,
    loudness,
    mode,
    speechiness,
    acousticness,
    instrumentalness,
    liveness,
    valence,
    tempo,
    time_signature
) VALUES
    (1, 0.597, 0.351, 4, -8.043, 1, 0.0281, 0.727, 0.0000386, 0.319, 0.243, 119.948, 3),
    (2, 0.249, 0.492, 2, -7.108, 0, 0.0352, 0.755, 0, 0.243, 0.34, 54.134, 4),
    (3, 0.557, 0.532, 2, -6.467, 1, 0.0307, 0.16, 0.00000442, 0.0999, 0.122, 103.992, 4),
    (4, 0.591, 0.92, 5, -3.699, 1, 0.185, 0.0524, 0, 0.0467, 0.545, 165.087, 4);

INSERT INTO genres (id, name) VALUES
    (1, 'pop punk'),
    (2, 'k-pop');

INSERT INTO artist_genres (artist_id, genre_id) VALUES
    (3, 1),
    (4, 2);

INSERT INTO track_artists (track_id, artist_id) VALUES
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4);

INSERT INTO playlist_tracks (playlist_id, track_id, added_at) VALUES
    (1, 1, '2023-06-01 12:12:47'),
    (1, 2, '2023-06-01 12:14:52'),
    (1, 3, '2023-06-01 12:19:59'),
    (1, 4, '2023-06-02 16:53:44');