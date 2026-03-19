DROP DATABASE IF EXISTS spotyfinderdb;
CREATE DATABASE spotyfinderdb;
USE spotyfinderdb;

CREATE TABLE playlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spotify_playlist_id VARCHAR(255) UNIQUE,
    name VARCHAR(255)
);

CREATE TABLE record_labels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE
);

CREATE TABLE artists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spotify_artist_id VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    artist_name VARCHAR(255),
    image_url VARCHAR(512) NULL
);

CREATE TABLE albums (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spotify_album_id VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    release_date DATE,
    label_id INT,
    image_url VARCHAR(512) NULL,
    FOREIGN KEY (label_id) REFERENCES record_labels(id)
);

CREATE TABLE tracks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spotify_track_id VARCHAR(255) UNIQUE,
    track_uri VARCHAR(255),
    name VARCHAR(255) NULL,
    album_id INT,
    duration_ms INT,
    popularity INT,
    explicit BOOLEAN,
    spotify_url VARCHAR(512) NULL,
    preview_url VARCHAR(512) NULL,
    cover_image_url VARCHAR(512) NULL,
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
    name VARCHAR(255) UNIQUE
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