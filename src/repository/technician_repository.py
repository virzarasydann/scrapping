from sqlalchemy.orm import Session
from src.models.technician_models import Technician 

class TechnicianRepository:
    
    def get_all_technicians(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Technician).filter(Technician.is_active == True).offset(skip).limit(limit).all()

    def get_technician_by_id(self, db: Session, technician_id: int):
        return db.query(Technician).filter(Technician.id == technician_id).first()