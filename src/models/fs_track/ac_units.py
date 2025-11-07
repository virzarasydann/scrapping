from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.configuration.database import ClientBase


class ACUnit(ClientBase):
    __tablename__ = 'ac_units'

    id_ac_unit = Column(Integer, primary_key=True, autoincrement=True)
    product_type = Column(String(255), nullable=False)
    
    # Relationships
    jobs = relationship("Job", back_populates="ac_unit")