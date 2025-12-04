from pydantic import BaseModel
from datetime import datetime

class GreeRequestSchema(BaseModel):
    no_ticket: str
    customer: str
    model: str
    keluhan: str
    tanggal: datetime
    before: str
    after: str
    serial_number: str
    lokasi: str
    status_gree: int
