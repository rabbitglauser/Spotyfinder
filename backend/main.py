from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal, engine
from .models import SavedSong
from .schemas import SongCreate, SongUpdate, SongOut
from .db import Base

app = FastAPI(title="Spotyfinder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/songs", response_model=SongOut, status_code=201)
def create_song(payload: SongCreate, db: Session = Depends(get_db)):
    song = SavedSong(**payload.model_dump())
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


@app.get("/songs", response_model=list[SongOut])
def list_songs(db: Session = Depends(get_db)):
    songs = db.scalars(select(SavedSong).order_by(SavedSong.id.desc())).all()
    return songs


@app.put("/songs/{song_id}", response_model=SongOut)
def update_song(song_id: int, payload: SongUpdate, db: Session = Depends(get_db)):
    song = db.get(SavedSong, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    song.note = payload.note
    db.commit()
    db.refresh(song)
    return song


@app.delete("/songs/{song_id}", status_code=204)
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.get(SavedSong, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)
    db.commit()
    return None
