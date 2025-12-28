import enum
from sqlalchemy import Column, String, Date, Text, Enum, TIMESTAMP
from sqlalchemy.dialects.mysql import BIGINT 
from sqlalchemy.sql import func
from src.configuration.database import Base 


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FS = "fs"
    GREE = "gree"


class WorkOrder(Base):
    __tablename__ = "work_orders"

    
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

    
    work_order_number = Column(String(50), unique=True, nullable=True)

    
    spk_date = Column(Date, nullable=True)
    purchase_date = Column(Date, nullable=True)
    last_maintain_date = Column(Date, nullable=True)
    installation_date = Column(Date, nullable=True)

    
    asc_name = Column(String(150), nullable=True)
    customer_name = Column(String(150), nullable=True)
    phone_number = Column(String(30), nullable=True)
    whatsapp_number = Column(String(30), nullable=True)

    
    service_type = Column(String(50), nullable=True)
    product_category = Column(String(100), nullable=True)
    product_model = Column(String(100), nullable=True)
    product_problem = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)

    
    address = Column(Text, nullable=True)
    district_city_province = Column(String(150), nullable=True)
    google_maps_url = Column(Text, nullable=True)

   
    status = Column(
        Enum(
            WorkOrderStatus,
            values_callable=lambda obj: [e.value for e in obj]
        ), 
        default=WorkOrderStatus.PENDING, 
        server_default="pending",
        nullable=True
    )

  
    created_at = Column(TIMESTAMP, nullable=True, default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())

    def __repr__(self):
        return f"<WorkOrder(id={self.id}, wo_number={self.work_order_number}, spk_date={self.spk_date})>"