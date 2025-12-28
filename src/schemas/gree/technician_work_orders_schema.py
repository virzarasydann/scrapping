from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import enum


class MessageType(str, enum.Enum):
    SHARE_LOKASI = "share_lokasi"
    PESAN = "pesan"
    FOTO_RUMAH_CUSTOMER = "foto_rumah_customer"

    BARCODE_INDOOR = "barcode_indoor"
    BARCODE_OUTDOOR = "barcode_outdoor"




class MessageResponse(BaseModel):
    work_orders_number: str
    barcode_indoor: Optional[str] = None
    barcode_outdoor: Optional[str] = None
    share_lokasi: Optional[str] = None
    foto_rumah_customer: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True



class TechnicianSimpleResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    level: Optional[str] = None

    class Config:
        from_attributes = True



class TechnicianWorkOrderResponse(BaseModel):
    assignment_id: int
    assigned_at: Optional[datetime] = None
    technician: TechnicianSimpleResponse
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True