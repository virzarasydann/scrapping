from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.configuration.database import Base


class Menu(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_parent = Column(Integer, ForeignKey("menu.id"), nullable=True)
    judul = Column(String(100), nullable=False)
    route = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)
    urutan = Column(Integer, default=0)
    is_admin = Column(Boolean, nullable=False, server_default="0")


    # relasi parent-child
    parent = relationship("Menu", remote_side=[id], backref="children")

    # relasi ke hak akses
    hak_akses = relationship("HakAkses", back_populates="menu")
