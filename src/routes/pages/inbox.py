# from fastapi import APIRouter, Request, Depends
# from fastapi.responses import HTMLResponse
# from sqlalchemy.orm import Session

# from src.configuration.database import get_db
# from src.models.ticket_models import Ticket
# from src.services.template_service import templates
# from src.services.sessions_utils import get_user_id, get_role_id

# router = APIRouter(prefix="/inbox", tags=["Pages"])


# @router.get("", response_class=HTMLResponse)
# async def inbox(request: Request, db: Session = Depends(get_db)):
#     role = get_role_id(request)
#     user_id = get_user_id(request)

#     query_filters = {
#         "admin": lambda q: q,  
#         "teknisi": lambda q: q.filter(Ticket.user_id == user_id),
#     }

#     base_query = db.query(Ticket)
#     messages = query_filters.get(role, query_filters["teknisi"])(base_query)

#     return templates.TemplateResponse(
#         "tiket/index.html",
#         {"request": request, "messages": messages}
#     )
