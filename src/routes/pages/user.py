from fastapi import APIRouter, Request, Depends

from fastapi.templating import Jinja2Templates
from src.configuration.config import SRC_DIR
from fastapi.responses import HTMLResponse
from src.configuration.database import get_db
from sqlalchemy.orm import Session
from src.models.listeners_models import Listener
from src.models.files_models import File
from sqlalchemy.orm import load_only

router = APIRouter(prefix="/user", tags=["Pages"])
templates = Jinja2Templates(directory=SRC_DIR / "templates" / "pages")


@router.get("", response_class=HTMLResponse)
async def user_list(request: Request, db: Session = Depends(get_db)):
    messages = db.query(Listener).options(
            load_only(Listener.nomer, Listener.nama, Listener.aktif)
        ).all()
    return templates.TemplateResponse(
        "user/index.html",
        {"request": request, "messages": messages}
    )

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