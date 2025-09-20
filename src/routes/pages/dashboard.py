from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.configuration.config import SRC_DIR
from fastapi.responses import HTMLResponse
from src.services.template_service import templates
router = APIRouter(prefix="/dashboard", tags=["Pages"])
# templates = Jinja2Templates(directory=SRC_DIR / "templates" / "pages")


@router.get("", response_class=HTMLResponse, name="dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard/index.html", {"request": request})

