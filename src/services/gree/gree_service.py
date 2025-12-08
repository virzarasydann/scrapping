# services/fs_track_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing_extensions import Tuple

from src.repository.ticket_repository import TicketRepository
from src.schemas.gree.gree_request_schema import GreeRequestSchema as GreeTicket


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
            serial_number_indoor=orm_ticket.serial_number_indoor,
            serial_number_outdoor=orm_ticket.serial_number_outdoor,
            lokasi=orm_ticket.lokasi,
            route_navigation=orm_ticket.route_navigation,
            status_gree=orm_ticket.status_gree,
        )

        return gree_ticket, orm_ticket
