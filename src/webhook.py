import logging
import time
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiohttp
import aiofiles
import os
import mysql.connector
from datetime import datetime
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from src.configuration.config import get_config
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.orm import Session
from src.configuration.database import get_db
from src.models.files_models import File
from src.models.listeners_models import Listener



BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
PUBLIC_DIR.mkdir(exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates" / "pages")
app.mount("/UI", StaticFiles(directory=BASE_DIR / "templates" / "static" / "UI"), name="UI")
app.mount("/assets", StaticFiles(directory=BASE_DIR / "templates" / "static" / "assets"), name="assets")
app.mount("/css", StaticFiles(directory=BASE_DIR / "templates" / "static" / "css"), name="css")
app.mount("/docs", StaticFiles(directory=BASE_DIR / "templates" / "static" / "docs"), name="docs")
app.mount("/examples", StaticFiles(directory=BASE_DIR / "templates" / "static" / "examples"), name="examples")
app.mount("/forms", StaticFiles(directory=BASE_DIR / "templates" / "static" / "forms"), name="forms")
app.mount("/generate", StaticFiles(directory=BASE_DIR / "templates" / "static" / "generate"), name="generate")
app.mount("/js", StaticFiles(directory=BASE_DIR / "templates" / "static" / "js"), name="js")
app.mount("/layout", StaticFiles(directory=BASE_DIR / "templates" / "static" / "layout"), name="layout")
app.mount("/tables", StaticFiles(directory=BASE_DIR / "templates" / "static" / "tables"), name="tables")
app.mount("/widgets", StaticFiles(directory=BASE_DIR / "templates" / "static" / "widgets"), name="widgets")
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  
    logger.info(
        f"{request.client.host} {request.method} {request.url.path} "
        f"Status={response.status_code} Time={process_time:.2f}ms"
    )
    return response






class WebhookPayload(BaseModel):
    url: str
    extension: str
    pengirim: str
    message: str
    name: str
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("dashboard/index.html", {"request": request})

@app.get("/inbox", response_class=HTMLResponse)
async def inbox(request: Request, db: Session = Depends(get_db)):
    messages = db.query(File).all()
    return templates.TemplateResponse(
        "inbox/index.html",
        {"request": request, "messages": messages}
    )

@app.get("/dashboard/v2", response_class=HTMLResponse)
async def dashboardv2(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})


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



@app.post("/webhook")
async def webhook_post(payload: Request, db: Session = Depends(get_db)):
    body = await payload.json()
    logger.info(f"Received POST payload: {body}")

    file_url = body.get("url", "").strip()
    extension = body.get("extension", "").strip()
    nama = body.get("name", "").strip()
    message = body.get("message", "").strip()
    nomer = body.get("pengirim", "").strip()
    lokasi = body.get("location", "").strip()

    
    if "#LAPOR" in message.upper():
        listener = db.query(Listener).filter(Listener.nomer == nomer).first()
        if listener:
            listener.aktif = True
            listener.started_at = datetime.now()
            listener.ended_at = None
            logger.info(f"Listener diaktifkan kembali untuk nomor {nomer}")
        else:
            listener = Listener(nomer=nomer, aktif=True)
            db.add(listener)
            logger.info(f"Listener baru dibuat untuk nomor {nomer}")
        db.commit()
        return {"message": f"Listener aktif untuk {nomer}"}

   
    if "#SELESAI" in message.upper():
        listener = db.query(Listener).filter(Listener.nomer == nomer, Listener.aktif == True).first()
        if listener:
            listener.aktif = False
            listener.ended_at = datetime.now()
            db.commit()
            logger.info(f"Listener dinonaktifkan untuk nomor {nomer}")
            return {"message": f"Listener dimatikan untuk {nomer}"}
        else:
            logger.info(f"Tidak ada listener aktif untuk {nomer} yang bisa dimatikan")
            return {"message": f"Tidak ada listener aktif untuk {nomer}"}

    
    listener = db.query(Listener).filter(Listener.nomer == nomer, Listener.aktif == True).first()
    if not listener:
        logger.info(f"Tidak ada listener aktif untuk {nomer}, abaikan pesan")
        return {"message": "Listener tidak aktif, pesan diabaikan."}

    
    cleaned_message = message.strip()

    if not ((file_url and extension) or lokasi or cleaned_message):
        logger.info("Tidak ada file, lokasi, atau pesan yang valid")
        return {"message": "Tidak ada data valid, skip database."}

    filename = None
    filepath = None

    if file_url and extension:
        filename = f"{uuid.uuid4().hex}.{extension}"
        filepath = os.path.join(PUBLIC_DIR, filename)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status != 200:
                        logger.error(f"Gagal download file: {file_url}, status={resp.status}")
                        return {"error": f"Gagal download file, status {resp.status}"}
                    data = await resp.read()
                    async with aiofiles.open(filepath, "wb") as f:
                        await f.write(data)
            logger.info(f"File berhasil disimpan: {filepath}")
        except Exception:
            logger.exception("Error saat download file")
            filename = None
            filepath = None

    try:
        new_file = File(
            nomer=nomer,
            nama=nama,
            message=cleaned_message,
            url=file_url if file_url else None,
            extension=extension if extension else None,
            filename=filename,
            location=lokasi if lokasi else None,
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        logger.info(f"Data tersimpan, ID: {new_file.id}")
        return {
            "message": "Pesan disimpan (listener aktif)",
            "saved_file": filepath,
            "db_id": new_file.id
        }

    except Exception as e:
        logger.exception("Error saat simpan DB")
        return JSONResponse(status_code=500, content={"error": str(e)})





@app.post("/run-automation")
def run_automation():
    start_time = time.time()

    # Setup Chrome headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://webscraper.io/test-sites/e-commerce/allinone")
    driver.implicitly_wait(3)

    # Ambil semua card thumbnail
    cards = driver.find_elements(By.CSS_SELECTOR, ".card.thumbnail")

    products = []
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, "a.title").text.strip()
        except:
            title = None

        try:
            price = card.find_element(By.CSS_SELECTOR, "h4.price > span").text.strip()
        except:
            price = None

        try:
            description = card.find_element(By.CSS_SELECTOR, "p.description").text.strip()
        except:
            description = None

        try:
            review_count = card.find_element(By.CSS_SELECTOR, ".review-count span").text.strip()
        except:
            review_count = None

        products.append({
            "title": title,
            "price": price,
            "description": description,
            "reviews": review_count
        })

    page_title = driver.title
    driver.quit()

    response_time = round(time.time() - start_time, 2)
    logger.info(f"Scraped {len(products)} products")

    return {
        "status": "success",
        "page_title": page_title,
        "response_time": f"{response_time} seconds",
        "data": products
    }


    


@app.get("/debug-error")
async def debug_error():
    try:
        
        1 / 0
    except Exception as e:
        logger.exception("Debug error endpoint triggered!")
        return {"error": str(e)}
