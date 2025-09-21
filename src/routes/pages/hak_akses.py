from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from src.configuration.database import get_db
from src.models.user_models import User
from src.models.hak_akses_models import HakAkses
from src.models.menu_models import Menu
from src.services.template_service import templates

router = APIRouter(prefix="/hak_akses", tags=["Hak Akses"])

@router.get("/", response_class=HTMLResponse, name="hak_akses_index")
async def hak_akses_index(request: Request, db: Session = Depends(get_db)):
    # Ambil semua user
    # Ambil semua user dengan role teknisi
    users = db.query(User).filter(User.role == "teknisi").all()

    # Ambil semua menu yang bukan admin
    menus = db.query(Menu).filter(Menu.is_admin == False,  Menu.route != "#").all()
    for m in menus:
        print("di route /hak_akses/",m.id, m.judul, m.route, m.is_admin)
    return templates.TemplateResponse(
        "admin/hak_akses/index.html",
        {
            "request": request,
            "users": users,
            "menu_hak_akses": menus,
        }
    )


@router.get("/get_hak_akses")
async def get_user_hak_akses(user_id: int, db: Session = Depends(get_db)):
    data = db.query(HakAkses).filter(HakAkses.id_user == user_id).all()
    result = [
        {
            "id_menu": d.id_menu,
            "lihat": d.lihat,
            "tambah": d.tambah,
            "update_data": d.update_data,
            "hapus": d.hapus,
        }
        for d in data
    ]
    print(result)
    return result


@router.post("/save_hak_akses")
async def save_hak_akses(
    request: Request,
    db: Session = Depends(get_db)
):
    form = await request.form()
    user_id = int(form.get("user_id")) 

    # Hapus dulu semua hak akses lama user ini
    db.query(HakAkses).filter(HakAkses.id_user == user_id).delete()

    # Looping isi form -> simpan baru
    for key, value in form.items():
        if not key.startswith("akses"):
            continue
        
        # key = "akses[menu_id][field]"
        # contoh: akses[1][lihat]
        try:
            _, menu_id, field = key.replace("]", "").split("[")
            menu_id = int(menu_id)
        except Exception:
            continue

        # Cari apakah sudah ada HakAkses untuk menu_id ini
        akses = db.query(HakAkses).filter_by(id_user=user_id, id_menu=menu_id).first()
        if not akses:
            akses = HakAkses(id_user=user_id, id_menu=menu_id)
            db.add(akses)

        # Set field True kalau checkbox dicentang
        if field == "lihat":
            akses.lihat = True
        elif field == "tambah":
            akses.tambah = True
        elif field == "update_data":
            akses.update_data = True
        elif field == "hapus":
            akses.hapus = True

    db.commit()

    return RedirectResponse(url="/hak_akses", status_code=303)