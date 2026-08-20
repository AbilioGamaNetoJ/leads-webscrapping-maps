from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text

from database.connection import engine
from database.models import Base
from routers import autocomplete, export, history, search
from services.business_types import as_dicts

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)


def ensure_business_type_column() -> None:
    columns = {column["name"] for column in inspect(engine).get_columns("businesses")}
    if "business_type" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE businesses ADD COLUMN business_type VARCHAR"))


ensure_business_type_column()

app = FastAPI(title="Prospector de Negócios Locais — Codex Create")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(search.router)
app.include_router(export.router)
app.include_router(history.router)
app.include_router(autocomplete.router)


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "business_types": as_dicts()},
    )
