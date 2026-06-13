from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.include_router(api_router, prefix=settings.api_prefix)

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
ASSETS_DIR = FRONTEND_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="frontend-assets")


@app.get("/", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
async def dashboard() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
