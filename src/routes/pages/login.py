from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from src.configuration.config import SRC_DIR
from fastapi.responses import HTMLResponse, RedirectResponse
from src.configuration.database import get_db
from sqlalchemy.orm import Session
from src.models.user_models import User
import bcrypt  # pakai bcrypt
from src.services.sessions_utils import set_session,get_user_id
from sqlalchemy.orm import joinedload
from src.models.menu_models import Menu
from src.models.hak_akses_models import HakAkses
router = APIRouter(prefix="/login", tags=["Pages"])
templates = Jinja2Templates(directory=SRC_DIR / "templates" / "pages")


@router.get("", response_class=HTMLResponse,name="login")
async def login(request: Request):
    return templates.TemplateResponse(
        "login/index.html",
        {"request": request}
    )




@router.post("/post", name="login_post")
async def login_post(
    request: Request,
    nomer: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.nomer == nomer).first()
    if not user:
        return templates.TemplateResponse(
            "login/index.html",
            {"request": request, "error": "User tidak ditemukan"}
        )

    
    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return templates.TemplateResponse(
            "login/index.html",
            {"request": request, "error": "Password salah"}
        )

    
    set_session(request, user)

    
    if user.role == "admin":
        return RedirectResponse(
            url=request.url_for("user_list_admin"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

   
    first_menu = (
        db.query(Menu)
        .join(HakAkses, HakAkses.id_menu == Menu.id)
        .filter(
            HakAkses.id_user == user.id,
            HakAkses.lihat == True,
            Menu.is_admin == False,
            Menu.route != "#",   
            Menu.route != "",
        )
        .order_by(Menu.urutan.asc())
        .first()
    )

    if first_menu:
        return RedirectResponse(
            url=first_menu.route,
            status_code=status.HTTP_303_SEE_OTHER,
        )

    
    return RedirectResponse(
        url=request.url_for("dashboard"),
        status_code=status.HTTP_303_SEE_OTHER,
    )

