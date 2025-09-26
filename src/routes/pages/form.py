from fastapi import APIRouter, Request, Depends

from fastapi.templating import Jinja2Templates
from src.configuration.config import SRC_DIR
from fastapi.responses import HTMLResponse
from src.configuration.database import get_db
from sqlalchemy.orm import Session
from src.models.files_models import File
from datetime import date
from src.services.sessions_utils import get_user_id, get_role_id
from src.services.template_service import templates
router = APIRouter(prefix="/form", tags=["Pages"])
# templates = Jinja2Templates(directory=SRC_DIR / "templates" / "pages")


@router.get("", response_class=HTMLResponse, name="form")
async def inbox(request: Request):
    
    print(get_user_id(request))
    today = date.today().isoformat()
    return templates.TemplateResponse(
        "form/index.html",
        {"request": request,"current_time": today}
    )
