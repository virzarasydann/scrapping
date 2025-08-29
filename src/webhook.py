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
async def webhook_post(payload: WebhookPayload):
    logger.info(f"Received POST payload: {payload.dict()}")

    file_url = payload.url
    extension = payload.extension
    nama = payload.name
    message = payload.message
    nomer = payload.pengirim
    filename = f"{uuid.uuid4().hex}.{extension}"
    filepath = os.path.join("public", filename)

    try:
        # download file
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to download file: {file_url}, status={resp.status}")
                    return {"error": f"Failed to download file, status {resp.status}"}
                data = await resp.read()
                async with aiofiles.open(filepath, "wb") as f:
                    await f.write(data)

        # simpan metadata ke database
        now = datetime.now()
        sql = "INSERT INTO files (nomer,nama,message,url, extension, filename, created_at) VALUES (%s, %s, %s, %s)"
        val = (nomer,nama,message,file_url, extension, filename, now)
        cursor.execute(sql, val)
        db.commit()

        logger.info(f"File saved: {filepath}, DB ID: {cursor.lastrowid}")
        return {
            "message": "Webhook processed successfully",
            "saved_file": filepath,
            "db_id": cursor.lastrowid
        }

    except Exception as e:
        logger.exception("Unhandled error in webhook_post")
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
