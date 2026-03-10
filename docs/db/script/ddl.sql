DROP DATABASE IF EXISTS spotifydb;
CREATE DATABASE spotifydb;
USE spotifydb;

CREATE TABLE playlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id VARCHAR(255),
    name VARCHAR(255)
);

CREATE TABLE record_labels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE artists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artist_id VARCHAR(255),
    name VARCHAR(255),
    artist_name VARCHAR(255)
);

CREATE TABLE albums (
    id INT AUTO_INCREMENT PRIMARY KEY,
    album_id VARCHAR(255),
    name VARCHAR(255),
    release_date DATE,
    label_id INT,
    FOREIGN KEY (label_id) REFERENCES record_labels(id)
);

CREATE TABLE tracks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    track_uri VARCHAR(255),
    album_id INT,
    duration_ms INT,
    popularity INT,
    explicit BOOLEAN,
    FOREIGN KEY (album_id) REFERENCES albums(id)
);

CREATE TABLE audio_features (
    track_id INT PRIMARY KEY,
    danceability FLOAT,
    energy FLOAT,
    `key` INT,
    loudness FLOAT,
    mode INT,
    speechiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    tempo FLOAT,
    time_signature INT,
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);

CREATE TABLE genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE artist_genres (
    artist_id INT,
    genre_id INT,
    PRIMARY KEY (artist_id, genre_id),
    FOREIGN KEY (artist_id) REFERENCES artists(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id)
);

CREATE TABLE track_artists (
    track_id INT,
    artist_id INT,
    PRIMARY KEY (track_id, artist_id),
    FOREIGN KEY (track_id) REFERENCES tracks(id),
    FOREIGN KEY (artist_id) REFERENCES artists(id)
);

CREATE TABLE playlist_tracks (
    playlist_id INT,
    track_id INT,
    added_at TIMESTAMP,
    PRIMARY KEY (playlist_id, track_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);