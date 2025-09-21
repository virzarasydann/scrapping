from sqlalchemy.orm import joinedload
from src.configuration.database import SessionLocal
from src.models.menu_models import Menu
from src.models.hak_akses_models import HakAkses
from src.services.sessions_utils import get_user_id, get_role_id, get_username
from fastapi import Request

def build_menu_tree(menus):
    menu_dict = {m.id: {"id": m.id, "judul": m.judul, "route": m.route, "children": []} for m in menus}

    root_menus = []
    for m in menus:
        if m.id_parent:
            parent = menu_dict.get(m.id_parent)
            if parent:
                parent["children"].append(menu_dict[m.id])
        else:
            root_menus.append(menu_dict[m.id])
    print(root_menus)
    return root_menus


# def common_context(request: Request):
#     db = SessionLocal()
#     user_id = get_user_id(request)

#     if not user_id:
#         db.close()
#         return {"menus": [], "request": request}

#     role = get_role_id(request)
#     username = get_username(request)
  
#     menus = (
#         db.query(Menu)
#         .join(HakAkses, HakAkses.id_menu == Menu.id)
#         .filter(HakAkses.id_user == user_id, HakAkses.lihat == 1)
#         .order_by(Menu.urutan)
#         .all()
#     )

#     db.close()
#     return {"menus": build_menu_tree(menus), "request": request, "username": username, "role": role}


def common_context(request: Request):
    db = SessionLocal()
    user_id = get_user_id(request)

    if not user_id:
        db.close()
        return {"menus": [], "request": request}

    role = get_role_id(request)
    username = get_username(request)

    # Ambil semua menu anak yang user punya akses lihat
    accessible_children = (
        db.query(Menu)
        .join(HakAkses, HakAkses.id_menu == Menu.id)
        .filter(HakAkses.id_user == user_id, HakAkses.lihat == True)
        .all()
    )

    # Ambil parent dari children tersebut (route="#" atau parent asli)
    parent_ids = list({m.id_parent for m in accessible_children if m.id_parent})
    parents = db.query(Menu).filter(Menu.id.in_(parent_ids)).all()

    # Gabungkan parent + children untuk build tree
    menus_to_build = parents + accessible_children

    db.close()
    return {
        "menus": build_menu_tree(menus_to_build),
        "request": request,
        "username": username,
        "role": role
    }
