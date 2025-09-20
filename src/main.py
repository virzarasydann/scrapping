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
    return {"status": "success"}
@app.middleware("http")
async def check_login(request: Request, call_next):
    # Boleh diakses tanpa login
    allow_paths = ["/login", "/logout", "/static", "/phpmyadmin"]

    if not any(request.url.path.startswith(path) for path in allow_paths):
        if "user_id" not in request.session:
            return RedirectResponse(url="/login", status_code=303)

    # kalau sudah login atau path bebas → lanjut
    response = await call_next(request)
    return response
app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")