# services/fs_track_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.fs_track.domain_models import Ticket as FsTicket
from src.services.ticket_orm_service import TicketORMService


class FsTrackService:
    def __init__(self):
        self.orm = TicketORMService()

    def get_ticket_by_id(self, db: Session, ticket_id: int) -> FsTicket:
        """Ambil ticket SQLAlchemy → konversi ke FsTrack Ticket (dataclass)."""

        orm_ticket = self.orm.get_ticket_by_id(db, ticket_id)

        if not orm_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Mapping ORM → dataclass domain model
        return FsTicket(
            customer=orm_ticket.customer,
            model=orm_ticket.model,
            keluhan=orm_ticket.keluhan,
            tanggal=orm_ticket.tanggal,
            before=orm_ticket.before,
            after=orm_ticket.after,
            serial_number=orm_ticket.serial_number,
            lokasi=orm_ticket.lokasi,
        )
