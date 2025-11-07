from fastapi import APIRouter, Request, Depends, Form, status

from fastapi.templating import Jinja2Templates
from src.configuration.config import SRC_DIR
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.configuration.database import get_db, get_db_client
from sqlalchemy.orm import Session
from src.models.listeners_models import Listener
from src.models.user_models import User
from src.models.files_models import File
from src.models.menu_models import Menu
from src.models.hak_akses_models import HakAkses
from src.models.fs_track.technicians import Technician
from sqlalchemy.orm import load_only
from src.services.template_service import templates
import bcrypt
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
router = APIRouter(prefix="/user", tags=["User"])
# templates = Jinja2Templates(directory=SRC_DIR / "templates" / "pages")


@router.get("", response_class=HTMLResponse)
async def user_list(request: Request, db: Session = Depends(get_db)):
    messages = db.query(Listener).options(
            load_only(Listener.nomer, Listener.nama, Listener.aktif)
        ).all()
    return templates.TemplateResponse(
        "user/index.html",
        {"request": request, "messages": messages}
    )

@router.get("/admin", response_class=HTMLResponse,name="user_list_admin")
async def user_list_in_admin(request: Request, db: Session = Depends(get_db)):
    messages = db.query(User).all()
    return templates.TemplateResponse(
        "admin/teknisi/index.html",
        {"request": request, "messages": messages}
    )



@router.post("/admin", name="user_post")
async def create_or_update_user_in_admin(
    request: Request,
    id_user: Optional[str] = Form(None),
    nomer: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    db_client: Session = Depends(get_db_client)
):

    if id_user:
        int(id_user)  # UPDATE USER
        user = db.query(User).filter(User.id == id_user).first()
        if user:
            user.nomer = nomer
            plain = f"{password}".encode("utf-8")
            salt = bcrypt.gensalt(rounds=12)
            hashed_bytes = bcrypt.hashpw(plain, salt)
            hashed_str = hashed_bytes.decode("utf-8")
            user.password = hashed_str
            db.commit()
            db.refresh(user)

    else:  
        
        plain = f"{password}".encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(plain, salt)
        hashed_str = hashed_bytes.decode("utf-8")

        new_user = User(
            nomer=nomer,
            password=hashed_str,
            role="teknisi"
        )

        newTechnician = Technician(technician_name=nomer)
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db_client.add(newTechnician)
        db_client.commit()
        db_client.refresh(newTechnician)

        
        menus = db.query(Menu.id).filter(Menu.is_admin == False, Menu.route != "#").all()
        for menu in menus:
            hak = HakAkses(
                id_user=new_user.id,
                id_menu=menu.id,
                lihat=True,
                tambah=True,
                update_data=True,
                hapus=True
            )
            db.add(hak)

        db.commit()

    return RedirectResponse(
        url=request.url_for("user_list_admin"),
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.delete("/admin", name="user_delete")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(status_code=404, content={"message": "User tidak ditemukan"})

    # Hapus semua hak akses user ini
    db.query(HakAkses).filter(HakAkses.id_user == user_id).delete(synchronize_session=False)

    # Hapus user
    db.delete(user)
    db.commit()

    return JSONResponse(status_code=200, content={"message": "User dan hak akses terkait berhasil dihapus"})




@router.get("/search",response_class=HTMLResponse)
async def detail_listener(
    request: Request, 
    nomer_user: str, 
    db: Session = Depends(get_db)
):

    search = db.query(File).filter(File.nomer == nomer_user).all()
    
    if not search:
        
        pass
    
    return templates.TemplateResponse(
        "user/detail.html",
        {
            "request": request,
            "data": search
        }
    )


