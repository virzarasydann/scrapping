# src/models/listeners_models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from src.configuration.database import Base

class Listener(Base):
    __tablename__ = "listeners"

    id = Column(Integer, primary_key=True, index=True)
    nomer = Column(String(50), unique=True, index=True)  # nomor pengirim
    nama = Column(String(50))
    aktif = Column(Boolean, default=True)  # status listener aktif/tidak
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
