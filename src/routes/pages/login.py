from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from src.configuration.config import SRC_DIR
from fastapi.responses import HTMLResponse, RedirectResponse
from src.configuration.database import get_db
from sqlalchemy.orm import Session
from src.models.user_models import User
import bcrypt  # pakai bcrypt
from src.services.sessions_utils import set_session,get_user_id


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
    # plain = "rahasia123".encode("utf-8")
    # # cost/rounds default di gensalt() biasanya 12 — bisa disesuaikan
    # salt = bcrypt.gensalt(rounds=12)
    # hashed_bytes = bcrypt.hashpw(plain, salt)

    # # simpan ke DB sebagai string (decode)
    # hashed_str = hashed_bytes.decode("utf-8")
    # print(hashed_str) 
    if not user:
        return templates.TemplateResponse(
            "login/index.html",
            {"request": request, "error": "User tidak ditemukan"}
        )

    # cek password dengan bcrypt
    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return templates.TemplateResponse(
            "login/index.html",
            {"request": request, "error": "Password salah"}
        )

    
    set_session(request, user)
    
    return RedirectResponse(
        url=request.url_for("dashboard"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
