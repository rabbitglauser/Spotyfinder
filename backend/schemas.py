from pydantic import BaseModel, Field

class SongCreate(BaseModel):
    spotify_track_id: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    artist: str = Field(min_length=1, max_length=255)
    note: str | None = None

class SongUpdate(BaseModel):
    # Update only what you want (keep it minimal)
    note: str | None = None

class SongOut(BaseModel):
    id: int
    spotify_track_id: str
    title: str
    artist: str
    note: str | None

    class Config:
        from_attributes = True