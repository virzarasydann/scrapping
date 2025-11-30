# services/ticket_service.py

from sqlalchemy.orm import Session

from src.models.ticket_models import Ticket
from src.schemas.ticket import TicketCreate


class TicketORMService:
    def create_ticket(self, db: Session, data: TicketCreate, user_id: int):
        ticket = Ticket(
            user_id=user_id,
            tanggal=data.tanggal,
            no_tiket=data.no_tiket,
            customer=data.customer,
            model=data.model,
            keluhan=data.keluhan,
            teknisi=data.teknisi,
            indikasi=data.indikasi,
            tindakan=data.tindakan,
            lokasi_koordinat=data.lokasi_koordinat,
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    def get_all_tickets(self, db: Session):
        return db.query(Ticket).order_by(Ticket.id.desc()).all()

    def get_ticket_by_id(self, db: Session, ticket_id: int):
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def update_ticket(self, db: Session, ticket_id: int, data: TicketCreate):
        ticket = self.get_ticket_by_id(db, ticket_id)
        if not ticket:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket, key, value)

        db.commit()
        db.refresh(ticket)
        return ticket

    def delete_ticket(self, db: Session, ticket_id: int):
        ticket = self.get_ticket_by_id(db, ticket_id)
        if not ticket:
            return False

        db.delete(ticket)
        db.commit()
        return True
