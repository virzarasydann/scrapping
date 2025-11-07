from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.configuration.database import ClientBase

class ServiceType(ClientBase):
    __tablename__ = 'service_types'

    id_service_type = Column(Integer, primary_key=True, autoincrement=True)
    service_type = Column(String(255), nullable=False)
    
    # Relationships
    jobs = relationship("Job", back_populates="service_type")