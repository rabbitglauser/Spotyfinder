from fastapi import APIRouter, File, Form, UploadFile

from services.import_service import import_exportify_file

router = APIRouter()


@router.post("/api/import/exportify")
async def import_exportify_csv(
    file: UploadFile = File(...),
    playlist_name: str = Form(...),
    enrich_with_spotify: bool = Form(True),
):
    return await import_exportify_file(
        file=file,
        playlist_name=playlist_name,
        enrich_with_spotify=enrich_with_spotify,
    )