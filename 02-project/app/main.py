from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from .config import settings
from .events import seed_from_disk
from .k8s import init_kube
from .api import router as api_router

app = FastAPI(title="Dev Envs API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(settings.static_dir), html=True), name="static")

@app.on_event("startup")
async def startup():
    init_kube()
    seed_from_disk()

@app.get("/")
async def root():
    return RedirectResponse(url="/static/") if settings.static_dir.exists() else {"ok": True}

@app.get("/healthz")
async def healthz():
    return {"ok": True}

app.include_router(api_router)