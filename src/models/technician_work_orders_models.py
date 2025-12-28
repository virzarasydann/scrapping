from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.configuration.database import Base



class TechnicianWorkOrder(Base):
    __tablename__ = "technician_work_order"

   
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

    
    work_order_id = Column(
        BIGINT(unsigned=True), 
        ForeignKey("work_orders.id", ondelete="CASCADE"), 
        nullable=False
    )

    
    technician_id = Column(
        BIGINT(unsigned=True), 
        ForeignKey("technicians.id", ondelete="CASCADE"), 
        nullable=False
    )

    
    created_at = Column(TIMESTAMP, nullable=True, default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())

    
    profile_technician = relationship("Technician", backref="work_order_assignments")

   
    work_order = relationship("WorkOrder", backref="technician_assignments")

    def __repr__(self):
        return f"<TechnicianWorkOrder(wo={self.work_order_id}, tech={self.technician_id})>"