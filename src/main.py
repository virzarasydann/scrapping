import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from src.configuration.logger import setup_logging
from src.configuration.config import SRC_DIR,PUBLIC_DIR
from src.configuration.static_config import setup_static_files

from src.routes.api import webhook
from src.routes import api_routers, page_routers

logger = setup_logging()


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

