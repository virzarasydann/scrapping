import os
import uuid

import httpx
from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.configuration.config import APP_ENV, GROUP_ID, SRC_DIR, TOKEN
from src.configuration.database import get_db
from src.models.ticket_models import Ticket
from src.schemas.ticket import TicketCreate
from src.services.sessions_utils import get_role_id, get_user_id
from src.services.template_service import templates

router = APIRouter(prefix="/tiket", tags=["Tickets"])

PUBLIC_DIR = SRC_DIR / "public"
os.makedirs(PUBLIC_DIR, exist_ok=True)


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
        "tiket/index.html", {"request": request, "data": messages}
    )


@router.post("", name="ticket_post")
async def ticket_create(
    request: Request,
    before: UploadFile = File(None),
    after: UploadFile = File(None),
    serial_number_indoor: UploadFile = File(...),
    serial_number_outdoor: UploadFile = File(...),
    lokasi_file: UploadFile = File(...),
    route_navigation: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    required_files = {
        "serial_number_indoor": serial_number_indoor,
        "serial_number_outdoor": serial_number_outdoor,
        "lokasi_file": lokasi_file,
        "route_navigation": route_navigation,
    }

    file_errors = {}
    for field_name, file in required_files.items():
        if not file or not file.filename:
            file_errors[field_name] = (
                f"{field_name.replace('_', ' ').title()} harus diisi"
            )

    if file_errors:
        form = await request.form()
        return templates.TemplateResponse(
            "form/index.html",
            {
                "request": request,
                "field_errors": file_errors,
                "show_error_toast": True,
                "formdata": dict(form),
                "current_time": form.get("tanggal", ""),
            },
            status_code=422,
        )
    try:
        form = await request.form()

        data = TicketCreate(
            tanggal=str(form.get("tanggal") or ""),
            no_tiket=str(form.get("no_tiket") or ""),
            customer=str(form.get("customer")) or None,
            model=str(form.get("model")) if form.get("model") else None,
            keluhan=str(form.get("keluhan")) if form.get("keluhan") else None,
            teknisi=str(form.get("teknisi")) if form.get("teknisi") else None,
            indikasi=str(form.get("indikasi")) if form.get("indikasi") else None,
            tindakan=str(form.get("tindakan")) if form.get("tindakan") else None,
            status_fs=False,
            status_gree=False,
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
                "current_time": form.get("tanggal", ""),
            },
            status_code=422,
        )

    except Exception as e:
        print("=== UNEXPECTED ERROR ===")
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
                "formdata": {},
            },
            status_code=500,
        )

    BASE_URL = "http://192.206.117.191:8000/public"

    def file_url(filename: str) -> str:
        if APP_ENV == "production" and filename:
            return f"{BASE_URL}/{filename}"
        return ""

    user_id = get_user_id(request)

    before_filename = save_upload_file(before)
    after_filename = save_upload_file(after)
    serial_indoor_filename = save_upload_file(serial_number_indoor)
    serial_outdoor_filename = save_upload_file(serial_number_outdoor)
    lokasi_filename = save_upload_file(lokasi_file)
    route_filename = save_upload_file(route_navigation)

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
        before=before_filename,
        after=after_filename,
        serial_number_indoor=serial_indoor_filename,
        serial_number_outdoor=serial_outdoor_filename,
        lokasi=lokasi_filename,
        route_navigation=route_filename,
        user_id=user_id,
        status_fs=data.status_fs,
        status_gree=data.status_gree,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Kirim ke Fonnte
    files = [
        ("Before", before_filename),
        ("After", after_filename),
        ("Serial Number Indoor", serial_indoor_filename),
        ("Serial Number Outdoor", serial_outdoor_filename),
        ("Lokasi", lokasi_filename),
        ("Route Navigation", route_filename),
    ]

    headers = {"Authorization": f"{TOKEN}"}

    async with httpx.AsyncClient() as client:
        for idx, (label, filename) in enumerate(files):
            if not filename:
                continue

            message = (
                (
                    f"Tiket baru berhasil di automisasi!\n"
                    f"No Tiket: {ticket.no_tiket}\n"
                    f"Tanggal: {ticket.tanggal}\n"
                    f"Foto untuk: {label}"
                )
                if idx == 0
                else f"Tiket: {ticket.no_tiket}\nFoto untuk: {label}"
            )

            payload = {
                "target": GROUP_ID,
                "url": file_url(filename),
                "message": message,
            }

            try:
                response = await client.post(
                    "https://api.fonnte.com/send", data=payload, headers=headers
                )
                res_json = response.json()
                print(f"✅ Response Fonnte ({label}):", res_json)
            except Exception as e:
                print(f"❌ Error kirim Fonnte ({label}):", str(e))

    return RedirectResponse(
        url="/tiket",
        status_code=status.HTTP_303_SEE_OTHER,
    )
