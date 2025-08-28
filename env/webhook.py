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
    user="root",       # ganti dengan user MySQL kamu
    password="",       # ganti dengan password MySQL kamu
    database="webhook_db"  # ganti dengan nama database
)
cursor = db.cursor()

# pastikan ada tabel:
# CREATE TABLE files (
#   id INT AUTO_INCREMENT PRIMARY KEY,
#   url TEXT,
#   extension VARCHAR(10),
#   filename VARCHAR(255),
#   created_at DATETIME
# );

# --- Model untuk request ---
class WebhookPayload(BaseModel):
    url: str
    extension: str

@app.post("/webhook")
async def webhook(payload: WebhookPayload):
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
            # simpan ke file
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
