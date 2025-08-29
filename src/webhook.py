import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
import aiohttp
import aiofiles
import os
import mysql.connector
from datetime import datetime

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

# --- konfigurasi MySQL ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bm5#2025hH",
    database="webhook_db"
)
cursor = db.cursor()

# --- Model untuk request ---
class WebhookPayload(BaseModel):
    url: str
    extension: str

# --- GET endpoint untuk verifikasi webhook ---
@app.get("/webhook")
async def webhook_get():
    logger.info("Received GET request on /webhook")
    return {"message": "Webhook GET endpoint is alive!"}

# --- POST endpoint untuk menerima data ---
@app.post("/webhook")
async def webhook_post(payload: WebhookPayload):
    logger.info(f"Received POST payload: {payload.dict()}")

    file_url = payload.url
    extension = payload.extension
    filename = f"file.{extension}"
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
        sql = "INSERT INTO files (url, extension, filename, created_at) VALUES (%s, %s, %s, %s)"
        val = (file_url, extension, filename, now)
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
        return {"error": str(e)}
