
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse


from src.configuration.config import APP_ENV, PUBLIC_DIR, SRC_DIR


from src.configuration.logger import setup_logging

from src.routes import api_routers


logger = setup_logging()

print(APP_ENV)
app = FastAPI(
    title="Webhook Scraping API",
    description="API untuk menangani webhook dan proses scraping",
    version="1.0.0",
)





for router in api_routers:
    app.include_router(router)




print(f"🎯 Mounted {len(api_routers)} API routes")



@app.on_event("shutdown")
async def shutdown_event():
    """Jalankan saat aplikasi berhenti"""
    logger.info("Application shutting down")




@app.get("/health")
async def health_check():
    return {"status": "healthy"}








