import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiohttp
import aiofiles
import os
import mysql.connector
from datetime import datetime
import uuid

# --- Konfigurasi logging ---
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "app.log")),      # log umum
        logging.FileHandler(os.path.join(log_dir, "error.log")),    # log error
        logging.StreamHandler()  # tetap tampil di terminal / systemd journal
    ]
)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI()

# --- Middleware untuk logging request/response ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # ms
    logger.info(
        f"{request.client.host} {request.method} {request.url.path} "
        f"Status={response.status_code} Time={process_time:.2f}ms"
    )
    return response

# --- konfigurasi MySQL ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bm5#2025hH",
    database="webhook_db"
)
cursor = db.cursor()

class WebhookPayload(BaseModel):
    url: str
    extension: str
    pengirim: str
    message: str
    name: str

# --- GET endpoint untuk verifikasi webhook ---
@app.get("/webhook")
async def webhook_get():
    logger.info("Received GET request on /webhook")
    return {"message": "Webhook GET endpoint is alive!"}

@app.get("/webhook/flexible")
async def webhook_get():
    logger.info("Received GET request on /webhook")
    return {"message": "Webhook GET endpoint is alive!"}


@app.post("/webhook/flexible")
async def webhook_flexible(req: Request):
    """
    Flexible mode: mirip Express req.body
    Bisa terima request JSON apapun, tanpa validasi.
    """
    try:
        body = await req.json()
        logger.info(f"[FLEXIBLE] Request received: {body}")
        return {
            "status": "ok",
            "mode": "flexible",
            "data": body
        }
    except Exception as e:
        logger.exception("[FLEXIBLE] Error parsing request body")
        return {"error": str(e)}


# --- POST endpoint untuk menerima data ---
@app.post("/webhook")
async def webhook_post(payload: Request):
    body = await payload.json()
    logger.info(f"Received POST payload: {body}")

    file_url = body.get("url", "").strip()
    extension = body.get("extension", "").strip()
    nama = body.get("name", "").strip()
    message = body.get("message", "").strip()
    nomer = body.get("pengirim", "").strip()

    # jika tidak ada file, skip proses
    if not file_url or not extension:
        logger.info("No file detected, skipping DB insert")
        return {"message": "No file to process, skipping database."}

    filename = f"{uuid.uuid4().hex}.{extension}"
    filepath = os.path.join("public", filename)
    now = datetime.now()

    # download file
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to download file: {file_url}, status={resp.status}")
                    return {"error": f"Failed to download file, status {resp.status}"}
                data = await resp.read()
                async with aiofiles.open(filepath, "wb") as f:
                    await f.write(data)
        logger.info(f"File downloaded and saved: {filepath}")
    except Exception as e:
        logger.exception("Error downloading file")
        return JSONResponse(status_code=500, content={"error": str(e)})

    # simpan ke database
    try:
        sql = """
INSERT INTO files (nomer, nama, message, url, extension, filename, created_at)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
        val = (nomer, nama, message, file_url, extension, filename, now)
        cursor.execute(sql, val)
        db.commit()

        logger.info(f"DB entry created, ID: {cursor.lastrowid}")
        return {
            "message": "Webhook processed successfully",
            "saved_file": filepath,
            "db_id": cursor.lastrowid
        }

    except Exception as e:
        logger.exception("Unhandled error saving to DB")
        return JSONResponse(status_code=500, content={"error": str(e)})


# --- Endpoint untuk mengetes error logging ---
@app.get("/debug-error")
async def debug_error():
    try:
        # contoh error (bagi 1 dengan 0)
        1 / 0
    except Exception as e:
        logger.exception("Debug error endpoint triggered!")
        return {"error": str(e)}
