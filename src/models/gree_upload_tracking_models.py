# src/models/gree_upload_tracking_models.py
from sqlalchemy import Column, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.configuration.database import Base

class GreeUploadTracking(Base):
    __tablename__ = "gree_upload_tracking"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    work_order_id = Column(
        BIGINT(unsigned=True), 
        ForeignKey("work_orders.id", ondelete="CASCADE"), 
        nullable=False
    )

    is_barcode_indoor_uploaded = Column(Boolean, default=False)
    is_barcode_outdoor_uploaded = Column(Boolean, default=False)
    is_foto_rumah_uploaded = Column(Boolean, default=False)
    is_share_lokasi_uploaded = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, nullable=True, default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())

    work_order = relationship("WorkOrder", backref="gree_tracking")