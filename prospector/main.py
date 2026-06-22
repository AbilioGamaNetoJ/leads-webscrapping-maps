from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import search, export, history, autocomplete
from database.connection import engine
from database.models import Base

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prospector de Negócios Locais — Codex Create")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(search.router)
app.include_router(export.router)
app.include_router(history.router)
app.include_router(autocomplete.router)


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
