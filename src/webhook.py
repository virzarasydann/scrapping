from fastapi import FastAPI, Request
from pydantic import BaseModel
import aiohttp
import aiofiles
import os
import mysql.connector
from datetime import datetime

app = FastAPI()

# --- konfigurasi MySQL ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bm5#2025hH",
    database="webhook_db"
)
cursor = db.cursor()

# --- Model untuk request POST ---
class WebhookPayload(BaseModel):
    url: str
    extension: str

# --- GET: biasanya dipakai provider untuk test/verify ---
@app.get("/webhook")
async def webhook_get():
    return {"message": "Webhook GET endpoint is alive!"}

# --- POST: untuk kirim data sebenarnya ---
@app.post("/webhook")
async def webhook_post(payload: WebhookPayload):
    file_url = payload.url
    extension = payload.extension
    filename = f"file.{extension}"
    filepath = os.path.join("public", filename)

    # download file
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            if resp.status != 200:
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

    return {
        "message": "Webhook processed successfully",
        "saved_file": filepath,
        "db_id": cursor.lastrowid
    }
