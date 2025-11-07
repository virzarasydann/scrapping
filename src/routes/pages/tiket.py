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

import requests
from bs4 import BeautifulSoup
from src.services.sessions_utils import get_user_id, get_role_id
from src.services.template_service import templates
router = APIRouter(prefix="/tiket", tags=["Tickets"])
# templates = Jinja2Templates(directory=SRC_DIR / "templates" / "pages")

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
@router.get("", response_class=HTMLResponse,name="tiket")
async def index(request: Request, db: Session = Depends(get_db)):
    role = get_role_id(request)
    user_id = get_user_id(request)

    query_filters = {
        "admin": lambda q: q,  
        "teknisi": lambda q: q.filter(Ticket.user_id == user_id),
    }

    base_query = db.query(Ticket)
    messages = query_filters.get(role, query_filters["teknisi"])(base_query)

    return templates.TemplateResponse(
        "tiket/index.html",
        {"request": request, "data": messages}
    )


# ------------ POST tiket baru ------------
BASE_URL_CI = "https://fs.616263.my.id"
CI_USERNAME = "ADMIN1"
CI_PASSWORD = "ADMINAC"

def ci_create_job(ticket):
    """
    Fungsi untuk login ke CodeIgniter dan kirim data job baru
    berdasarkan data tiket dari FastAPI.
    """
    session = requests.Session()

    # Step 1: Ambil token login
    login_page = session.get(f"{BASE_URL_CI}/login")
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_login = soup.find("meta", {"name": "csrf_test_name"})["content"]
    
    # Step 2: Login
    login_payload = {
        "login": CI_USERNAME,
        "password": CI_PASSWORD,
        "csrf_test_name": csrf_login
    }
    login_resp = session.post(f"{BASE_URL_CI}/login", data=login_payload)
    print("[DEBUG] After login URL:", login_resp.url)
    print("[DEBUG] After login snippet:", login_resp.text[:300])

    print("\n[DEBUG] Cookies setelah login:")
    for cookie in session.cookies:
        print(f"  {cookie.name} = {cookie.value[:50]}...")
    # Step 3: Ambil token halaman tambah job
    add_page = session.get(f"{BASE_URL_CI}/admin/jobs/add")
    
    soup_add = BeautifulSoup(add_page.text, "html.parser")
    for inp in soup_add.find_all(["input", "textarea", "select"]):
        name = inp.get("name")
        if name:
            print("Field:", name)
    csrf_add = soup_add.find("meta", {"name": "csrf_test_name"})["content"]

    # Step 4: Kirim data job
    # payload = {
    #     # "customer_name": ticket.customer or "testing",
    #     "customer_address": "Jl. Test Integration No.1",
    #     "customer_phone_number": "081234567890",
    #     "ac_unit_name": ticket.model or "testing",
    #     "id_service_type": "24",
    #     "description": ticket.keluhan or "testing",
    #     "team": "AhliAC",
    #     "accessor": "Wahyu Nugraha",
    #     "start_date": str(ticket.tanggal),
    #     "end_date": str(ticket.tanggal),
    #     "csrf_test_name": csrf_add,
    #     "save": "1"
    # }

    payload = {
        "csrf_test_name": csrf_add,
        
        # "id_customer": "1",                              # ← TAMBAHKAN
        "customer_name" : ticket.customer,
        "customer_address": "Jl. Test Integration No.1",
        "customer_phone_number": "081234567890",
        
        "id_ac_unit": "156",                               # ← TAMBAHKAN
        "id_service_type": "24",
        "description": ticket.keluhan or "testing",
        "team": "AhliAC",
        "accessor": "Wahyu Nugraha",
        "start_date": str(ticket.tanggal),
        "end_date": str(ticket.tanggal),
        "save": "1"                                     # ← TAMBAHKAN (atau "")
    }

    response = session.post(f"{BASE_URL_CI}/admin/jobs/add", data=payload)
    # print("[CI] Response text:", response.text)
    # print("[CI] Response JSON:", response.content)
    print("\n[DEBUG] Payload yang dikirim:")
    for k, v in payload.items():
        print(f"  {k}: {v}")
    print("[CI] Status:", response.status_code)
    print("[CI] URL:", response.url)

    return response.status_code


# ----------------------------- #
# Function utama FastAPI kamu   #
# ----------------------------- #

@router.post("", name="ticket_post")
async def ticket_create(
    request: Request,
    data: TicketCreate = Depends(TicketCreate.as_form),
    before: UploadFile = File(None),
    after: UploadFile = File(None),
    serial_number: UploadFile = File(None),
    lokasi: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    BASE_URL = "http://192.206.117.191:8000/public"

    def file_url(filename: str) -> str:
        if APP_ENV == "production" and filename:
            return f"{BASE_URL}/{filename}"
        return ""

    # -------------------
    # Simpan file upload
    # -------------------
    user_id = get_user_id(request)
    before_name = save_upload_file(before)
    after_name = save_upload_file(after)
    serial_name = save_upload_file(serial_number)
    lokasi_name = save_upload_file(lokasi)

    # -------------------
    # Buat tiket di DB
    # -------------------
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
        user_id=user_id
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # -------------------------
    # Kirim data ke CI (jobs)
    # -------------------------
    try:
        ci_status = ci_create_job(ticket)
        print(f"[+] Job CI status: {ci_status}")
    except Exception as e:
        print("❌ Gagal integrasi ke CI:", e)

    # -------------------------
    # Kirim notifikasi ke Fonnte
    # -------------------------
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

            message = (
                f"Tiket baru berhasil dibuat!\n"
                f"No Tiket: {ticket.no_tiket}\n"
                f"Customer: {ticket.customer}\n"
                f"Tanggal: {ticket.tanggal}\n"
                f"Model: {ticket.model}\n"
                f"Keluhan: {ticket.keluhan}\n"
                f"Teknisi: {ticket.teknisi}\n"
                f"Indikasi: {ticket.indikasi}\n"
                f"Tindakan: {ticket.tindakan}\n"
                f"Lokasi Koor: {ticket.lokasi_koordinat}\n\n"
                f"Foto untuk: {label}"
            ) if idx == 0 else f"Tiket: {ticket.no_tiket}\nFoto untuk: {label}"

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
        url="/form",
        status_code=status.HTTP_303_SEE_OTHER,
    )





