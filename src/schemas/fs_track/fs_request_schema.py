from pydantic import BaseModel
from datetime import datetime

class FsRequestSchema(BaseModel):
    no_ticket: str
    customer: str
    model: str
    keluhan: str
    tanggal: datetime
    before: str
    after: str
    serial_number: str
    lokasi: str
    status_fs: int
