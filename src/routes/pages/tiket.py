import httpx
import os
from pydantic import ValidationError
import uuid

from fastapi import (
    APIRouter, 
    Request, 
    Depends, 
    UploadFile, 
    File, 
    status
)
from fastapi.responses import (
    HTMLResponse, 
    RedirectResponse
)

from sqlalchemy.orm import Session

from src.configuration.config import (
    SRC_DIR,
    GROUP_ID,
    TOKEN, 
    APP_ENV
)
from src.configuration.database import get_db
from src.models.ticket_models import Ticket
from src.schemas.ticket import TicketCreate
from src.services.fs_track.factory import CodeIgniterServiceFactory
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


async def ci_create_job(ticket: Ticket) -> int:
    BASE_URL_CI = "https://fs.616263.my.id"
    CI_USERNAME = "ADMIN1"
    CI_PASSWORD = "ADMINAC"
    
    service = CodeIgniterServiceFactory.create_service(
        BASE_URL_CI, CI_USERNAME, CI_PASSWORD
    )
    
    return await service.create_job_from_ticket(ticket)

@router.post("", name="ticket_post")
async def ticket_create(
    request: Request,
    before: UploadFile = File(None),
    after: UploadFile = File(None),
    serial_number: UploadFile = File(None),
    lokasi: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    
    try:
        form = await request.form()
        
        
        data = TicketCreate(
            tanggal=str(form.get("tanggal") or ""),
            no_tiket=str(form.get("no_tiket") or ""),
            customer=str(form.get("customer") or ""),
            model=str(form.get("model")) if form.get("model") else None,
            keluhan=str(form.get("keluhan")) if form.get("keluhan") else None,
            teknisi=str(form.get("teknisi")) if form.get("teknisi") else None,
            indikasi=str(form.get("indikasi")) if form.get("indikasi") else None,
            tindakan=str(form.get("tindakan")) if form.get("tindakan") else None,
            lokasi_koordinat=str(form.get("lokasi_koordinat")) if form.get("lokasi_koordinat") else None
        )

    except ValidationError as e:
        field_errors = {}
        for err in e.errors():
            field_name = err["loc"][0]  
            field_errors[field_name] = err["msg"]
        
        print("=== VALIDATION ERRORS ===")
        print(field_errors)
        print("=========================")

        return templates.TemplateResponse(
            "form/index.html",
            {
                "request": request,
                "field_errors": field_errors,
                "show_error_toast": True,
                "formdata": dict(form),
                "current_time": form.get("tanggal", "")
            },
            status_code=422
        )
    
    except Exception as e:
        
        print(f"=== UNEXPECTED ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        print("========================")
        
        return templates.TemplateResponse(
            "form/index.html",
            {
                "request": request,
                "errors": [f"Terjadi kesalahan: {str(e)}"],
                "formdata": {}
            },
            status_code=500
        )

    
    BASE_URL = "http://192.206.117.191:8000/public"

    def file_url(filename: str) -> str:
        if APP_ENV == "production" and filename:
            return f"{BASE_URL}/{filename}"
        return ""

    user_id = get_user_id(request)
    before_name = save_upload_file(before)
    after_name = save_upload_file(after)
    serial_name = save_upload_file(serial_number)
    lokasi_name = save_upload_file(lokasi)

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

    # Kirim ke Fonnte
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





