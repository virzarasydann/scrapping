
from fastapi import Request

SESSION_USER_ID = "user_id"
SESSION_ROLE = "role"
SESSION_NOMER = "nomer"

def set_session(request: Request, user):
    """Simpan data user ke session"""
    request.session[SESSION_USER_ID] = user.id
    request.session[SESSION_ROLE] = user.role
    request.session[SESSION_NOMER] = user.nomer

def clear_session(request: Request):
    """Hapus semua session"""
    request.session.clear()

def get_user_id(request: Request):
    return request.session.get(SESSION_USER_ID) or 26

def get_role_id(request: Request):
    return request.session.get(SESSION_ROLE)

def get_username(request: Request):
    return request.session.get(SESSION_NOMER)

def is_logged_in(request: Request):
    return SESSION_USER_ID in request.session
