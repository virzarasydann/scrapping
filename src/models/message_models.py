import enum
from sqlalchemy import Column, String, Text, Enum, TIMESTAMP, ForeignKey, DECIMAL
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.configuration.database import Base


class MessageType(str, enum.Enum):
    PESAN = "pesan"
    SHARE_LOKASI = "share_lokasi"
    VOICE = "voice"
    VIDEO = "video"

    FOTO_RUMAH_CUSTOMER = "foto_rumah_customer"
    FOTO_KARTU_GARANSI = "foto_kartu_garansi"
    FOTO_FAKTUR_PEMBELIAN = "foto_faktur_pembelian"
    FOTO_TGL_PRODUKSI_INDOOR = "foto_tgl_produksi_indoor"
    FOTO_TGL_PRODUKSI_OUTDOOR = "foto_tgl_produksi_outdoor"
    FOTO_VOLTASE = "foto_voltase"
    FOTO_AMPERE = "foto_ampere"
    FOTO_SUHU = "foto_suhu"
    FOTO_TEKANAN_FREON_SEBELUM = "foto_tekanan_freon_sebelum"
    FOTO_TEKANAN_FREON_SESUDAH = "foto_tekanan_freon_sesudah"
    FOTO_TABUNG_FREON = "foto_tabung_freon"
    FOTO_INDIKASI_MASALAH = "foto_indikasi_masalah"

    BARCODE_INDOOR = "barcode_indoor"
    BARCODE_OUTDOOR = "barcode_outdoor"

    TIDAK_DIKENALI = "tidak_dikenali"


class MessageStatus(str, enum.Enum):
    NEW = "new"
    PROCESSED = "processed"
    COMPLETED = "completed"


class Message(Base):
    __tablename__ = "messages"

   
    id = Column(BIGINT, primary_key=True, autoincrement=True)

   
    work_order_id = Column(
        BIGINT(unsigned=True), 
        ForeignKey("work_orders.id"), 
        nullable=True,
        index=True 
    )

   
    group_id = Column(String(50), nullable=True)
    nama_pengirim = Column(String(100), nullable=True)
    nomor_pengirim = Column(String(20), nullable=False) 

    
    jenis_data = Column(
        Enum(
            MessageType,
            values_callable=lambda obj: [e.value for e in obj]
            ), nullable=False
        )
    text_content = Column(Text, nullable=True)
    media_url = Column(Text, nullable=True)
    mime_type = Column(String(50), nullable=True)

    
    latitude = Column(DECIMAL(10, 7), nullable=True)
    longitude = Column(DECIMAL(10, 7), nullable=True)

    
    status = Column(
        Enum(
            MessageStatus,
            values_callable=lambda obj: [e.value for e in obj]
            ), 
        default=MessageStatus.NEW, 
        server_default="new", 
        nullable=False
    )

   
    created_at = Column(
        TIMESTAMP, 
        server_default=func.now(), 
        default=func.now()         
    )

    
    work_order = relationship("WorkOrder", backref="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, pengirim={self.nama_pengirim}, type={self.jenis_data})>"