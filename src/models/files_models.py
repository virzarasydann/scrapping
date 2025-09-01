from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from src.configuration.database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    nomer = Column(String(50))
    nama = Column(String(255))
    message = Column(Text)
    url = Column(String(255), nullable=True)
    extension = Column(String(50), nullable=True)
    filename = Column(String(255))
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
