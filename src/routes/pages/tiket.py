import os
from pathlib import Path
import shutil
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.configuration.config import SRC_DIR,GROUP_ID,TOKEN, APP_ENV
from src.configuration.database import get_db
from src.models.ticket_models import Ticket
from src.schemas.ticket import TicketCreate
import uuid
import httpx

router = APIRouter(prefix="/tiket", tags=["Tickets"])
templates = Jinja2Templates(directory=SRC_DIR / "templates" / "pages")

PUBLIC_DIR = SRC_DIR / "public"
os.makedirs(PUBLIC_DIR, exist_ok=True)

# @router.get("", response_class=HTMLResponse, name="tiket")
# async def ticket_index(request: Request):
   
#     return templates.TemplateResponse(
#         "tiket/index.html",
#         {"request": request}
#     )

def save_upload_file(file: UploadFile | None) -> str | None:
    if not file:
        return None

    # ambil ekstensi file asli
    _, ext = os.path.splitext(file.filename)
    # bikin nama unik
    filename = f"{uuid.uuid4().hex}{ext.lower()}"
    file_path = PUBLIC_DIR / filename

    # simpan ke disk
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return filename



# ------------ GET semua tiket ------------
@router.get("", response_class=HTMLResponse, name="tiket")
async def ticket_list(request: Request, db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    return templates.TemplateResponse(
        "tiket/index.html", {"request": request, "data": tickets}
    )


# ------------ POST tiket baru ------------
@router.post("", name="ticket_post")
async def ticket_create(
    data: TicketCreate = Depends(TicketCreate.as_form),
    before: UploadFile = File(None),
    after: UploadFile = File(None),
    serial_number: UploadFile = File(None),
    lokasi: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    

    
    BASE_URL = "http://103.191.92.250:8000/public"

    def file_url(filename: str) -> str:
        if APP_ENV == "production" and filename:
            return f"{BASE_URL}/{filename}"
        return ""

    # Simpan file upload
    before_name = save_upload_file(before)
    after_name = save_upload_file(after)
    serial_name = save_upload_file(serial_number)
    lokasi_name = save_upload_file(lokasi)

    # Buat ticket di DB
    ticket = Ticket(
        tanggal=data.tanggal,
        no_tiket=data.no_tiket,
        customer=data.customer,
        model=data.model,
        keluhan=data.keluhan,
        teknisi=data.teknisi,
        indikasi=data.indikasi,
        tindakan=data.tindakan,
        lokasi_koordinat=data.lokasi_koordinat,
        before=before_name,
        after=after_name,
        serial_number=serial_name,
        lokasi=lokasi_name,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # List file beserta label
    files = [
        ("Before", before_name),
        ("After", after_name),
        ("Serial Number", serial_name),
        ("Lokasi", lokasi_name),
    ]

    headers = {"Authorization": f"{TOKEN}"}

    async with httpx.AsyncClient() as client:
        for idx, (label, filename) in enumerate(files):
            if not filename:
                continue

            # Pesan berbeda untuk file pertama vs berikutnya
            if idx == 0:
                # Full ticket message + label foto
                message = f"""Tiket baru berhasil dibuat!
No Tiket: {ticket.no_tiket}
Customer: {ticket.customer}
Tanggal: {ticket.tanggal}
Model: {ticket.model}
Keluhan: {ticket.keluhan}
Teknisi: {ticket.teknisi}
Indikasi: {ticket.indikasi}
Tindakan: {ticket.tindakan}
Lokasi Koor: {ticket.lokasi_koordinat}

Foto untuk: {label}"""
            else:
                # Minimal message: tiket + nama file
                message = f"Tiket: {ticket.no_tiket}\nFoto untuk: {label}"

            payload = {
                "target": GROUP_ID,
                "url": file_url(filename),
                "message": message
            }

            try:
                response = await client.post(
                    "https://api.fonnte.com/send",
                    data=payload,
                    headers=headers
                )
                res_json = response.json()
                print(f"✅ Response Fonnte ({label}):", res_json)
            except Exception as e:
                print(f"❌ Error kirim Fonnte ({label}):", str(e))

    return RedirectResponse(
        url=router.url_path_for("tiket"),
        status_code=status.HTTP_303_SEE_OTHER,
    )





