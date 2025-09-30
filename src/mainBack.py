import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.configuration.logger import setup_logging
from src.configuration.config import SRC_DIR,PUBLIC_DIR, APP_ENV
from src.configuration.static_config import setup_static_files
from starlette.middleware.sessions import SessionMiddleware
from src.routes.api import webhook
from src.routes import api_routers, page_routers
from src.services.sessions_utils import clear_session
from src.models.menu_models import Menu
from src.models.hak_akses_models import HakAkses
from src.configuration.database import SessionLocal
from sqlalchemy import or_
from sqlalchemy.orm import Session
from src.models.user_models import User
from sqlalchemy import func
from sqlalchemy import literal
logger = setup_logging()

print(APP_ENV)
app = FastAPI(
    title="Webhook Scraping API",
    description="API untuk menangani webhook dan proses scraping",
    version="1.0.0"
)

setup_static_files(app)

# app.include_router(webhook.router, prefix="/api/v1")
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

# @app.middleware("http")
# async def check_login(request: Request, call_next):
#     # Daftar path yang boleh dilewati tanpa cek hak akses
#     allow_paths = ["/login", "/logout", "/static", "/.well-known",  "/user/delete", "/docs#"]

#     path = request.url.path.rstrip("/")  # normalisasi trailing slash

#     # Jika path termasuk yang dilewati, langsung lanjut
#     if any(path.startswith(p) for p in allow_paths):
#         return await call_next(request)

#     # Ambil user dari session
#     user_id = request.session.get("user_id")
#     if not user_id:
#         return RedirectResponse(url="/login", status_code=303)

#     # Cek hak akses user
#     db: Session = SessionLocal()
#     try:
#         allowed = (
#     db.query(HakAkses)
#     .join(Menu, HakAkses.id_menu == Menu.id)
#     .filter(
#         HakAkses.id_user == user_id,
#         HakAkses.lihat == True,
#         Menu.route != "#",
#         Menu.route.like(f"{path}%")  # mengabaikan trailing slash
#     )
#     .first()
# )
#     finally:
#         db.close()

#     if not allowed:
#         # Bisa return JSONResponse untuk AJAX/fetch, bukan 505
#         if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.method in ["POST", "DELETE", "PUT"]:
#             return JSONResponse(status_code=403, content={"message": "Akses ditolak"})
#         # Untuk browser biasa, redirect ke home
#         return RedirectResponse(url="/", status_code=303)

#     # Jika user punya akses
#     response = await call_next(request)
#     return response

@app.middleware("http")
async def check_login(request: Request, call_next):
    """
    Middleware untuk mengecek:
    - Login user
    - Hak akses halaman menu
    - Melewati API endpoints
    - Melewati DevTools / static / login paths
    """
    # Path yang dilewati tanpa cek hak akses
    allow_paths = [
        "/public",
    "/login",
    "/logout",
    "/static",
    "/docs",         # Swagger UI
    "/redoc",        # Redoc UI
    "/openapi.json",
    "/form",
    "/phpmyadmin" # OpenAPI schema
]

    path = request.url.path.rstrip("/")  

   
    if any(path.startswith(p) for p in allow_paths) or request.method in ["POST", "DELETE", "PUT"]:
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

    #

    if not is_allowed:
        return JSONResponse(content={"error": "Not Allowed"}, status_code=403)


    # User punya akses, lanjutkan request
    response = await call_next(request)
    return response

app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")