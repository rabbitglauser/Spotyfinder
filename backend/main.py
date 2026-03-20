from fastapi import FastAPI
from routes.items import router as items_router
from routes.spotify import router as spotify_router
from routes.import_exportify import router as import_router

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(items_router)
app.include_router(spotify_router)
app.include_router(import_router)