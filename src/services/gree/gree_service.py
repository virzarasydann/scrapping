# services/fs_track_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing_extensions import Tuple

from src.schemas.gree.gree_request_schema import GreeRequestSchema as GreeTicket
from src.repository.ticket_repository import TicketRepository

class GreeService:
    def __init__(self):
        self.orm = TicketRepository()

    def get_ticket_by_id(
        self, ticket_id: int, db: Session
    ) -> Tuple[GreeTicket, TicketRepository]:
        """Ambil ticket SQLAlchemy → konversi ke FsTrack Ticket (dataclass)."""

        orm_ticket = self.orm.get_ticket_by_id(db, ticket_id)

        if not orm_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        gree_ticket = GreeTicket(
            no_ticket=orm_ticket.no_tiket,
            customer=orm_ticket.customer,
            model=orm_ticket.model,
            keluhan=orm_ticket.keluhan,
            tanggal=orm_ticket.tanggal,
            before=orm_ticket.before,
            after=orm_ticket.after,
            serial_number=orm_ticket.serial_number,
            lokasi=orm_ticket.lokasi,
            status_gree=orm_ticket.status_gree,
        )

        return gree_ticket, orm_ticket
