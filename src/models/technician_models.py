from sqlalchemy import Column, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.mysql import BIGINT 
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.configuration.database import Base

class Technician(Base):
    __tablename__ = "technicians"

   
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

   
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=True)
    location = Column(String(100), nullable=True) 
    phone_number = Column(String(20), nullable=True)
    
   
    level = Column(String(50), nullable=True) 
    
    
    is_active = Column(Boolean, nullable=False, default=True)

  
    created_at = Column(TIMESTAMP, nullable=True, default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())

   
    # assignments = relationship("TechnicianWorkOrder", back_populates="technician")

    def __repr__(self):
        return f"<Technician(id={self.id}, name={self.name}, active={self.is_active}, phone_number={self.phone_number})>"