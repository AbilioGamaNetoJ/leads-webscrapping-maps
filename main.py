import os
from pathlib import Path
from typing import Annotated
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text
from starlette.middleware.sessions import SessionMiddleware

from database.connection import engine
from database.models import AppUser, Base, Business
from routers import auth, autocomplete, export, history, search, users, webhooks
from services.auth import LoginRequired, get_current_user
from services.business_types import as_dicts

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine, tables=[Business.__table__])


def ensure_business_type_column() -> None:
    columns = {column["name"] for column in inspect(engine).get_columns("businesses")}
    if "business_type" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE businesses ADD COLUMN business_type VARCHAR"))


ensure_business_type_column()

app = FastAPI(title="Prospector de Negócios Locais — Codex Create")

session_secret = os.getenv("SESSION_SECRET_KEY")
if not session_secret:
    raise RuntimeError("SESSION_SECRET_KEY deve ser configurada antes de iniciar a aplicação.")

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    https_only=os.getenv("APP_ENV") == "production",
    same_site="lax",
    session_cookie="prospector_session",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
CurrentUser = Annotated[AppUser, Depends(get_current_user)]

app.include_router(search.router)
app.include_router(export.router)
app.include_router(history.router)
app.include_router(autocomplete.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(webhooks.router)


@app.exception_handler(LoginRequired)
async def redirect_to_login(_: Request, error: LoginRequired):
    return RedirectResponse(f"/login?{urlencode({'return_to': error.return_to})}", status_code=303)


@app.get("/")
def index(request: Request, current_user: CurrentUser):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "business_types": as_dicts(include_all=True),
            "current_user": current_user,
        },
    )
