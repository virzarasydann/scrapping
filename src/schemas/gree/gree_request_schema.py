from pydantic import BaseModel
from datetime import datetime

class GreeRequestSchema(BaseModel):
    no_ticket: str
    serial_number_indoor: str
    serial_number_outdoor: str
    lokasi: str
    route_navigation: str
    status_gree: int
