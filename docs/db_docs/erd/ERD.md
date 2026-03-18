**Quick explanation for the ERD**

The ERD has been created with the web-service "dbdiagram.io" via it's SQL implementation feature.

# Data duplication avoidance
- "track_artists" to allow multiple artists per track
- "artist_genres" to allow multiple genres per artist
- "audio-features" to allow storing audio analysis separately
- "playlist_tracks" to allow storing metadata separately

# The written script will be provided below

Table playlists {
  id integer [primary key, increment]
  playlist_id varchar
  name varchar
}


Table artists {
  id integer [primary key, increment]
  artist_id varchar
  name varchar
  artist_name varchar
}

Table albums {
  id integer [primary key, increment]
  album_id varchar
  name varchar
  release_date date
  label_id integer
}

Table record_labels {
  id integer [primary key, increment]
  name varchar
}

Table tracks {
  id int [primary key, increment]
  track_uri varchar
  album_id integer
  duration_ms integer
  popularity integer
  explicit boolean
}

Table audio_features {
  track_id integer [primary key]
  danceability float
  energy float
  key integer
  loudness float
  mode integer
  speechiness float
  acousticness float
  instrumentalness float
  liveness float
  valence float
  tempo float
  time_signature integer
}

Table genres {
id integer [primary key, increment]
name varchar
}

Table artist_genres {
  artist_id integer
  genre_id integer
}

Table track_artists {
  track_id integer
  artist_id integer
}
Table playlist_tracks {
  playlist_id integer
  track_id integer
  added_at timestamp
}

Ref: albums.label_id > record_labels.id
Ref: tracks.album_id > albums.id
Ref: audio_features.track_id > tracks.id
Ref: artist_genres.artist_id > artists.id
Ref: artist_genres.genre_id > genres.id
Ref: track_artists.track_id > tracks.id
Ref: track_artists.artist_id > artists.id
Ref: playlist_tracks.playlist_id > playlists.id
Ref: playlist_tracks.track_id > tracks.id






