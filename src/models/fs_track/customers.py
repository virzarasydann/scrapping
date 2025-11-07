from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.configuration.database import ClientBase

class Customer(ClientBase):
    __tablename__ = 'customers'

    id_customer = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    phone_number = Column(String(255), default='')
    
    # Relationships
    jobs = relationship("Job", back_populates="customer")