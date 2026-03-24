from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.items import router as items_router
from routes.spotify import router as spotify_router
from routes.import_exportify import router as import_router
from routes.recommendations import router as recommendations_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://spotyfinder.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(items_router)
app.include_router(spotify_router)
app.include_router(import_router)
app.include_router(recommendations_router)