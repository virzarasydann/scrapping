from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.configuration.database import Base


class HakAkses(Base):
    __tablename__ = "hak_akses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user = Column(Integer, nullable=False)  # FK ke tabel users, kalau ada
    id_menu = Column(Integer, ForeignKey("menu.id"), nullable=False)

    lihat = Column(Boolean, default=False)
    tambah = Column(Boolean, default=False)
    update_data = Column(Boolean, default=False)
    hapus = Column(Boolean, default=False)

    # relasi ke menu
    menu = relationship("Menu", back_populates="hak_akses")
