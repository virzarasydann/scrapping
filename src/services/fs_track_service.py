# services/fs_track_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.schemas.fs_track.fs_request_schema import FsRequestSchema as FsTicket

from src.repository.ticket_repository import TicketRepository

class FsTrackService:
    def __init__(self):
        self.orm = TicketRepository()

    def get_ticket_by_id(self, db: Session, ticket_id: int) -> FsTicket:
        """Ambil ticket SQLAlchemy → konversi ke FsTrack Ticket (dataclass)."""

        orm_ticket = self.orm.get_ticket_by_id(db, ticket_id)

        if not orm_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        return FsTicket(
            no_ticket=orm_ticket.no_tiket,
            customer=orm_ticket.customer,
            model=orm_ticket.model,
            keluhan=orm_ticket.keluhan,
            tanggal=orm_ticket.tanggal,
            before=orm_ticket.before,
            after=orm_ticket.after,
            serial_number=orm_ticket.serial_number,
            lokasi=orm_ticket.lokasi,
            status_fs=orm_ticket.status_fs,
        )
