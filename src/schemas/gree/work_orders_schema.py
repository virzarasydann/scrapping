from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import enum


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FS = "fs"
    GREE = "gree"

class WorkOrderCreate(BaseModel):
   
    work_order_number: Optional[str] = Field(None, max_length=50)
    
    
    spk_date: Optional[date] = None
    purchase_date: Optional[date] = None
    last_maintain_date: Optional[date] = None
    installation_date: Optional[date] = None
    
    
    asc_name: Optional[str] = Field(None, max_length=150)
    customer_name: Optional[str] = Field(None, max_length=150)
    phone_number: Optional[str] = Field(None, max_length=30)
    whatsapp_number: Optional[str] = Field(None, max_length=30)
    
    
    service_type: Optional[str] = Field(None, max_length=50)
    product_category: Optional[str] = Field(None, max_length=100)
    product_model: Optional[str] = Field(None, max_length=100)
    
    
    product_problem: Optional[str] = None 
    error_code: Optional[str] = Field(None, max_length=50)
    
    
    address: Optional[str] = None
    district_city_province: Optional[str] = Field(None, max_length=150)
    google_maps_url: Optional[str] = None
    
   
    status: Optional[WorkOrderStatus] = WorkOrderStatus.PENDING

    class Config:
        
        use_enum_values = True


class WorkOrderUpdate(WorkOrderCreate):
    pass 


class WorkOrderResponse(WorkOrderCreate):
    id: int
    created_at: Optional[object] = None 
    updated_at: Optional[object] = None

    class Config:
       
        from_attributes = True

