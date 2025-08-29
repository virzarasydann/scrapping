from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("automation_dashboard2.html", {"request": request})

class LoginRequest(BaseModel):
    phone: str

@app.post("/submit-login")
async def submit_login(data: LoginRequest):
    phone = data.phone

    # contoh: panggil Selenium atau proses OTP
    # selenium_logic(phone)

    return JSONResponse({
        "phone": phone,
        "status": f"OTP dikirim ke WhatsApp {phone}!"
    })



