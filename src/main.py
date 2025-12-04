import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, literal, or_
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from src.configuration.config import APP_ENV, PUBLIC_DIR, SRC_DIR

# from src.configuration.database import SessionLocal
from src.configuration.database import SessionLocal
from src.configuration.logger import setup_logging
from src.configuration.static_config import setup_static_files
from src.models.hak_akses_models import HakAkses
from src.models.menu_models import Menu
from src.models.user_models import User
from src.routes import api_routers, page_routers
from src.routes.api import webhook
from src.services.sessions_utils import clear_session

logger = setup_logging()

print(APP_ENV)
app = FastAPI(
    title="Webhook Scraping API",
    description="API untuk menangani webhook dan proses scraping",
    version="1.0.0",
)

setup_static_files(app)

templates = Jinja2Templates(directory="src/templates")

for router in api_routers:
    app.include_router(router)


for router in page_routers:
    app.include_router(router)

print(f"🎯 Mounted {len(api_routers)} API routes")
print(f"🎯 Mounted {len(page_routers)} Page routes")


@app.on_event("shutdown")
async def shutdown_event():
    """Jalankan saat aplikasi berhenti"""
    logger.info("Application shutting down")


@app.get("/")
async def root():
    return {"message": "Welcome to Webhook Scraping API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/logout")
async def logout(request: Request):
    clear_session(request)
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    theme = request.session.get("theme", "light")
    return templates.TemplateResponse(
        "login.html", {"request": request, "theme": theme}
    )


@app.get("/set-theme/{mode}")
async def set_theme(request: Request, mode: str):
    if mode in ["dark", "light"]:
        request.session["theme"] = mode
    return RedirectResponse(url="/login", status_code=303)


@app.middleware("http")
async def check_login(request: Request, call_next):
    """
    Middleware untuk mengecek:
    - Login user
    - Hak akses halaman menu
    - Melewati API endpoints
    - Melewati DevTools / static / login paths
    """
    allow_paths = [
        "/public",
        "/login",
        "/logout",
        "/static",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/form",
        "/phpmyadmin",
        "/set-theme",
        "/api",
    ]

    path = request.url.path.rstrip("/")

    if any(path.startswith(p) for p in allow_paths) or request.method in [
        "POST",
        "DELETE",
        "PUT",
    ]:
        return await call_next(request)

    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    print(path)

    db: Session = SessionLocal()
    try:
        akses = (
            db.query(HakAkses)
            .join(Menu, HakAkses.id_menu == Menu.id)
            .filter(
                HakAkses.id_user == user_id,
                HakAkses.lihat == True,
                Menu.route != "#",
            )
            .all()
        )
    finally:
        is_allowed = any(path.startswith(a.menu.route.rstrip("/")) for a in akses)
        db.close()

    if not is_allowed:
        return JSONResponse(content={"error": "Not Allowed"}, status_code=403)

    response = await call_next(request)
    return response


app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")
