from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.configuration.database import ClientBase


class Technician(ClientBase):
    __tablename__ = 'technicians'

    id_technicians = Column(Integer, primary_key=True, autoincrement=True)
    technician_name = Column(String(255), nullable=False)
    
    # Relationships
    job_details = relationship("JobDetail", back_populates="technician")
